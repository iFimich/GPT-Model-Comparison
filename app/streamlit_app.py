import streamlit as st
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.datavisualazer import showPlot
from src.explain_utils import build_system_prompt
from src.llm_interface import ask_gpt
from src.evaluateResponse import evaluate_response, get_cost_per_1k
from src.savereport import saveReportAll

PREDEFINED_QUESTIONS = [
    "What is linear regression?",
    "What is overfitting in machine learning?",
    "How does Random Forest work?",
    "What is the difference between classification and regression?",
    "Explain gradient boosting in simple terms."
]

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("### Options")
    tone = st.selectbox("Choose explanation style:", ["simple", "technical", "analogy"])
    length = st.selectbox("Choose response length:", ["normal", "short"])
    conversation_mode = st.radio("Mode:", ["One-shot", "Story (multi-turn)"])
    models = st.multiselect(
        "Compare Models:",
        ["gpt-4o", "gpt-3.5-turbo", "gpt-4"],
        default=["gpt-3.5-turbo"]
    )
    temperature = st.slider(
        "Temperature (creativity vs. precision):",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    if st.button("🤖 Run Demo Questions"):
        st.session_state.run_demo = True

    if "run_demo" not in st.session_state:
        st.session_state.run_demo = False

    if st.button("📊 Show Report"):
        st.session_state.show_report = True

    if "show_report" not in st.session_state:
        st.session_state.show_report = False

    if st.session_state.get("show_report"):
        if st.button("Hide Report"):
            st.session_state.show_report = False

    if st.button("💾 Save report"):
       st.session_state.save_report = True

    if "save_report" not in st.session_state:
        st.session_state.save_report = False

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.model_histories = {}
        st.session_state.totals = {}
        st.session_state.run_demo = False
        st.session_state.show_report = False


# --- Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_mode" not in st.session_state:
    st.session_state.conversation_mode = conversation_mode

if st.session_state.conversation_mode != conversation_mode:
    st.session_state.messages = []
    st.session_state.conversation_mode = conversation_mode

if "model_histories" not in st.session_state:
    st.session_state.model_histories = {}

if "totals" not in st.session_state:
    st.session_state.totals = {}

# --- Input ---
st.markdown("### 🤖 GPT Model Comparison (ML Model Explainer) Chatbot")  # H3
question = st.text_area("Ask a question about ML models:", "What is the difference between Random Forest and Gradient Boosting?")

# --- Core logic ---
def handle_question(question, tone, length, temperature, models, conversation_mode):
    if not any(m["role"] == "system" for m in st.session_state.messages):
        st.session_state.messages.append({"role": "system", "content": build_system_prompt(tone, length)})

    st.session_state.messages.append({"role": "user", "content": question})
    base_messages = list(st.session_state.messages)
    st.session_state.comparison_responses = []

    for model in models:
        if model not in st.session_state.model_histories:
            st.session_state.model_histories[model] = []
        if model not in st.session_state.totals:
            st.session_state.totals[model] = {
                "tokens": 0, "cost": 0.0, "words": 0, "key_terms": 0, "clarity": 0.0, "turns": 0
            }

        answer, tokens = ask_gpt(list(base_messages), model=model, temperature=temperature)
        cost_per_1k = get_cost_per_1k(model)
        estimated_cost = round((tokens / 1000) * cost_per_1k, 4)
        metrics = evaluate_response(answer, tokens)

        st.session_state.model_histories[model].append({"role": "user", "content": question})
        st.session_state.model_histories[model].append({"role": "assistant", "content": answer})

        st.session_state.totals[model]["tokens"] += tokens
        st.session_state.totals[model]["cost"] += estimated_cost
        st.session_state.totals[model]["words"] += metrics["words"]
        st.session_state.totals[model]["key_terms"] += metrics["key_terms"]
        st.session_state.totals[model]["clarity"] += metrics["clarity"]
        st.session_state.totals[model]["turns"] += 1

        st.session_state.comparison_responses.append({
            "model": model,
            "answer": answer,
            "tokens": tokens,
            "cost": estimated_cost,
            "cost_per_1k": cost_per_1k
        })

    if conversation_mode == "Story (multi-turn)":
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.comparison_responses[0]["answer"]})
    else:
        st.session_state.messages = []

# --- Trigger Manual Question ---
if st.button("Explain") and question.strip():
    with st.spinner("Thinking..."):
        handle_question(question, tone, length, temperature, models, conversation_mode)
        st.session_state.last_answer = st.session_state.comparison_responses[0]["answer"]

# --- Trigger Demo Questions ---
if st.session_state.run_demo:
    for demo_q in PREDEFINED_QUESTIONS:
        with st.spinner(f"Asking: {demo_q}"):
            handle_question(demo_q, tone, length, temperature, models, conversation_mode)
    st.session_state.run_demo = False

# --- Per-Model Display ---
if st.session_state.model_histories:
    st.markdown("---")
    st.markdown("### 🧠 Per-Model Conversation History")
    cols = st.columns(len(st.session_state.model_histories))
    for i, (model, messages) in enumerate(st.session_state.model_histories.items()):
        with cols[i]:
            st.markdown(f"### 🤖 `{model}`")
            for msg in messages:
                bg = "#e0f7fa" if msg["role"] == "user" else "#f1f8e9"
                align = "right" if msg["role"] == "user" else "left"
                st.markdown(
                    f"<div style='text-align: {align}; color: Black; background-color: {bg}; padding: 10px; border-radius: 10px; margin-bottom: 5px;'> {msg['content']} </div>",
                    unsafe_allow_html=True
                )

            res = next((r for r in st.session_state.comparison_responses if r["model"] == model), None)
            metrics = evaluate_response(res["answer"], res["tokens"])
            # Latest response
            st.markdown("**🆕 Latest response:**")
            st.markdown(f"""
            **🧮 Tokens:** {res['tokens']}  
            **📝 Words:** {metrics['words']}  
            **💰 Estimated Cost:** ${res['cost']}  
            **🔑 ML Keywords Used:** {metrics['key_terms']}  
            **✨ Clarity Score:** {metrics['clarity']}  
            """)

            totals = st.session_state.totals[model]
            avg_clarity = round(totals["clarity"] / max(totals["turns"], 1), 2)
            st.markdown("**📊 Total so far:**")
            st.markdown(f"""
            **🧮 Tokens:** {totals['tokens']}  
            **📝 Words:** {totals['words']}  
            **💰 Estimated Cost:** ${totals['cost']:.4f}  
            **🔑 ML Keywords Used:** {totals['key_terms']}  
            **✨ Avg. Clarity Score:** {avg_clarity}  
            **🔁 Turns:** {totals['turns']}  
            """)

# --- Plot Preview ---
if "last_answer" in st.session_state:
    showPlot(st, st.session_state.last_answer.lower())

# --- Report View ---
if st.session_state.get("show_report"):
    st.markdown("---")
    st.markdown("## 📊 Model Usage Report")
    for model, totals in st.session_state.totals.items():
        avg_clarity = round(totals["clarity"] / max(totals["turns"], 1), 2)
        st.markdown(f"### 🤖 `{model}` Summary")
        st.markdown(f"""
        **🧮 Tokens:** {totals['tokens']}  
        **📝 Words:** {totals['words']}  
        **💰 Estimated Cost:** ${totals['cost']:.4f}  
        **🔑 ML Keywords Used:** {totals['key_terms']}  
        **✨ Avg. Clarity Score:** {avg_clarity}  
        **🔁 Turns:** {totals['turns']}  
        """)

# --- Report Save Logic ---
if st.session_state.get("save_report", False):
    saveReportAll(
        models=st.session_state.totals.keys(), 
        model_totals=st.session_state.totals
    )

    st.success("✅ Report saved!")

    # Reset state to avoid repeated saving on rerun
    st.session_state.save_report = False
