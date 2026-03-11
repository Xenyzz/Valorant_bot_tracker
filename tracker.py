import requests
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY_TRACKER")
headers = {"Authorization": API_KEY}

# Current act — update when a new act drops
CURRENT_ACT = "e11a1"


# ==================== Account info ====================

def get_user(nametag: str) -> dict | None:
    try:
        name, tag = nametag.split("#", 1)
    except ValueError:
        logger.error(f"Invalid nametag format: '{nametag}' (expected Name#TAG)")
        return None

    try:
        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        logger.warning(f"get_user: status {response.status_code} for '{nametag}'")
    except requests.RequestException as e:
        logger.error(f"get_user request error: {e}")
    return None


def get_users_info(nametag: str) -> dict | None:
    player_acc = get_user(nametag)
    if not player_acc:
        return None

    player_data = player_acc.get("data")
    if not player_data:
        return None

    return {
        "name": player_data.get("name"),
        "tag": player_data.get("tag"),
        "card": player_data.get("card", {}).get("small"),
        "account_level": player_data.get("account_level"),
        "last_updated": player_data.get("last_update"),
    }


# ==================== MMR / Rank ====================

def get_api_mmr(nametag: str) -> dict | None:
    try:
        name, tag = nametag.split("#", 1)
    except ValueError:
        return None

    try:
        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v3/mmr/eu/pc/{name}/{tag}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        logger.warning(f"get_api_mmr: status {response.status_code} for '{nametag}'")
    except requests.RequestException as e:
        logger.error(f"get_api_mmr request error: {e}")
    return None


def get_max_rank(player_mmr: dict) -> tuple:
    try:
        peak = player_mmr.get("data", {}).get("peak")
        if not peak:
            return "Never calibrated", "-"
        highest_rank = peak.get("tier", {}).get("name", "Unknown")
        season = peak.get("season", {}).get("short", "-")
        return highest_rank, season
    except Exception as e:
        logger.error(f"get_max_rank error: {e}")
        return "Unknown", "-"


def get_current_rank(player_mmr: dict) -> tuple:
    try:
        current = player_mmr.get("data", {}).get("current", {})
        rank = current.get("tier", {}).get("name", "Unranked")
        rr = current.get("rr", 0)
        return rank, rr
    except Exception as e:
        logger.error(f"get_current_rank error: {e}")
        return "Unranked", 0


# ==================== Match stats ====================

def get_match_list(nametag: str) -> dict | None:
    try:
        name, tag = nametag.split("#", 1)
    except ValueError:
        return None

    try:
        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v1/stored-matches/eu/{name}/{tag}",
            headers=headers,
            timeout=10,
            params={"mode": "competitive"}
        )
        if response.status_code == 200:
            return response.json()
        logger.warning(f"get_match_list: status {response.status_code} for '{nametag}'")
    except requests.RequestException as e:
        logger.error(f"get_match_list request error: {e}")
    return None


def get_player_stats(player_matches: dict) -> float | str:
    try:
        matches = player_matches.get("data") or []
        act_kills = 0
        act_deaths = 0

        for match in matches:
            act = match.get("meta", {}).get("season", {}).get("short")
            if act == CURRENT_ACT:
                act_kills += match.get("stats", {}).get("kills", 0)
                act_deaths += match.get("stats", {}).get("deaths", 0)

        if act_deaths == 0:
            return "N/A" if act_kills == 0 else str(act_kills)  # all kills, no deaths

        return round(act_kills / act_deaths, 2)

    except Exception as e:
        logger.error(f"get_player_stats error: {e}")
        return "N/A"