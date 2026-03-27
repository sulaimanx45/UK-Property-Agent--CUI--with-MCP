# UK Property AI Agent (MCP + LLM)

An intelligent **AI-powered property assistant** that interacts with real-world UK property listings using an **MCP (Model Context Protocol) server** and a **tool-using LLM agent**.

This project demonstrates how to build a **production-style agentic system** that:

* Uses structured tools instead of hallucinating
* Validates user inputs before execution
* Integrates with live APIs
* Follows strict reasoning workflows

---

## Features

✅ MCP-powered tool system
✅ Real UK property data integration
✅ Smart validation before search
✅ Price insight when no results found
✅ Direct property lookup via URL/name
✅ Zero hallucination (tool-only responses)
✅ Clean agent decision flow

---

## Architecture

```
User Query
   ↓
LLM Agent (Groq - LLaMA 3.3)
   ↓
Decision Logic (Instructions)
   ↓
MCP Tools Layer (FastMCP Server)
   ↓
External API (Property Listings)
```

---

## Tech Stack

* **LLM**: Groq (LLaMA 3.3 70B)
* **Agent Framework**: Agno
* **MCP Server**: FastMCP
* **Backend**: Python
* **API Source**: Cuishoreditch Property Listings

---

## Project Structure

```
uk-property-agent/
│── agent/
│   └── client.py
│
│── mcp_server/
│   └── server.py
│
│── requirements.txt
│── .env.example
│── README.md
```

---

## Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/your-username/uk-property-agent.git
cd uk-property-agent
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## Running the Project

### Step 1: Start MCP Server

```bash
python mcp_server/server.py
```

Server runs at:

```
http://localhost:8013/sse
```

---

### Step 2: Run Agent

```bash
python agent/client.py
```

---

## How the Agent Works

The agent follows a strict reasoning pipeline:

### 1. Direct Lookup

If user provides:

* Property URL
* Property name

→ Calls: `search_by_query`

---

### 2. Property Search Flow

1. Calls `get_catalog`
2. Extracts:

   * intent (buy/rent)
   * city
   * category
   * max_price
3. Validates inputs
4. Calls `search_properties`

---

### 3. Smart Response Handling

* ✅ Results → Show properties
* ❌ No results → Suggest minimum price
* 🔍 Direct lookup → Show property

---

## Available MCP Tools

### 1. `get_catalog`

* Returns valid cities and categories
* Used for validation

---

### 2. `search_properties(intent, city, category, max_price)`

* Returns matching properties
* Includes price insights if no results

---

### 3. `search_by_query(query)`

* Finds properties by:

  * Name
  * URL

---

## Example Queries

```
Find me a 2-bedroom apartment in London under 500000
```

```
Show me properties for rent in Manchester under 2000
```

```
https://cuishoreditch.com/property/example-property
```

---

## Design Principles

* ❌ No hallucinated data
* ✅ Tool-first architecture
* ✅ Strict validation before execution
* ✅ Separation of concerns (Agent vs MCP)

---


---

## Contribute

Feel free to fork, improve, and submit PRs!
