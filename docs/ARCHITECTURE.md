# Architecture

```text
                    ┌─────────────────────┐
                    │      User + CSV     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    └──────────┬──────────┘
                               │ task + dataframe
                               ▼
                    ┌─────────────────────┐
                    │   Agent Controller  │
                    └───────┬───────┬─────┘
                            │       │
                       PLAN │       │ DECIDE
                            ▼       ▼
                    ┌──────────┐  ┌──────────────┐
                    │ Ollama   │  │ Intent/Tool  │
                    │ Qwen2.5  │  │ Router       │
                    └────┬─────┘  └──────┬───────┘
                         │               │
                         │               ▼
                         │       ┌─────────────────┐
                         │       │ Pandas Tools    │
                         │       │ totals/grouping │
                         │       │ products/trends │
                         │       │ stats/missing   │
                         │       └────────┬────────┘
                         │                │
                         └───────┬────────┘
                                 ▼
                         ┌───────────────┐
                         │   OBSERVE     │
                         │ actual result │
                         └───────┬───────┘
                                 ▼
                         ┌───────────────┐
                         │  AGENT STATE  │
                         │ plan + schema │
                         │ observations  │
                         └───────┬───────┘
                                 ▼
                         ┌───────────────┐
                         │ Qwen final    │
                         │ explanation   │
                         └───────────────┘
```

## Why this is agentic

- **Goal intake:** natural-language task.
- **Planning:** local LLM creates a concise plan.
- **Decision/tool use:** a deterministic intent router maps the request to a relevant analysis tool.
- **Execution:** Pandas performs the actual computation.
- **Observation:** tool outputs are stored in state.
- **Response:** the local LLM explains only the observed results.

This avoids making the LLM itself the source of numerical truth.
