import json
import os
import re
from dataclasses import dataclass
from typing import Any
import requests

from .tools import TOOLS

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

@dataclass
class AgentResult:
    tool: str
    tool_result: Any
    response: str

SYSTEM_PROMPT = '''
You are an AI business agent.

Understand the user's request in Arabic or English and choose exactly one tool.

Allowed tools:

1. search_invoices
Use when the user wants to show, list, find, inspect, filter, or view invoices.
Arguments:
- status: optional
- customer: optional
- invoice_id: optional

Examples:
Show me all invoices
{"tool":"search_invoices","arguments":{}}

اعرض كل الفواتير
{"tool":"search_invoices","arguments":{}}

Show overdue invoices
{"tool":"search_invoices","arguments":{"status":"overdue"}}

اعرض الفواتير المتأخرة
{"tool":"search_invoices","arguments":{"status":"overdue"}}

Look up invoice INV-1001
{"tool":"search_invoices","arguments":{"invoice_id":"INV-1001"}}

2. summarize_invoices
Use when the user asks for totals, sums, counts, or numerical summaries.
Arguments:
- status: optional
- customer: optional

Example:
What is the total of overdue invoices?
{"tool":"summarize_invoices","arguments":{"status":"overdue"}}

كم مجموع الفواتير المتأخرة؟
{"tool":"summarize_invoices","arguments":{"status":"overdue"}}

Rules:
- Return ONLY valid JSON.
- Never invent tool names.
- Do not use markdown.
'''

def _clean_json(content: str) -> dict:
    content = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE)
    content = content.replace("```", "").strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("LLM did not return valid JSON")

    return json.loads(content[start:end + 1])

def ask_ollama(message: str) -> dict:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "options": {"temperature": 0},
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=90)
    response.raise_for_status()

    return _clean_json(response.json()["message"]["content"])

def fallback_decision(message: str) -> dict:
    text = message.lower()
    invoice_match = re.search(r"inv-\d+", text, re.IGNORECASE)

    if invoice_match:
        return {
            "tool": "search_invoices",
            "arguments": {"invoice_id": invoice_match.group(0).upper()},
        }

    is_overdue = any(x in text for x in ["overdue", "متأخر", "المتأخرة", "متأخرة"])
    asks_total = any(x in text for x in ["total", "sum", "count", "مجموع", "اجمالي", "إجمالي", "كم"])

    if asks_total:
        args = {}
        if is_overdue:
            args["status"] = "overdue"
        return {"tool": "summarize_invoices", "arguments": args}

    args = {}
    if is_overdue:
        args["status"] = "overdue"

    return {"tool": "search_invoices", "arguments": args}

def choose_tool(message: str) -> dict:
    try:
        decision = ask_ollama(message)
        tool_name = decision.get("tool")
        arguments = decision.get("arguments") or {}

        if tool_name not in TOOLS:
            return fallback_decision(message)

        return {"tool": tool_name, "arguments": arguments}
    except Exception:
        return fallback_decision(message)

def build_response(tool_name: str, result: dict) -> str:
    if tool_name == "search_invoices":
        if result["count"] == 0:
            return "No matching invoices were found."

        if result["count"] == 1:
            i = result["invoices"][0]
            return f"{i['id']} — {i['customer']} — {i['amount']:.2f} — {i['status']}."

        return f"Found {result['count']} invoice(s)."

    if tool_name == "summarize_invoices":
        return f"Found {result['count']} invoice(s) with a total value of {result['total_amount']:.2f}."

    return "Request completed."

def run_agent(message: str) -> AgentResult:
    decision = choose_tool(message)
    tool_name = decision["tool"]
    arguments = decision.get("arguments", {})

    tool_result = TOOLS[tool_name](**arguments)
    response = build_response(tool_name, tool_result)

    return AgentResult(tool=tool_name, tool_result=tool_result, response=response)
