# fcd4bce1-2143-4593-af83-2bbb7aa37da4.py
import os
import json
import pandas as pd

DEFAULT_RAW_PATH = os.path.join("analysis", "raw_data.json")
PROCESSED_OUT = os.path.join("analysis", "processed_data.json")

def load_raw_json(filename=None):
    """Load the raw data JSON file (default: analysis/raw_data.json)."""
    path = filename if filename else DEFAULT_RAW_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def json_to_dfs(data):
    """Return (profile_df, repos_df) from raw json structure."""
    profile_data = data.get("profile", {}) or {}
    repos_data = data.get("repos", []) or []
    profile_df = pd.DataFrame([profile_data])
    repos_df = pd.DataFrame(repos_data)
    return profile_df, repos_df

def clean_repos_df(df):
    """Clean repos DataFrame: parse dates, fill missing, cast numeric."""
    if df is None or df.empty:
        # produce empty but consistent dataframe
        cols = ['name','full_name','created_at','updated_at','pushed_at','language',
                'stargazers_count','forks_count','watchers_count','size']
        return pd.DataFrame(columns=cols)

    # parse date columns
    for col in ['created_at','updated_at','pushed_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # language
    if 'language' in df.columns:
        df['language'] = df['language'].fillna('Unknown')
    else:
        df['language'] = 'Unknown'

    # numeric columns: ensure they exist and are ints
    for col in ['stargazers_count','forks_count','watchers_count','size']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0

    return df

# --- analysis helpers ---
def total_stars(repos_df):
    if repos_df is None or repos_df.empty:
        return 0
    return int(repos_df['stargazers_count'].sum())

def top_repos_by_stars(repos_df, n=5):
    if repos_df is None or repos_df.empty:
        return repos_df.head(0)
    return repos_df.sort_values('stargazers_count', ascending=False).head(n)[
        ['name','stargazers_count','language','forks_count','watchers_count']
    ]

def top_languages(repos_df, n=6):
    if repos_df is None or repos_df.empty:
        return {}
    return repos_df['language'].value_counts().head(n).to_dict()

def avg_stars_per_repo(repos_df):
    if repos_df is None or repos_df.empty:
        return 0.0
    return float(repos_df['stargazers_count'].mean())

def commits_by_month(repos_df):
    if repos_df is None or repos_df.empty:
        return {}
    df = repos_df.dropna(subset=['pushed_at']).copy()
    if df.empty:
        return {}
    df['month'] = df['pushed_at'].dt.to_period('M').astype(str)
    series = df['month'].value_counts().sort_index()
    return series.to_dict()

def popularity_score(repos_df):
    """Simple normalized popularity score 0-100 per repo"""
    if repos_df is None or repos_df.empty:
        return pd.Series(dtype=float)
    s = repos_df[['stargazers_count','forks_count','watchers_count']].sum(axis=1)
    mn, mx = s.min(), s.max()
    if mn == mx:
        return pd.Series([50.0]*len(s), index=repos_df.index)
    return ((s - mn) / (mx - mn) * 100).round(2)

def build_summary(profile_df, repos_df):
    """Return a JSON-serializable dict for UI/visualization."""
    # safe profile
    profile = {}
    if profile_df is not None and not profile_df.empty:
        p = profile_df.iloc[0].to_dict()
        profile = {
            "login": p.get('login'),
            "name": p.get('name'),
            "followers": int(p.get('followers') or 0),
            "following": int(p.get('following') or 0),
            "public_repos": int(p.get('public_repos') or 0),
            "created_at": p.get('created_at')
        }

    # clean repos
    repos_df = clean_repos_df(repos_df)
    if not repos_df.empty:
        repos_df = repos_df.copy()
        repos_df['popularity'] = popularity_score(repos_df)

    # build list of repos serializable
    repos_list = []
    for _, r in repos_df.iterrows():
        repos_list.append({
            "name": r.get('name'),
            "full_name": r.get('full_name'),
            "language": r.get('language'),
            "stargazers_count": int(r.get('stargazers_count') or 0),
            "forks_count": int(r.get('forks_count') or 0),
            "watchers_count": int(r.get('watchers_count') or 0),
            "size": int(r.get('size') or 0),
            "pushed_at": r['pushed_at'].isoformat() if pd.notna(r['pushed_at']) else None,
            "updated_at": r['updated_at'].isoformat() if pd.notna(r['updated_at']) else None,
            "created_at": r['created_at'].isoformat() if pd.notna(r['created_at']) else None,
            "popularity": float(r['popularity']) if 'popularity' in r else None
        })

    summary = {
        "profile": profile,
        "totals": {
            "total_repos": len(repos_df),
            "total_stars": total_stars(repos_df),
            "avg_stars_per_repo": round(avg_stars_per_repo(repos_df), 2)
        },
        "top_languages": top_languages(repos_df),
        "top_repos": top_repos_by_stars(repos_df, n=5).to_dict(orient="records"),
        "repos": repos_list,
        "commits_by_month": commits_by_month(repos_df)
    }
    return summary

def save_summary(summary, out_path=PROCESSED_OUT):
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Processed summary saved to:", out_path)

if __name__ == "__main__":
    # CLI quick-run: load raw -> build summary -> save processed
    raw_path = DEFAULT_RAW_PATH
    if not os.path.exists(raw_path):
        print(f"No raw file found at '{raw_path}'. Run fetcher first.")
    else:
        raw = load_raw_json(raw_path)
        p_df, r_df = json_to_dfs(raw)
        r_df = clean_repos_df(r_df)
        summary = build_summary(p_df, r_df)
        save_summary(summary)
        print("Summary keys:", list(summary.keys()))
