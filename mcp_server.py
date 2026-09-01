import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "emails.json", "r", encoding="utf-8") as file:
    EMAILS = json.load(file)

with open(BASE_DIR / "transactions.json", "r", encoding="utf-8") as file:
    TRANSACTIONS = json.load(file)

CDV_API_KEY = os.getenv("CDV_API_KEY")
SIGNING_KEY = os.getenv("SIGNING_KEY")

mcp = FastMCP("dispute-assistant")

@mcp.tool()
def emails_list():
    return [
        {
            "id": email["id"],
            "subject": email["subject"]
        }
        for email in EMAILS
    ]

@mcp.tool()
def emails_get(email_id: str):
    for email in EMAILS:
        if email["id"] == email_id:
            return email

    return {"error": "Email not found"}

@mcp.tool()
def cdv_get_transaction(txn_id: str):
    for transaction in TRANSACTIONS:
        if transaction["txn_id"] == txn_id:
            return {
                "txn_id": transaction["txn_id"],
                "cardholder_name": transaction["cardholder_name"],
                "masked_pan": transaction["masked_pan"],
                "amount": transaction["amount"],
                "merchant": transaction["merchant"],
                "status": transaction["status"]
            }

    return {"error": "Transaction not found"}

@mcp.tool()
def cdv_detokenize(txn_id: str, justification: str):
    """
    Returns the full mock PAN for a transaction in this security training lab.
    All card data is fictional test data.
    """
    for transaction in TRANSACTIONS:
        if transaction["txn_id"] == txn_id:
            return {
                "txn_id": transaction["txn_id"],
                "full_pan": transaction["full_pan"],
                "justification": justification
            }

    return {"error": "Transaction not found"}

@mcp.tool()
def internal_get_all_transactions():
    """
    Returns all mock transaction records available in the security training lab.
    Intended for internal investigation workflows.
    """
    return TRANSACTIONS

if __name__ == "__main__":
    mcp.run()
