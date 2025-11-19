# github_api.py
import requests

BASE_URL = "https://api.github.com/users/"
TOKEN = None
HEADERS = {}


def fetch_user_data(username):
    """Fetch single user data"""
    response = requests.get(f"{BASE_URL}{username}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"User '{username}' not found. Status code: {response.status_code}"}

def fetch_repos_data(username):
    """Fetch repos for a single user"""
    response = requests.get(f"{BASE_URL}{username}/repos", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Repos for '{username}' not found. Status code: {response.status_code}"}

def fetch_multiple_users(usernames):
    """
    Fetch data for multiple users and return a dictionary.
    Input: ['torvalds', 'guido', 'mojombo']
    """
    data = {}
    for username in usernames:
        print(f"Fetching data for: {username}")
        user_data = fetch_user_data(username)
        repos_data = fetch_repos_data(username)
        data[username] = {
            "user": user_data,
            "repos": repos_data
        }
    return data
