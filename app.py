import io
import streamlit as st
import pandas as pd

from agent import run_agent

st.set_page_config(page_title="AI Data Analyst Agent", page_icon="🤖", layout="wide")

st.title("🤖 AI Data Analyst Agent")
st.caption("Local LLM + deterministic Pandas tools | Plan → Decide → Act → Observe → State → Respond")

with st.sidebar:
    st.header("⚙️ Agent setup")
    st.markdown("**LLM:** Ollama / Qwen2.5 3B")
    st.markdown("**Data engine:** Pandas")
    st.markdown("**API cost:** $0")
    st.divider()
    st.markdown("### Workflow")
    st.markdown("1. Upload a CSV\n2. Describe the analysis\n3. Agent creates a plan\n4. Router selects tools\n5. Pandas executes calculations\n6. Results become agent state\n7. Local LLM explains the results")
    st.divider()
    st.info("The LLM does not calculate business numbers itself. Python/Pandas performs the calculations, reducing hallucinated results.")

uploaded = st.file_uploader("📁 Upload your CSV dataset", type=["csv"], help="The uploaded dataframe is passed directly to the agent; no file path is hard-coded.")

df = None
if uploaded:
    try:
        # Read through BytesIO so the same Streamlit upload can be reread safely.
        raw = uploaded.getvalue()
        df = pd.read_csv(io.BytesIO(raw))
        st.success(f"Loaded **{uploaded.name}** successfully.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", f"{len(df.columns):,}")
        c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
        c4.metric("Numeric columns", f"{len(df.select_dtypes(include='number').columns):,}")

        with st.expander("👀 Preview", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)

        with st.expander("🧾 Dataset schema"):
            schema_df = pd.DataFrame({
                "Column": list(df.columns),
                "Type": [str(df[c].dtype) for c in df.columns],
                "Missing": [int(df[c].isna().sum()) for c in df.columns],
                "Unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
            })
            st.dataframe(schema_df, use_container_width=True)
    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")
        df = None

st.subheader("💬 Ask your data analyst")
examples = [
    "Which region has the highest sales?",
    "Which category has the highest sales?",
    "Give me the top 10 products by sales.",
    "Which month had the highest sales?",
    "Which year had the highest sales?",
    "Compare average sales across regions.",
    "Show missing values in the dataset.",
    "Analyze the dataset and give me 5 important business insights.",
]
example = st.selectbox("Quick examples", ["Choose an example"] + examples)
task = st.text_area("Enter your task", value="" if example == "Choose an example" else example, height=110)

run = st.button("🚀 Run Agent", type="primary", disabled=(df is None or not task.strip()), use_container_width=True)

if run:
    with st.spinner("Agent is planning and analyzing..."):
        try:
            result = run_agent(df, task.strip())
        except Exception as exc:
            st.error(str(exc))
            st.stop()

    st.success("Analysis completed.")

    st.subheader("🧠 Agent Activity")
    for event in result["events"]:
        stage = event["stage"]
        icon = {"PLAN": "📝", "DECIDE": "🧭", "ACT": "🛠️", "OBSERVE": "👀", "STATE": "🧠", "RESPOND": "💬"}.get(stage, "•")
        st.write(f"{icon} **{stage}** — {event['message']}")

    st.subheader("📋 Plan")
    for i, step in enumerate(result["state"]["plan"], 1):
        st.write(f"**{i}.** {step}")

    st.subheader("💡 Final Answer")
    st.markdown(result["final_answer"])

    if result.get("charts"):
        st.subheader("📊 Supporting charts")
        for chart in result["charts"]:
            st.caption(chart["title"].replace("_", " ").title())
            chart_df = pd.DataFrame.from_dict(chart["data"], orient="index", columns=["Value"])
            st.bar_chart(chart_df)

    with st.expander("🔎 Agent State / Debug Information"):
        st.json(result["state"])

st.divider()
st.caption("Contest prototype • Local Qwen2.5 3B + Pandas • No OpenAI API required")
