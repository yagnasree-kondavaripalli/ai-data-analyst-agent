# 🤖 AI Data Analyst Agent

A local, agentic CSV analysis system that accepts a user's natural-language data task, creates a plan with an LLM, selects analysis tools, executes deterministic Pandas calculations, stores observations as state, and generates a final answer.

## Contest mapping

| Requirement | Implementation |
|---|---|
| Accept user goal | Streamlit task box |
| Planning | Local Qwen2.5 3B creates a short plan |
| Reasoning/action selection | Intent/tool router chooses the appropriate tool |
| Tool use | Pandas analysis functions |
| State/context | `state` stores task, schema, plan, detected columns and observations |
| Execution | Tools calculate totals, groupings, products, trends, statistics and missing values |
| Final response | Local Qwen explains only the observed results |

## Agent workflow

**Plan → Decide → Act → Observe → State → Respond**

This is not a one-shot chatbot. The LLM plans the work and explains results; Python/Pandas is responsible for numerical computation.

## Features

- Upload any CSV from the UI.
- Dataset preview and schema inspection.
- Automatic detection of common value/date/dimension columns.
- Total and average calculations.
- Grouped sales/value analysis by region, category, sub-category, state, city and segment when present.
- Top or bottom products/items.
- Monthly and yearly time-series analysis.
- Descriptive statistics.
- Missing-value analysis.
- Correlation analysis for numeric columns.
- Automatic business-insight workflow.
- Charts for compact numeric results.
- Agent activity log.
- Agent state/debug view.
- No OpenAI API or paid credits required.

## Technology

- Python
- Streamlit
- Pandas
- Ollama
- Qwen2.5 3B

## Requirements

- Windows/macOS/Linux
- Python 3.10+ recommended
- Ollama installed and available in PATH
- About 2 GB+ free disk space for the Qwen2.5 3B model

## Fastest Windows start

After installing Python and Ollama, double-click `start_windows.bat`, or use the manual commands below.

## Setup — Windows

### 1. Open the project

```powershell
cd "C:\path\to\ai-data-analyst-agent"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama from its official Windows download page:

https://ollama.com/download/windows

Restart the terminal after installation.

### 5. Download the local model

```powershell
ollama pull qwen2.5:3b
```

Optional direct test:

```powershell
ollama run qwen2.5:3b
```

Type `Hello`, confirm it responds, then press `Ctrl+C` to exit.

### 6. Start the application

```powershell
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, normally:

http://localhost:8501

## How to use

1. Upload a CSV.
2. Confirm the row/column counts.
3. Enter a natural-language question.
4. Click **Run Agent**.
5. Review the plan, tool activity, result, chart and final answer.

## Sample questions

- Which region has the highest sales?
- Which category has the highest sales?
- Give me the top 10 products by sales.
- Which month had the highest sales?
- Which year had the highest sales?
- Compare average sales across regions.
- Show missing values in the dataset.
- What are the descriptive statistics?
- Analyze the dataset and give me 5 important business insights.

## Demo dataset

The supplied contest demo dataset is a sales CSV with approximately 9,800 rows and 18 columns. Upload it through the UI as `train.csv`.

The application does not hard-code a dataset path.

## Project structure

```text
ai-data-analyst-agent/
├── app.py
├── agent.py
├── tools.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── train.csv            # local demo dataset; verify license before public redistribution
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md
│   └── SLIDES_OUTLINE.md
└── tests/
    └── test_tools.py
```

## Testing

Run:

```powershell
python -m pytest tests
```

If `pytest` is not installed, install it with `pip install pytest`.

## Design decisions

### Why local Qwen?

The project avoids paid API credits and demonstrates that the LLM can run locally.

### Why Pandas tools?

Numerical operations such as sums, groupings and time-series aggregation should be deterministic. The LLM should not invent or approximate business numbers.

### Why a router?

A small local model can make unreliable tool-selection decisions. The router converts explicit user intent into a deterministic tool call while the LLM remains responsible for planning and explanation.

## Limitations

- Very large CSVs may require additional memory optimization.
- The intent router currently focuses on common analytics language and common column names.
- Qwen2.5 3B is a small local model; complex natural-language requests may require extending the router.
- The current system is optimized for tabular CSV analysis, not arbitrary databases.

## Future scope

- SQL database connector.
- More advanced query planning.
- Automatic chart selection.
- Multi-file analysis.
- Data cleaning recommendations.
- Exportable PDF/Excel reports.
- Additional local models.

## Submission notes

Before publishing to GitHub:

1. Do not commit API keys or secrets.
2. Verify the dataset license before redistributing the CSV.
3. Mention that Ollama/Qwen is used locally.
4. Include a 2–5 minute demo video.
5. Show the Plan → Act → Observe workflow during the demo.
