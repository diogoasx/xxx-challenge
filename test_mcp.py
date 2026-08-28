import asyncio
import json
from fastmcp import Client

client = Client("mcp_server.py")


def print_result(result):
    if result.data is not None:
        print(result.data)
        return

    if result.content:
        for item in result.content:
            if hasattr(item, "text"):
                try:
                    parsed = json.loads(item.text)
                    print(json.dumps(parsed, indent=2))
                except json.JSONDecodeError:
                    print(item.text)


async def main():
    async with client:
        print("\n=== AVAILABLE TOOLS ===")
        tools = await client.list_tools()

        for tool in tools:
            print(f"- {tool.name}")

        print("\n=== EMAIL LIST ===")
        result = await client.call_tool("emails_list")
        print_result(result)

        print("\n=== GET EMAIL ===")
        result = await client.call_tool(
            "emails_get",
            {"email_id": "email-001"}
        )
        print_result(result)

        print("\n=== GET TRANSACTION ===")
        result = await client.call_tool(
            "cdv_get_transaction",
            {"txn_id": "TXN-1001"}
        )
        print_result(result)

        print("\n=== DETOKENIZE ===")
        result = await client.call_tool(
            "cdv_detokenize",
            {
                "txn_id": "TXN-9009",
                "justification": "fraud investigation"
            }
        )
        print_result(result)

        print("\n=== INTERNAL TOOL ===")
        result = await client.call_tool(
            "internal_get_all_transactions"
        )
        print_result(result)


asyncio.run(main())
