
# LunarCrush.ai and MCP API Documentation

**Base URL:** `https://lunarcrush.ai`

---

## Overview

**LunarCrush.ai** is a token-efficient, LLM-friendly service that delivers LunarCrush social data optimized for AI-enabled applications and agents.  
It provides real-time social context retrieval and server-sent event (SSE) streaming for autonomous AI tools and MCP connectors.

**Requirements:**
- An [active subscription](https://lunarcrush.com/pricing)
- An [API key](https://lunarcrush.com/developers/api/authentication)

---

## MCP Connector

### 🛰️ Server-Sent Events (SSE) / Streamable HTTP

**Purpose:**  
SSE enables real-time, one-way streaming of social data updates from LunarCrush.ai to your AI application or agent over a persistent HTTP connection.

**Endpoint:**  
```bash
https://lunarcrush.ai/sse
```

**Headers Example:**  
```json
{
  "Authorization": "Bearer YOUR_API_KEY"
}
```

**Config Example (MCP style):**
```json
{
  "mcpServers": {
    "LunarCrush": {
      "type": "sse",
      "url": "https://lunarcrush.ai/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**Protocol:** `HTTPS`  
**Stream Type:** `text/event-stream`  
**Method:** `GET`  
**Behavior:** Continuous, auto-reconnecting stream delivering incremental updates for topics, creators, or metrics.

**Example JavaScript Client:**
```js
import EventSource from 'eventsource';

const stream = new EventSource('https://lunarcrush.ai/sse?key=YOUR_API_KEY');

stream.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New Event:', data);
};

stream.onerror = (err) => {
  console.error('Stream error:', err);
};
```

**Sample Event Payload:**
```json
{
  "type": "topic_update",
  "topic": "bitcoin",
  "timestamp": "2025-11-07T10:45:00Z",
  "metrics": {
    "alt_rank": 12,
    "galaxy_score": 74,
    "interactions": 21043,
    "sentiment": 0.63
  }
}
```

---

## MCP Server Tools

### 1. List

**Endpoint:** `GET lunarcrush.ai/list/{category}`  
Get a list of social topics within a category sorted and filtered by metrics.

Example: [lunarcrush.ai/list](https://lunarcrush.ai/list?key=YOUR_API_KEY)

---

### 2. Cryptocurrencies

**Endpoint:** `GET lunarcrush.ai/list/cryptocurrencies/{sector}/{sort}/{limit}`  
Lists cryptocurrencies by chosen metrics and sector.

Example: [lunarcrush.ai/list/cryptocurrencies/100](https://lunarcrush.ai/list/cryptocurrencies/100?key=YOUR_API_KEY)

---

### 3. Stocks

**Endpoint:** `GET lunarcrush.ai/list/stocks/{sector}/{sort}/{limit}`  
Lists stocks by available metrics and sector.

Example: [lunarcrush.ai/list/stocks/100](https://lunarcrush.ai/list/stocks/100?key=YOUR_API_KEY)

---

### 4. Topic

**Endpoint:** `GET lunarcrush.ai/topic/{topic}`  
Fetch details for a topic, cryptocurrency, or stock.

Example: [lunarcrush.ai/topic](https://lunarcrush.ai/topic/?key=YOUR_API_KEY)

---

### 5. Topic Time Series

**Endpoint:** `GET lunarcrush.ai/topic/{topic}/time-series/{interval}/{metrics}`  
Retrieve historical time series for a topic or asset.

---

### 6. Topic Posts

**Endpoint:** `GET lunarcrush.ai/topic/{topic}/posts/{interval}/{from_date}/{to_date}`  
Returns the most popular social and news posts mentioning a topic.

---

### 7. Creator

**Endpoint:** `GET lunarcrush.ai/creator/{network}/{screenName}`  
Fetch metrics and insights for a specific creator.

---

### 8. Post

**Endpoint:** `GET lunarcrush.ai/post/{network}/{id}`  
Fetch a specific post by network and ID.

---

### 9. Search

**Endpoint:** `GET lunarcrush.ai/search/{query}`  
Search across topics, creators, and posts with contextual expansion.

---

### 10. Fetch

**Endpoint:** `GET lunarcrush.ai/fetch/{path}`  
Retrieve content for any defined path (e.g. `/topic/bitcoin/posts/1m`).

---

### 11. Authentication

**Endpoint:** `GET lunarcrush.ai/auth/{apiKey}`  
Check subscription or verify API key status.

---

© 2025 LunarCrush Inc.
