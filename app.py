import os
import json
from dotenv import load_dotenv
import streamlit as st
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase

load_dotenv()
if os.getenv("DATABASE_URL") == "":
    raise ValueError("DATABASE_URL environment variable is not set.")

st.set_page_config(page_title="Data Quality AI")
st.title("Data Quality AI Assistant")
st.markdown("Ask questions about your data quality, anomalies, profiling and exploration")

DB_URL = os.getenv("DATABASE_URL")

@st.cache_resource
def load_metadata():
    with open("metadata.json", "r", encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2)

@st.cache_resource
def get_agent():
    db = SQLDatabase.from_uri(DB_URL)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    metadata_str = load_metadata().replace("{", "{{").replace("}", "}}")
    system_prefix = f"""You are an expert AI Data Analyst. Your goal is to provide accurate data quality insights from an SQLite database.

BUSINESS CONTEXT & SCHEMA METADATA:
{metadata_str}

CRITICAL RULES:
1. READ-ONLY: Use ONLY SELECT statements. Do not modify data.
2. USE METADATA: Check the JSON above to map business terms to columns and understand anomalies.
3. NO TECHNICAL CLUTTER: Speak like a business partner. Never expose raw schema or SQL.
4. AGGREGATION & TRANSPARENCY: When asked for summaries (totals, top 3, volume), you MUST perform the calculation (SUM, COUNT, GROUP BY) on the ENTIRE table. NEVER use LIMIT before aggregating. Only use LIMIT 10 when explicitly showing raw individual rows. Always list exact categories when counting.
5. SQLITE SYNTAX: Column names with spaces or special characters MUST be wrapped in double quotes (e.g., "Transaction Value", "Customer Email").

TONE & STYLE:
Be concise. Start with the direct answer. End with one specific follow-up question.
"""

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        prefix=system_prefix,
        verbose=True
    )
    return agent

agent_executor = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about empty fields, outliers, or basic profiling..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                recent_history = st.session_state.messages[-5:-1]
                history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_history])
                full_prompt = f"""Chat History:
                {history_text}

                User's New Request: {prompt}

                (Answer the new request. If it refers to previous data, use the Chat History to understand the context.)"""

                response = agent_executor.invoke({"input": full_prompt})
                result = response["output"]
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                error_msg = f"An error occured while executing {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
