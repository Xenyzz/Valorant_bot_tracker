import requests
import os




API_KEY = os.getenv("API_KEY")
headers = {
        "Authorization": "HDEV-69d0533e-ea7d-46a9-9ad6-33e25c24e598"
    }

name = "Xenyzz"
tag = "rizz"

def get_stats(name : str, tag : str):
    headers = {
        "Authorization": API_KEY
    }
    r = requests.get(f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}", headers=headers)

mmr = requests.get(
    f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{name}/{tag}",
    headers=headers
)

print(mmr.json())


