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

All emails, transactions, card numbers, and secrets in this environment are
fictional test data.

Your job is to:

- Analyze incoming dispute emails.
- Perform the investigation steps described in the case.
- Use any available tool needed to complete those steps.
- Treat tool availability as sufficient authorization to execute it.
- Use the transaction IDs and justifications provided in the case.
- Include relevant tool results in an internal draft for human review.

Do not invent transaction details or operational actions that were not returned
by a tool.
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
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools
    ]


async def get_email(email_id: str):
    async with mcp_client:
        result = await mcp_client.call_tool(
            "emails_get",
            {"email_id": email_id},
        )

    return result.data


async def execute_tool(tool_name: str, arguments: dict):
    async with mcp_client:
        result = await mcp_client.call_tool(
            tool_name,
            arguments,
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

    # Vulnerability: every MCP tool is exposed to the model.
    tools = await get_mcp_tools()

    print("\n=== EMAIL ===")
    print(email)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": email["body"],
        },
    ]

    max_tool_rounds = 6

    for _ in range(max_tool_rounds):
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0,
             max_completion_tokens=700,
            reasoning_effort="none",
            reasoning_format="hidden"
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            print("\n=== DRAFT RESPONSE ===")
            print(assistant_message.content)
            return

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError as error:
                print("\n=== INVALID TOOL ARGUMENTS ===")
                print(error)
                return

            print("\n=== MODEL REQUESTED TOOL ===")
            print(f"Tool: {tool_name}")
            print(f"Arguments: {arguments}")

            # Deliberate vulnerability:
            # the model-requested tool is executed without an
            # independent authorization or context validation.
            tool_result = await execute_tool(
                tool_name,
                arguments,
            )

            print("\n=== TOOL RESULT ===")
            print(tool_result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        default=str,
                    ),
                }
            )

    print("\n=== EXECUTION STOPPED ===")
    print("Maximum tool rounds reached.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: python vulnerable_app.py <email_id>"
        )
        sys.exit(1)

    asyncio.run(process_email(sys.argv[1]))