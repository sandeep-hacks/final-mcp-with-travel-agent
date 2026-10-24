import os
import sys
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },

        "aviationstack": {
            "transport": "stdio",
            "command": str(BASE_DIR / "aviationstack-mcp" / ".venv" / "bin" / "python"),
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
            }
        },

        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(BASE_DIR / "custom_weather_mcp.py")
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)


# tools discovery
# async def main():

#     tools = await client.get_tools()

#     print("\nAvailable MCP Tools:\n")

#     for tool in tools:
#         print(tool.name)


# async def main():
#     tools = await client.get_tools()

#     search_tool = next(
#         tool
#         for tool in tools
#         if tool.name == "tavily_search"
#     )

#     result = await search_tool.ainvoke(
#         {
#             "query": "Best hotels in Delhi"
#         }
#     )

#     print(result)

# asyncio.run(main()) 


# search_tool = None

# async def initialize_mcp():
#     global search_tool
#     if search_tool is not None:
#         return

#     tools = await client.get_tools()
#     print("\nAvailable MCP Tools:")

#     for tool in tools:
#         print(tool.name)

#     search_tool = next(
#         tool
#         for tool in tools
#         if tool.name == "tavily_search"
#     )



search_tool = None
aviation_tools = {}

async def initialize_mcp():

    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }





async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke(
        {
            "query": query
        }
    )
    return result




async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result



async def get_airports():

    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result


async def get_airlines():

    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool:
        return "Airline tool unavailable"

    result = await tool.ainvoke({})

    return result





weather_tool = None
forecast_tool = None


async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )


async def weather_mcp_search(city: str):

    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )


async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )




from langchain_groq import ChatGroq
from groq import Groq

def get_best_model():
    preferred = [
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3.8-27b",
        "gemma2-9b-it"
    ]
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "llama-3.3-70b-versatile"
    try:
        client = Groq(api_key=api_key)
        all_models = [m.id for m in client.models.list().data]
        
        # Filter to only general-purpose text LLMs (excluding speech, safety, vision)
        available = [
            m_id for m_id in all_models
            if not any(x in m_id.lower() for x in ["whisper", "orpheus", "guard", "audio", "speech", "vision", "moderation"])
        ]
        
        for model in preferred:
            if model in available:
                return model
        if available:
            return available[0]
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

# LLM
llm = ChatGroq(
    model=get_best_model(),
    api_key=os.getenv("GROQ_API_KEY")
)

###################################
# Destination Extractor
###################################

def extract_destination(query: str):
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
    groq_key = os.getenv("GROQ_API_KEY")

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    try:
        active_llm = ChatGroq(
            model=get_best_model(),
            api_key=groq_key
        )
        response = active_llm.invoke(prompt)
        dest = response.content.strip().split("\n")[0].strip()
        if dest:
            return dest
    except Exception as e:
        print(f"Warning: extract_destination LLM fallback ({e})")

    # Safe regex fallback if LLM is unavailable
    import re
    match = re.search(r'\b(?:to|in|visit|explore|trip)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', query, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Tokyo"


async def main():
    await initialize_mcp()
    print("MCP initialization successful.")

if __name__ == "__main__":
    asyncio.run(main())