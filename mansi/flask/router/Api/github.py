import requests

def fetch_data():
    url = "https://api.github.com/users/torvalds/repos"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    data = response.json()

    headers = [
        "Repo Name",
        "Repo ID",
        "Full Name",
        "Stars",
        "Language",
        "Repo URL"
    ]

    rows = []
    for repo in data:
        rows.append([
            repo.get("name"),
            repo.get("id"),
            repo.get("full_name"),
            repo.get("stargazers_count"),
            repo.get("language"),
            repo.get("html_url")
        ])

    return headers, rows
