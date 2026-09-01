import os
import re

ALLOWED_TOOLS = {
    "emails_list",
    "emails_get",
    "cdv_get_transaction",
}

RESTRICTED_TOOLS = {
    "cdv_detokenize",
}

FORBIDDEN_TOOLS = {
    "internal_get_all_transactions",
}


def authorize_tool(tool_name: str, human_approved: bool = False):
    if tool_name in ALLOWED_TOOLS:
        return {
            "allowed": True,
            "reason": "Tool allowed for Customer Operations."
        }

    if tool_name in RESTRICTED_TOOLS:
        if human_approved:
            return {
                "allowed": True,
                "reason": "Restricted tool approved by human reviewer."
            }

        return {
            "allowed": False,
            "reason": "Human approval required for detokenization."
        }

    if tool_name in FORBIDDEN_TOOLS:
        return {
            "allowed": False,
            "reason": "Tool not allowed for Customer Operations."
        }

    return {
        "allowed": False,
        "reason": "Tool not recognized by policy."
    }

## INPUT CONTROL ##

SUSPICIOUS_INPUT_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "internal investigation note",
    "cdv.detokenize",
    "cdv_detokenize",
    "get_all_transactions",
    "full pan",
]


def inspect_input(content: str):
    content_lower = content.lower()

    detected_patterns = [
        pattern
        for pattern in SUSPICIOUS_INPUT_PATTERNS
        if pattern in content_lower
    ]

    if detected_patterns:
        return {
            "suspicious": True,
            "reason": "Possible prompt injection detected.",
            "patterns": detected_patterns
        }

    return {
        "suspicious": False,
        "reason": "No suspicious input patterns detected.",
        "patterns": []
    }

## OUTPUT CONTROL ##
def inspect_output(content: str):
    if not content:
        return {
            "safe": True,
            "reason": "Empty output."
        }

    pan_pattern = r"\b(?:\d[ -]*?){13,19}\b"

    if re.search(pan_pattern, content):
        return {
            "safe": False,
            "reason": "Possible full PAN detected in output."
        }

    secrets = [
        os.getenv("CDV_API_KEY"),
        os.getenv("SIGNING_KEY"),
    ]

    for secret in secrets:
        if secret and secret in content:
            return {
                "safe": False,
                "reason": "Application secret detected in output."
            }

    return {
        "safe": True,
        "reason": "No sensitive data detected in output."
    }

## EXTRACT CONTEXT ##

def extract_dispute_context(content: str):
    txn_match = re.search(
        r"\bTXN-\d+\b",
        content,
        re.IGNORECASE
    )

    transaction_id = (
        txn_match.group(0).upper()
        if txn_match
        else None
    )

    content_lower = content.lower()

    if (
        "do not recognize" in content_lower
        or "don't recognize" in content_lower
        or "don't remember" in content_lower
    ):
        issue = "unrecognized transaction"
    else:
        issue = "general dispute"

    return {
        "transaction_id": transaction_id,
        "issue": issue
    }

## VALIDADE CONTEXT ##

def validate_transaction_context(
    tool_name: str,
    arguments: dict,
    dispute_context: dict
):
    transaction_tools = {
        "cdv_get_transaction",
        "cdv_detokenize",
    }

    if tool_name not in transaction_tools:
        return {
            "allowed": True,
            "reason": "No transaction context validation required."
        }

    requested_txn = arguments.get("txn_id")
    expected_txn = dispute_context.get("transaction_id")

    if requested_txn != expected_txn:
        return {
            "allowed": False,
            "reason": "Transaction outside dispute context."
        }

    return {
        "allowed": True,
        "reason": "Transaction matches dispute context."
    }
