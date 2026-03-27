import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")

# This is the "Status" endpoint - it tells you if your key is valid
url = "https://v3.football.api-sports.io/status"
headers = {'x-apisports-key': API_KEY}

response = requests.get(url, headers=headers)
print(response.json())