import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
#load_dotenv()
load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = MultiServerMCPClient(
    {
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

async def main():

    print("Loading tools...")

    tools = await client.get_tools()

    print("Tools loaded!")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())