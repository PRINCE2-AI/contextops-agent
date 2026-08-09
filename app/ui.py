from __future__ import annotations

import streamlit as st

from app.runner import ContextOpsRunner


st.set_page_config(page_title="ContextOps Agent", page_icon="CO", layout="wide")
st.title("ContextOps Agent")
st.caption("Context engineering layer for long-horizon agents: memory, compression, privacy, and evals.")

task = st.text_area(
    "Task",
    value="Build a long-horizon AI agent demo using OpenAI API, preserve privacy constraints, and show context compression metrics.",
    height=120,
)
payload = st.text_area(
    "Simulated external tool payload",
    value="Send research query. Contact: prince@example.com. token=sk-test-private",
    height=90,
)

if st.button("Run ContextOps", type="primary"):
    run = ContextOpsRunner().run(task, {"query": payload}, required_terms=("OpenAI API", "privacy", "compression"))
    left, right = st.columns(2)
    with left:
        st.subheader("Evaluation")
        st.json(run.evaluation.__dict__)
        st.subheader("Privacy Review")
        st.json(run.privacy.__dict__)
    with right:
        st.subheader("Context Metrics")
        st.metric("Token Estimate", run.packet.token_estimate)
        st.metric("Compression Ratio", run.packet.compression_ratio)
        st.write("Selected memories", len(run.packet.selected_memories))
    st.subheader("Managed Prompt")
    st.code(run.packet.prompt)
else:
    st.info("Run the demo to compare managed context, privacy decisions, and eval metrics.")

