import requests

def fetch_data():
    url = "https://puirf.codroidhub.com/api/api/v1/instruments/user/getHomeFacilities?upcomingLimit=2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    data = response.json()

    main_data = data.get("data", {})
    saif_data = main_data.get("saif", [])

   
    headers = ["Name", "Unique ID"]

    rows = []
    for item in saif_data:
        rows.append([
            item.get("name", "N/A"),
            item.get("uniqueId", "N/A")
        ])

    return headers, rows
