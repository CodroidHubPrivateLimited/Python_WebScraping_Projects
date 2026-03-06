import requests

def fetch_data():
    url = "https://puirf.codroidhub.com/api/api/v1/instruments/user/getHomeFacilities"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    data = response.json()
    main_data = data.get("data", {})
    saif_data = main_data.get("saif", [])

    headers = ["Name", "Unique ID"]
    rows = []

    for item in saif_data:
        rows.append([
            item.get("name"),
            item.get("uniqueId")
        ])

    if not rows:
        rows.append(["No Data", "No Data"])

    return headers, rows
