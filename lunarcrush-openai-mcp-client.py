import os
import asyncio
import json
import contextlib
import time

from agents import Agent, Runner, enable_verbose_stdout_logging, set_default_openai_key
from agents.mcp.server import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from extend_mcp_timeout import extend_mcp_timeout
from dotenv import load_dotenv

enable_verbose_stdout_logging()

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
RETRIES = 3
RETRY_DELAY = 2  # seconds

# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------
async def run_lunarcrush_agent():

    # Load environment variables from .env.local/.env (if present).
    for candidate in (".env.local", ".env"):
        load_dotenv(candidate, override=False)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found. Set it in the environment or .env file.")

    # Configure the Agents SDK to use the discovered key.
    set_default_openai_key(api_key)

    # 1️⃣  Build and connect MCP server
    lunarcrush_server = MCPServerStreamableHttp(
        params=MCPServerStreamableHttpParams(
            url=os.getenv("MCP_SERVER_URL"),
            request_timeout=60,          # outer HTTP timeout
            streamable_http_timeout=90,  # keep-alive window
            terminate_on_close=True,
        )
    )
    await lunarcrush_server.connect()

    # 2️⃣  Patch internal 5 s MCP RPC timeout → 60 s
    extend_mcp_timeout(60)

    # 3️⃣  Create agent
    agent = Agent(
        name="LunarcrushAgent",
        model="gpt-4o-mini",
        instructions=(
            "You are an expert cryptocurrency analyst. You will use the LunarCrush MCP to fetch the latest social sentiments."
            "You will include sentiment, galaxy_score, and alt_rank values in your report."
        ),
        mcp_servers=[lunarcrush_server],
    )

    # 4️⃣  Run
    start = time.perf_counter()
    result = await Runner.run(
        starting_agent=agent,
        input=os.getenv("LLM_PROMPT", "Fetch the latest social sentiments on bitcoin")
    )
    elapsed = time.perf_counter() - start

    # 5️⃣  Display results
    print("\n=== LLM SUMMARY ===")
    print(result.final_output)

    print("\n=== PARSED METRICS ===")
    containers = (
        getattr(result, "events", None)
        or getattr(result, "steps", None)
        or getattr(result, "tool_outputs", None)
        or []
    )

    for c in containers:
        text = getattr(c, "output_text", None) or getattr(c, "message", None) or str(c)
        if not text:
            continue
        try:
            data = json.loads(text)
            topic = data.get("data", [])[0] if isinstance(data.get("data"), list) else data
            sentiment = topic.get("sentiment")
            galaxy = topic.get("galaxy_score")
            alt_rank = topic.get("alt_rank")
            print(f"Sentiment: {sentiment}, Galaxy Score: {galaxy}, AltRank: {alt_rank}")
        except Exception:
            pass

    print(f"\nQuery time: {elapsed:.2f} s")

    # 6️⃣  Graceful cleanup
    with contextlib.suppress(asyncio.CancelledError, RuntimeError):
        await lunarcrush_server.cleanup()
    await asyncio.sleep(0.5)

# ---------------------------------------------------------------------
# Main with retry logic
# ---------------------------------------------------------------------
async def main():
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"\n--- Attempt {attempt}/{RETRIES} ---")
            await run_lunarcrush_agent()
            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < RETRIES:
                print(f"Retrying in {RETRY_DELAY}s...\n")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("All retries failed.")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
