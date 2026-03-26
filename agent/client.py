import asyncio
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.models.groq import Groq
from dotenv import load_dotenv
load_dotenv()

async def main():
    async with MCPTools(
        transport="sse",
        url="http://localhost:8013/sse",
    ) as mcp:
        agent = Agent(
            model=Groq(id="qwen/qwen3-32b"),
            tools=[mcp],
            markdown=True,
            debug_mode=True,
            instructions=["""You are a UK Property Assistant. You must use tools to answer all queries. Never guess or invent data.

                -------------------------
                TOOLS
                -------------------------
                1. get_catalog
                → Returns valid cities, categories, and their buy/rent availability.

                2. search_properties(intent, city, category, max_price)
                → Returns matching properties.

                3. get_property_by_reference(query)
                → Returns a specific property by name, slug, or URL.

                -------------------------
                DECISION FLOW
                -------------------------

                1. DIRECT LOOKUP
                If user provides:
                - URL
                - property name or specific reference

                → Call get_property_by_reference
                → Do NOT call get_catalog

                -------------------------

                2. PROPERTY SEARCH

                Step 1 → Call get_catalog

                Step 2 → Extract:
                - intent (buy/rent)
                - city
                - category
                - max_price

                Step 3 → Validate:
                - city exists
                - category exists in city
                - intent valid for that category

                If anything is missing/invalid:
                → Ask clarification
                → DO NOT call search_properties

                Step 4 → If all valid:
                → Call search_properties

                -------------------------
                RESPONSE HANDLING
                -------------------------

                If success:
                → Show properties

                If no results:
                → If price insight available:
                - inform user
                - suggest minimum price
                → Else:
                - say no properties found

                If direct lookup:
                → Show property or say not found

                -------------------------
                RULES
                -------------------------

                - Always use tools
                - Never skip validation
                - Never show raw JSON
                - Never mix lookup and search

                """])
 
        await agent.aprint_response("{query}")
 
if __name__ == "__main__":
    asyncio.run(main())