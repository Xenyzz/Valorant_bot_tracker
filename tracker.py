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

def get_user(nametag : str):
    name, tag = nametag.split("#")
    response_account = requests.get(
        f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}",
        headers=headers
    )
    if response_account.status_code == 200:
        return response_account.json()
    return None

def get_users_info(nametag : str) -> dict | None:
    player_acc = get_user(nametag)
    player_data = player_acc.get("data")
    if not player_data:
        return None

    account_lvl = player_data.get("account_level") #account level
    card = player_data.get("card", {}).get("small") #card picture pfp
    last_updated = player_data.get("last_update")
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

def get_api_mmr(nametag : str) -> dict | None :
    name, tag = nametag.split("#")
    response_account_mmr = requests.get(
        f"https://api.henrikdev.xyz/valorant/v3/mmr/eu/pc/{name}/{tag}",
        headers=headers
    )
    if response_account_mmr.status_code == 200:
        return response_account_mmr.json()
    return None

def get_max_rank(player_mmr : dict) -> tuple :
    peak = player_mmr.get("data", {}).get("peak")
    if not peak:
        return "Never calibrated", "-"
    highest_rank = peak.get("tier", {}).get("name")
    season = peak.get("season", {}).get("short")
    return highest_rank, season

def get_current_rank(player_mmr : dict) -> tuple:
    player_data = player_mmr.get("data")
    current_rank = player_data.get("current", {}).get("tier", {}).get("name")
    current_rr = player_data.get("current").get("rr")
    return current_rank, current_rr

#==================== to get user stats (k/d ratio, winrate) =============================

def get_match_list(nametag : str) -> dict | None:
    name, tag = nametag.split("#")
    response_account = requests.get(
        f"https://api.henrikdev.xyz/valorant/v1/stored-matches/eu/{name}/{tag}",
        headers=headers,
        params={
            "mode": "competitive"
        }
    )
    if response_account.status_code == 200:
        return response_account.json()
    return None


def get_player_stats(player_matches : dict) -> float:
    act_kills = 0
    act_deaths = 0
    for match in player_matches.get("data"):
        match_act = match.get("meta", {}).get("season", {}).get("short")
        if  match_act == "e11a1":
            act_kills += match.get("stats", {}).get("kills")
            act_deaths += match.get("stats", {}).get("deaths")

    return round((act_kills/act_deaths), 2)


if __name__ == "__main__":
    print()




