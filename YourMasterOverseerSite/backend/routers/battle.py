from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random
import time

from .bots import BOT_REGISTRY, get_league_for_elo, gain_xp, refresh_bot_status

router = APIRouter(
    prefix="/api/battle",
    tags=["battle"]
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class BattleRequest(BaseModel):
    bot1_gin: str
    bot2_gin: str


# -----------------------------
# SIMPLE DAMAGE FORMULA
# -----------------------------
def calculate_damage(attacker, defender):
    atk = attacker["stats"]["attack"]
    defn = defender["stats"]["defense"]
    base = max(1, atk - int(defn * 0.4))
    return random.randint(int(base * 0.8), int(base * 1.2))


# -----------------------------
# HIT / CRIT / DODGE
# -----------------------------
def roll_hit(attacker, defender):
    acc = attacker["stats"]["accuracy"]
    evd = defender["stats"]["evasion"]
    chance = acc - (evd * 0.5)
    chance = max(10, min(95, chance))
    return random.random() < (chance / 100)


def roll_crit(attacker):
    luck = attacker["stats"]["luck"]
    return random.random() < (luck / 200)  # ~0.5% to 50%


# -----------------------------
# MAIN BATTLE ENDPOINT
# -----------------------------
@router.post("/run")
def run_battle(request: BattleRequest):

    if request.bot1_gin not in BOT_REGISTRY:
        raise HTTPException(status_code=404, detail="Bot 1 not found")
    if request.bot2_gin not in BOT_REGISTRY:
        raise HTTPException(status_code=404, detail="Bot 2 not found")

    bot1 = BOT_REGISTRY[request.bot1_gin]
    bot2 = BOT_REGISTRY[request.bot2_gin]

    refresh_bot_status(bot1)
    refresh_bot_status(bot2)

    if bot1["status"] != "READY":
        raise HTTPException(status_code=400, detail="Bot 1 is not READY")
    if bot2["status"] != "READY":
        raise HTTPException(status_code=400, detail="Bot 2 is not READY")

    # HP pools
    hp1 = bot1["stats"]["stamina"] * 2
    hp2 = bot2["stats"]["stamina"] * 2

    turns = []
    turn_number = 1

    attacker = bot1
    defender = bot2
    attacker_hp = hp1
    defender_hp = hp2

    while attacker_hp > 0 and defender_hp > 0 and turn_number <= 50:

        hit = roll_hit(attacker, defender)
        crit = False
        dmg = 0

        if hit:
            dmg = calculate_damage(attacker, defender)
            crit = roll_crit(attacker)
            if crit:
                dmg = int(dmg * 1.5)
            defender_hp -= dmg

        turns.append({
            "turn_number": turn_number,
            "acting_gin": attacker["gin"],
            "acting_name": attacker["name"],
            "target_gin": defender["gin"],
            "target_name": defender["name"],
            "hit": hit,
            "crit": crit,
            "damage_dealt": dmg,
            "attacker_hp_after": attacker_hp,
            "defender_hp_after": max(0, defender_hp),
            "ability_used": "Basic Attack"
        })

        # swap attacker/defender
        attacker, defender = defender, attacker
        attacker_hp, defender_hp = defender_hp, attacker_hp
        turn_number += 1

    # Determine winner
    if attacker_hp <= 0:
        winner = defender
        loser = attacker
    else:
        winner = attacker
        loser = defender

    # Update stats
    winner["wins"] += 1
    loser["losses"] += 1

    # ELO
    winner["elo"] += 15
    loser["elo"] -= 10
    winner["league"] = get_league_for_elo(winner["elo"])
    loser["league"] = get_league_for_elo(loser["elo"])

    # XP
    gain_xp(winner, 50)
    gain_xp(loser, 20)

    # KO timer for loser
    loser["status"] = "KO"
    loser["recovery_ends_at"] = int(time.time()) + 60  # 1 minute

    return {
        "winner_gin": winner["gin"],
        "winner_name": winner["name"],
        "loser_gin": loser["gin"],
        "loser_name": loser["name"],
        "turns": turns
    }
