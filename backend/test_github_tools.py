import asyncio

from agents.git_agent import create_github_mcp_client


async def main():

    client = create_github_mcp_client()

    tools = await client.get_tools()

    for tool in tools:

        if tool.name == "get_file_contents":

            print("=" * 60)
            print("🔎 get_file_contents")
            print("=" * 60)

            print("NAME:")
            print(tool.name)

            print("\nDESCRIPTION:")
            print(tool.description)

            print("\nARGS SCHEMA:")
            print(tool.args)

            print("=" * 60)

            return

    print("❌ get_file_contents introuvable.")


asyncio.run(main())