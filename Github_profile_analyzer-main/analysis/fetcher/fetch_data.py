# fetch_data.py
import requests
import json
import os

GITHUB_API = "https://api.github.com/users/{}"
PER_PAGE = 100

def _headers():
    token = os.environ.get("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")
    if token:
        return {"Authorization": f"token {token}"}
    return {}

def fetch_profile(username):
    """Fetch basic user profile"""
    url = GITHUB_API.format(username)
    r = requests.get(url, headers=_headers())
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch profile: {r.status_code} - {r.text}")
    return r.json()

def fetch_repos(username):
    """Fetch all repositories handling pagination."""
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API.format(username)}/repos?per_page={PER_PAGE}&page={page}"
        r = requests.get(url, headers=_headers())
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch repos: {r.status_code} - {r.text}")
        page_data = r.json()
        if not page_data:
            break
        repos.extend(page_data)
        if len(page_data) < PER_PAGE:
            break
        page += 1
    return repos

def save_raw(profile, repos, out_folder="analysis", out_name="raw_data.json"):
    """Save raw JSON to disk for Member 2"""
    if not os.path.exists(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    path = os.path.join(out_folder, out_name)
    data = {"profile": profile, "repos": repos}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Raw data saved to: {path}")
    return path

def fetch_and_save(username):
    """Main function for Member 1 workflow"""
    print(f"Fetching GitHub data for '{username}' ...")
    profile = fetch_profile(username)
    repos = fetch_repos(username)
    out_path = save_raw(profile, repos)
    print("Done! Member 2 can now process", out_path)
    return out_path

if __name__ == "__main__":
    user = input("Enter GitHub username: ").strip()
    if not user:
        print("No username entered. Exiting.")
    else:
        try:
            fetch_and_save(user)
        except Exception as e:
            print("Error:", e)
