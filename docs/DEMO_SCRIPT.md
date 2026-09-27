# 3-minute demo script

## 0:00–0:20 — Problem
“Business users often have CSV data but need technical help to analyze it. This project is an AI Data Analyst Agent that accepts a natural-language task and performs the analysis through tools.”

## 0:20–0:45 — Upload
Upload `train.csv`. Show the row/column counts and schema.

Say: “The application accepts the dataframe directly, so the agent is not tied to one hard-coded file.”

## 0:45–1:30 — Agentic task
Ask: “Which region has the highest sales?”

Show the activity:
PLAN → DECIDE → ACT → OBSERVE → STATE → RESPOND.

Point out that `group_sum(Region, Sales)` is executed by Pandas and the numeric result comes from the dataset.

## 1:30–2:10 — Second task
Ask: “Give me the top 10 products by sales.”

Show the product chart and answer.

## 2:10–2:40 — Insight task
Ask: “Analyze the dataset and give me 5 important business insights.”

Show that multiple tools can be executed and their observations are passed into the final response.

## 2:40–3:00 — Architecture
Explain: “Qwen handles planning and natural-language explanation. A deterministic router selects tools, Pandas executes calculations, and the agent stores observations as state. No paid API is required because the LLM runs locally through Ollama.”
