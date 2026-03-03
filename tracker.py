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
        player_acc = response_account.json()
        return player_acc
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
        player_mmr = response_account_mmr.json()
        return player_mmr
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


if __name__ == "__main__":
    name = "alisanesedaya"
    tag = "ttv"
    region = "eu"
    platform = "pc"
    response_account = requests.get(
        f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{name}/{tag}",
        headers=headers
    )
    response_account = response_account.json()

    current_act_data = []
    for match in response_account.get("data"):
        match_act = match.get("meta", {}).get("season", {}).get("short")
        match_mode = match.get("meta", {}).get("mode")
        if  match_act == "e11a1" and match_mode == "Competitive":
            current_act_data.append(match)



    print(len(current_act_data))

    #
    # for match in current_act_data:
    #     match_stats = match.get("stats")
    #     if match_stats:
    #         rank = match_stats.get("rank")
