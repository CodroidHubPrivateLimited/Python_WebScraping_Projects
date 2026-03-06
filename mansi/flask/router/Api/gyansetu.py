import requests

def fetch_data():
    url = "https://gyansetu.codroidhub.com/api/universities"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    data = response.json()
    main_data = data.get("data", [])

    headers = [
        "University Name",
        "Address",
        "Registered Students",
        "Logo"
    ]

    rows = []
    for uni in main_data:
        rows.append([
            uni.get("name"),
            uni.get("address"),
            uni.get("registeredStudentCount"),
            uni.get("logo")
        ])

    return headers, rows
