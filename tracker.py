from typing import Any

import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY_TRACKER")
headers = {
        "Authorization": API_KEY
    }

#==================== to get user info (pfp, name, etc) =============================

def get_user(name : str, tag : str):
    response_account = requests.get(
        f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}",
        headers=headers
    )
    if response_account.status_code == 200:
        player_acc = response_account.json()
        return player_acc
    return None

def get_users_info(player_acc : dict) -> dict | None:
    player_data = player_acc.get("data")
    if not player_data:
        return None

    account_lvl = player_data.get("account_level") #account level
    card = player_data.get("card", {}).get("small") #card picture pfp
    last_updated = player_data.get("last_updated")
    name = player_data.get("name")
    tag = player_data.get("tag")

    return {
        "name": name,
        "tag": tag,
        "card": card,
        "account_level": account_lvl,
        "last_updated": last_updated
    }


#==================== to get user mmr (rank, peak, current) =============================

def get_api_mmr(name : str, tag : str) -> dict | None :
    response_account_mmr = requests.get(
        f"https://api.henrikdev.xyz/valorant/v3/mmr/eu/pc/{name}/{tag}",
        headers=headers
    )
    if response_account_mmr.status_code == 200:
        player_mmr = response_account_mmr.json()
        return player_mmr
    return None

def get_max_rank(player_mmr : dict) -> tuple | None:
    peak = player_mmr.get("data", {}).get("peak")
    if not peak:
        return None
    highest_rank = peak.get("tier", {}).get("name")
    season = peak.get("season", {}).get("short")
    return highest_rank, season

def get_current_rank(player_mmr : dict):
    player_data = player_mmr["data"]["current_data"]
    return None

player = get_user(name="Xenyzz", tag="rizz")
print(get_users_info(player))


