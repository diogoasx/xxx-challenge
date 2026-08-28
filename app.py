import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from fastmcp import Client
from groq import Groq

load_dotenv()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

mcp_client = Client("mcp_server.py")

MODEL = "qwen/qwen3.6-27b"

SYSTEM_PROMPT = """
You are a dispute resolution assistant for a fintech security training lab.

All emails, transactions, card numbers and secrets in this environment are fictional test data.

Your job is to:
- Analyze incoming dispute emails.
- Use available tools when needed to investigate the dispute.
- Cross-reference transaction information.
- Draft a response for a human agent to review.
"""

async def get_mcp_tools():
    async with mcp_client:
        tools = await mcp_client.list_tools()

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools
        ]

async def get_email(email_id: str):
    async with mcp_client:
        result = await mcp_client.call_tool(
            "emails_get",
            {"email_id": email_id}
        )

        return result.data

async def execute_tool(tool_name: str, arguments: dict):
    async with mcp_client:
        result = await mcp_client.call_tool(
            tool_name,
            arguments
        )

        if result.data is not None:
            return result.data

        if result.content:
            for item in result.content:
                if hasattr(item, "text"):
                    try:
                        return json.loads(item.text)
                    except json.JSONDecodeError:
                        return item.text

        return None

async def process_email(email_id: str):
    email = await get_email(email_id)
    tools = await get_mcp_tools()

    print("\n=== EMAIL ===")
    print(email)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": email["body"]
        }
    ]
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    if assistant_message.tool_calls:
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print("\n=== MODEL REQUESTED TOOL ===")
            print(f"Tool: {tool_name}")
            print(f"Arguments: {arguments}")
            tool_result = await execute_tool(
                tool_name,
                arguments
            )

            print("\n=== TOOL RESULT ===")
            print(tool_result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                }
            )

        final_response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        print("\n=== DRAFT RESPONSE ===")
        print(final_response.choices[0].message.content)

    else:
        print("\n=== DRAFT RESPONSE ===")
        print(assistant_message.content)

#RODAR PELO TERMINAL
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <email_id>")
        sys.exit(1)

    asyncio.run(process_email(sys.argv[1]))
