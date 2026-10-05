"""
MCP CLIENT HELPER
------------------
Lets agent nodes call MCP tools without repeating connection boilerplate.
"""
import os
import asyncio
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

async def _call_tool_async(tool_name:str,arguments:dict)->str:
    env =os.environ.copy()
    env['PYTHONPATH']=PROJECT_ROOT
    params =StdioServerParameters(
        command="python",args=['-m','app.mcp_server'], cwd=PROJECT_ROOT, env=env

    )
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()

            result = await session.call_tool(tool_name, arguments)
            # Some tools (like list_expenses) return MULTIPLE content blocks,
            # one per item. Join them all instead of taking only the first.
            texts = [block.text for block in result.content if hasattr(block, "text")]
            return "\n".join(texts)

def call_mcp_tool(tool_name:str,arguments:dict)->str:
    return asyncio.run(_call_tool_async(tool_name,arguments))
