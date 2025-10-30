# extend_mcp_timeout.py
import anyio
import inspect
import sys


def _find_session_class():
    """Locate the Session-like class that has send_request()."""
    for mod_name in ("mcp.client.session", "mcp.shared.session"):
        mod = sys.modules.get(mod_name)
        if not mod:
            try:
                __import__(mod_name)
                mod = sys.modules[mod_name]
            except ImportError:
                continue
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if hasattr(obj, "send_request") and inspect.iscoroutinefunction(obj.send_request):
                return obj
    return None


def extend_mcp_timeout(seconds: float = 60):
    """Patch *all* known MCP timeout layers (session, util, streamable_http)."""

    # ---- 1️⃣  BaseSession.send_request ----
    Session = _find_session_class()
    if Session is None:
        raise RuntimeError("Could not find a Session-like class with send_request()")

    original_send = Session.send_request

    async def patched_send_request(self, *args, **kwargs):
        with anyio.fail_after(seconds):
            return await original_send(self, *args, **kwargs)

    Session.send_request = patched_send_request
    print(f"[MCP] Patched {Session.__module__}.{Session.__name__}.send_request → {seconds}s")

    # ---- 2️⃣  MCPUtil.invoke_mcp_tool ----
    try:
        import agents.mcp.util as mcp_util
        MCPUtil = getattr(mcp_util, "MCPUtil", None)

        if MCPUtil and hasattr(MCPUtil, "invoke_mcp_tool"):
            orig_method = MCPUtil.invoke_mcp_tool

            async def patched_invoke_mcp_tool(cls, *args, **kwargs):
                with anyio.fail_after(seconds):
                    return await orig_method.__func__(cls, *args, **kwargs)

            MCPUtil.invoke_mcp_tool = classmethod(patched_invoke_mcp_tool)
            print(f"[MCP] Patched MCPUtil.invoke_mcp_tool outer timeout → {seconds}s")

        elif hasattr(mcp_util, "invoke_mcp_tool"):
            orig_func = mcp_util.invoke_mcp_tool

            async def patched_invoke_mcp_tool(*args, **kwargs):
                with anyio.fail_after(seconds):
                    return await orig_func(*args, **kwargs)

            mcp_util.invoke_mcp_tool = patched_invoke_mcp_tool
            print(f"[MCP] Patched agents.mcp.util.invoke_mcp_tool outer timeout → {seconds}s")
        else:
            print("[MCP] Warning: could not find invoke_mcp_tool in agents.mcp.util")
    except Exception as e:
        print(f"[MCP] Warning: patch of outer timeout failed: {e}")

    # ---- 3️⃣  mcp.client.streamable_http internal timeout ----
    try:
        import mcp.client.streamable_http as streamable_http
        from contextlib import asynccontextmanager

        if hasattr(streamable_http, "streamablehttp_client"):
            original_stream = streamable_http.streamablehttp_client

            @asynccontextmanager
            async def patched_streamablehttp_client(*args, **kwargs):
                # outer anyio timeout uses captured `seconds`
                with anyio.fail_after(seconds):
                    async for value in original_stream(*args, **kwargs):
                        yield value

            streamable_http.streamablehttp_client = patched_streamablehttp_client
            print(f"[MCP] Patched mcp.client.streamable_http.streamablehttp_client → {seconds}s")
        else:
            print("[MCP] Warning: streamablehttp_client not found")
    except Exception as e:
        print(f"[MCP] Warning: could not patch streamable_http timeout: {e}")
