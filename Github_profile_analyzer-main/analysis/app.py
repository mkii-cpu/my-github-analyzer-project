# app.py
import streamlit as st
import subprocess
import sys
import os
import json
from visualization import charts

RAW_PATH = os.path.join("analysis", "raw_data.json")
PROCESSED_PATH = os.path.join("analysis", "processed_data.json")
FETCHER_SCRIPT = "fetch_data.py"
PROCESSOR_SCRIPT = "fcd4bce1-2143-4593-af83-2bbb7aa37da4.py"

st.set_page_config(page_title="GitHub Profile Analyzer", layout="wide")
st.title("GitHub Profile Analyzer")

col1, col2 = st.columns([1,3])
with col1:
    username = st.text_input("GitHub username", value="")
    fetch = st.button("Fetch & Analyze")

with col2:
    st.markdown("Enter a GitHub username and click **Fetch & Analyze**. If you already have `analysis/processed_data.json`, the app will load that.")

def run_fetch(username):
    # run fetcher script using subprocess (safer than import)
    try:
        subprocess.check_call([sys.executable, FETCHER_SCRIPT], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError:
        # fallback: call fetch_data.fetch_and_save via python -c
        cmd = f'{sys.executable} -c "import fetch_data; fetch_data.fetch_and_save(\'{username}\')"'
        subprocess.check_call(cmd, shell=True)

def run_processor():
    subprocess.check_call([sys.executable, PROCESSOR_SCRIPT])

def load_summary():
    if not os.path.exists(PROCESSED_PATH):
        st.warning("No processed summary found. Run fetch + analyze first.")
        return None
    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

if fetch:
    if not username:
        st.error("Please enter a username.")
    else:
        st.info("Running fetcher...")
        # Call fetch_data.py by running: python fetch_data.py (but that script expects input).
        # We'll call fetch_and_save by running fetch_data module with -c to pass username
        cmd = f'{sys.executable} -c "import fetch_data; fetch_data.fetch_and_save(\'{username}\')"'
        try:
            subprocess.check_call(cmd, shell=True)
            st.success("Fetched raw data.")
        except Exception as e:
            st.error(f"Fetcher error: {e}")

        st.info("Running processor...")
        try:
            # run processor script which reads analysis/raw_data.json and writes processed_data.json
            subprocess.check_call([sys.executable, PROCESSOR_SCRIPT])
            st.success("Analysis complete.")
        except Exception as e:
            st.error(f"Processor error: {e}")

summary = load_summary()
if summary:
    st.subheader("Profile summary")
    profile = summary.get("profile", {})
    st.write(profile)

    st.subheader("Totals")
    st.write(summary.get("totals", {}))

    # Charts
    st.subheader("Charts")
    colA, colB = st.columns(2)
    with colA:
        fig1 = charts.top_languages_bar(summary)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    with colB:
        fig2 = charts.stars_per_repo_bar(summary)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

    fig3 = charts.commits_timeline(summary)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Repos table")
    df = charts.repos_table(summary)
    if df is not None:
        st.dataframe(df)

