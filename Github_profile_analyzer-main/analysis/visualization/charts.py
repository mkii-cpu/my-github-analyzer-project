# visualization/charts.py
import json
import pandas as pd
import plotly.express as px
import os

PROCESSED_PATH = os.path.join("analysis", "processed_data.json")

def load_summary(path=PROCESSED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def top_languages_bar(summary, n=10):
    langs = summary.get("top_languages", {})
    if not langs:
        return None
    df = pd.DataFrame(list(langs.items()), columns=["language","count"])
    df = df.head(n)
    fig = px.bar(df, x="language", y="count", title="Top Languages (by repo count)")
    return fig

def stars_per_repo_bar(summary):
    repos = summary.get("repos", [])
    if not repos:
        return None
    df = pd.DataFrame(repos)
    df = df.sort_values("stargazers_count", ascending=False)
    fig = px.bar(df, x="name", y="stargazers_count", title="Stars per Repository")
    return fig

def commits_timeline(summary):
    cmb = summary.get("commits_by_month", {})
    if not cmb:
        return None
    df = pd.DataFrame(list(cmb.items()), columns=["month","count"])
    df = df.sort_values("month")
    fig = px.line(df, x="month", y="count", title="Commits by month (last push per repo)")
    return fig

def repos_table(summary):
    repos = summary.get("repos", [])
    if not repos:
        return None
    df = pd.DataFrame(repos)
    return df

