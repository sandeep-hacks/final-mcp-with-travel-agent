import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient(
    {
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
        }
    }
)


import asyncio

async def main():

    tools = await client.get_tools()

    print("\nAvailable Tools:\n")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())