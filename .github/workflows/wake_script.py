import requests

url = "https://lauren-ops-audit.streamlit.app/"

try:
    response = requests.get(url)
    print(f"Pinged {url} - Status Code: {response.status_code}")
except Exception as e:
    print(f"Failed to ping: {e}")