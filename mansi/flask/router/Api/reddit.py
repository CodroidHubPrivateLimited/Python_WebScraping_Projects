import requests

def fetch_data():
    url = "https://www.reddit.com/r/python/top.json"

    headers = {
        "User-Agent": "python:reddit-app:v1.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Reddit API blocked"]]

    data = response.json()
    posts = data["data"]["children"]

    table_headers = ["Title", "Author", "Upvotes", "Comments", "Link"]
    rows = []

    for post in posts:
        post_data = post["data"]
        rows.append([
            post_data["title"],
            post_data["author"],
            post_data["ups"],
            post_data["num_comments"],
            "https://www.reddit.com" + post_data["permalink"]
        ])

    return table_headers, rows
