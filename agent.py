import json
import re
import urllib.error
import urllib.request
from typing import Any

from tools import (
    calculate_total,
    correlation,
    dataset_summary,
    group_mean,
    group_sum,
    inspect_dataset,
    missing_values,
    monthly_sales,
    numeric_statistics,
    time_series,
    top_products,
    yearly_sales,
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"


def call_llm(system_prompt: str, user_prompt: str, timeout: int = 180) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["message"]["content"]
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama is not reachable. Start Ollama and make sure qwen2.5:3b is installed."
        ) from exc


def extract_json(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "")
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def detect_columns(df):
    columns = list(df.columns)
    lower = {str(c).lower(): c for c in columns}

    def find(names):
        for name in names:
            if name.lower() in lower:
                return lower[name.lower()]
        for c in columns:
            lc = str(c).lower()
            if any(name.lower() in lc for name in names):
                return c
        return None

    numeric = list(df.select_dtypes(include="number").columns)
    return {
        "value": find(["Sales", "Revenue", "Amount", "Value", "Price"]) or (numeric[0] if numeric else None),
        "date": find(["Order Date", "Date", "Transaction Date", "Invoice Date"]),
        "product": find(["Product Name", "Product", "Item"]),
        "category": find(["Category"]),
        "sub_category": find(["Sub-Category", "Sub Category"]),
        "region": find(["Region"]),
        "state": find(["State"]),
        "city": find(["City"]),
        "segment": find(["Segment"]),
    }


def create_plan(task: str, schema: dict, hints: dict) -> list[str]:
    system = """You are the planning component of a data-analysis agent. Return ONLY JSON with a 'plan' array containing 3-5 concise executable steps. Do not calculate results and do not invent columns. The actual calculations will be performed by Python tools."""
    prompt = json.dumps({"task": task, "columns": schema["columns"], "detected_columns": hints}, default=str)
    result = extract_json(call_llm(system, prompt))
    plan = result.get("plan", [])
    return plan[:5] if isinstance(plan, list) else []


def choose_actions(task: str, df, hints: dict):
    text = task.lower()
    value = hints.get("value")
    date = hints.get("date")
    actions = []

    # Explicit intent routing is deterministic so the LLM cannot invent a tool/result.
    if any(k in text for k in ["missing", "null", "blank", "incomplete"]):
        actions.append(("missing_values", {}))

    if any(k in text for k in ["correlation", "correlations", "relationship between"]):
        actions.append(("correlation", {}))

    if any(k in text for k in ["statistics", "descriptive statistics", "describe"]):
        actions.append(("numeric_statistics", {}))

    if any(k in text for k in ["top product", "top products", "best product", "best products", "products by", "bottom product", "bottom products", "lowest product", "lowest products"]):
        if hints.get("product") and value:
            ascending = any(k in text for k in ["bottom", "lowest", "worst", "least"])
            actions.append(("top_products", {"product_column": hints["product"], "value_column": value, "limit": 10, "ascending": ascending}))

    dimension_map = [
        ("region", hints.get("region")),
        ("category", hints.get("category")),
        ("sub-category", hints.get("sub_category")),
        ("subcategory", hints.get("sub_category")),
        ("state", hints.get("state")),
        ("city", hints.get("city")),
        ("segment", hints.get("segment")),
    ]
    for keyword, column in dimension_map:
        if keyword in text and column and value:
            if any(k in text for k in ["average", "mean", "avg"]):
                actions.append(("group_mean", {"group_column": column, "value_column": value, "limit": 20}))
            else:
                actions.append(("group_sum", {"group_column": column, "value_column": value, "limit": 20}))
            break

    if any(k in text for k in ["monthly", "month-wise", "month wise", "which month", "by month"]) and date and value:
        actions.append(("monthly_sales", {"date_column": date, "value_column": value}))

    if any(k in text for k in ["yearly", "year-wise", "year wise", "which year", "annual", "by year"]) and date and value:
        actions.append(("yearly_sales", {"date_column": date, "value_column": value}))

    if any(k in text for k in ["total sales", "overall sales", "total revenue", "total amount", "sum of sales"]) and value:
        actions.append(("calculate_total", {"value_column": value}))

    if any(k in text for k in ["insight", "insights", "analyze", "analysis", "summary", "overview"]):
        actions.append(("dataset_summary", {"value_column": value, "date_column": date}))
        if value and hints.get("category"):
            actions.append(("group_sum", {"group_column": hints["category"], "value_column": value, "limit": 10}))
        if value and hints.get("region"):
            actions.append(("group_sum", {"group_column": hints["region"], "value_column": value, "limit": 10}))
        if value and date:
            actions.append(("yearly_sales", {"date_column": date, "value_column": value}))

    # If the question is a plain total/sales question, give a useful fallback.
    if not actions and value:
        actions.append(("calculate_total", {"value_column": value}))
    if not actions:
        actions.append(("dataset_summary", {"value_column": value, "date_column": date}))

    # Remove duplicate tool/argument pairs while preserving order.
    unique = []
    seen = set()
    for tool, args in actions:
        key = (tool, json.dumps(args, sort_keys=True, default=str))
        if key not in seen:
            unique.append((tool, args))
            seen.add(key)
    return unique[:5]


def execute_tool(df, tool, args):
    if tool == "inspect_dataset":
        return inspect_dataset(df)
    if tool == "numeric_statistics":
        return numeric_statistics(df)
    if tool == "missing_values":
        return missing_values(df)
    if tool == "calculate_total":
        return calculate_total(df, args["value_column"])
    if tool == "group_sum":
        return group_sum(df, args["group_column"], args["value_column"], args.get("limit", 20))
    if tool == "group_mean":
        return group_mean(df, args["group_column"], args["value_column"], args.get("limit", 20))
    if tool == "top_products":
        return top_products(df, args["product_column"], args["value_column"], args.get("limit", 10), args.get("ascending", False))
    if tool == "monthly_sales":
        return monthly_sales(df, args["date_column"], args["value_column"])
    if tool == "yearly_sales":
        return yearly_sales(df, args["date_column"], args["value_column"])
    if tool == "dataset_summary":
        return dataset_summary(df, args.get("value_column"), args.get("date_column"))
    if tool == "correlation":
        return correlation(df)
    return {"error": f"Unknown tool: {tool}"}


def make_chart_payload(observations):
    charts = []
    for observation in observations:
        result = observation["result"]
        if not isinstance(result, dict) or "error" in result or not result:
            continue
        numeric = all(isinstance(v, (int, float)) for v in result.values())
        if numeric and 2 <= len(result) <= 60:
            charts.append({
                "title": observation["tool"],
                "data": result,
            })
    return charts[:3]


def generate_final_answer(task, plan, observations):
    system = """You are the final response component of a data-analysis agent. Use ONLY the supplied tool results. Never invent or recalculate numbers. If a grouped result is supplied, identify the requested maximum/minimum directly from it. Clearly mention limitations when a requested column is missing. Answer concisely with useful bullet points."""
    payload = {"question": task, "plan": plan, "observations": observations}
    return call_llm(system, json.dumps(payload, default=str))


def run_agent(df, task: str) -> dict[str, Any]:
    schema = inspect_dataset(df)
    hints = detect_columns(df)
    state = {
        "task": task,
        "plan": [],
        "schema": schema,
        "detected_columns": hints,
        "observations": [],
        "completed": False,
    }
    events = []

    events.append({"stage": "PLAN", "message": "Creating an executable plan from the user goal."})
    state["plan"] = create_plan(task, schema, hints) or [
        "Understand the user request",
        "Select the relevant dataset tool",
        "Execute the calculation",
        "Use the observed result to answer",
    ]

    events.append({"stage": "DECIDE", "message": "Routing the request to deterministic Pandas tools."})
    actions = choose_actions(task, df, hints)

    for tool, args in actions:
        events.append({"stage": "ACT", "message": f"Executing {tool} with {args}"})
        result = execute_tool(df, tool, args)
        state["observations"].append({"tool": tool, "arguments": args, "result": result})
        events.append({"stage": "OBSERVE", "message": f"Recorded the result from {tool}."})

    state["completed"] = True
    events.append({"stage": "STATE", "message": "Plan, detected schema, tool calls, and observations are stored in agent state."})
    events.append({"stage": "RESPOND", "message": "Generating the final answer from actual tool results."})

    return {
        "state": state,
        "events": events,
        "final_answer": generate_final_answer(task, state["plan"], state["observations"]),
        "charts": make_chart_payload(state["observations"]),
    }
