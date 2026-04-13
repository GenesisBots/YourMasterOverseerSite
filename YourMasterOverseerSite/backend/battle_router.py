# battle_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import math
import random

from battle_engine import run_battle, BattleResult, TurnLog
from routers.bots import (
    BOT_REGISTRY,
    get_bot,
    refresh_bot_status,
    get_league_for_elo,
    gain_xp,
)

router = APIRouter(prefix="/api/battle", tags=["battle"])

# Recovery duration in seconds (5 minutes)
RECOVERY_SECONDS = 5 * 60

# ELO K-factor
ELO_K = 32

# Simple in-memory battle history
BATTLE_HISTORY: Dict[int, Dict[str, Any]] = {}
BATTLE_COUNTER = 0


# ---------- Bot helpers ----------

def get_bot_by_gin(gin: str) -> Dict[str, Any] | None:
    try:
        bot = get_bot(gin)
        return bot
    except HTTPException:
        return None
    except Exception:
        return None


def ensure_bot_ready_for_battle(bot: Dict[str, Any], gin_label: str):
    refresh_bot_status(bot)

    if bot.get("type") != "battle":
        raise HTTPException(status_code=400, detail=f"Bot {gin_label} is not a battle bot.")

    status = bot.get("status", "READY")
    if status != "READY":
        raise HTTPException(
            status_code=400,
            detail=f"Bot {gin_label} is not READY (current status: {status})."
        )


def mark_bot_ko(bot: Dict[str, Any]):
    now = int(time.time())
    bot["status"] = "KO"
    bot["recovery_ends_at"] = now + RECOVERY_SECONDS


def apply_elo_change(winner: Dict[str, Any], loser: Dict[str, Any]):
    winner_elo = int(winner.get("elo", 1000))
    loser_elo = int(loser.get("elo", 1000))

    expected_winner = 1.0 / (1.0 + math.pow(10, (loser_elo - winner_elo) / 400.0))
    expected_loser = 1.0 / (1.0 + math.pow(10, (winner_elo - loser_elo) / 400.0))

    new_winner_elo = winner_elo + int(ELO_K * (1 - expected_winner))
    new_loser_elo = loser_elo + int(ELO_K * (0 - expected_loser))

    winner["elo"] = new_winner_elo
    loser["elo"] = new_loser_elo

    winner["league"] = get_league_for_elo(winner["elo"])
    loser["league"] = get_league_for_elo(loser["elo"])


def apply_battle_progression(winner: Dict[str, Any], loser: Dict[str, Any], ko_occurred: bool):
    # Wins / losses
    winner["wins"] = int(winner.get("wins", 0)) + 1
    loser["losses"] = int(loser.get("losses", 0)) + 1

    # XP: winner gets more, loser gets some
    gain_xp(winner, 50 if ko_occurred else 35)
    gain_xp(loser, 20 if ko_occurred else 15)


# ---------- Pydantic models ----------

class BattleRequest(BaseModel):
    bot1_gin: str
    bot2_gin: str


class MatchmakeRequest(BaseModel):
    bot_gin: str


class TournamentRequest(BaseModel):
    bot_gins: List[str]


class TurnLogResponse(BaseModel):
    turn_number: int
    acting_gin: str
    acting_name: str
    target_gin: str
    target_name: str
    ability_used: str
    damage_dealt: int
    crit: bool
    hit: bool
    energy_before: int
    energy_after: int
    hp_before_target: int
    hp_after_target: int
    notes: List[str]


class BattleResultResponse(BaseModel):
    battle_id: int
    winner_gin: str
    winner_name: str
    loser_gin: str
    loser_name: str
    total_turns: int
    ko_occurred: bool
    started_at: int
    ended_at: int
    turns: List[TurnLogResponse]


class BattleSummary(BaseModel):
    battle_id: int
    winner_gin: str
    loser_gin: str
    started_at: int
    ended_at: int
    total_turns: int
    ko_occurred: bool


class TournamentMatchResult(BaseModel):
    round_number: int
    battle_id: int
    bot1_gin: str
    bot2_gin: str
    winner_gin: str
    loser_gin: str


class TournamentResponse(BaseModel):
    champion_gin: str
    matches: List[TournamentMatchResult]


# ---------- Core battle runner (shared) ----------

def _run_battle_and_record(bot1: Dict[str, Any], bot2: Dict[str, Any]) -> BattleResultResponse:
    global BATTLE_COUNTER

    result: BattleResult = run_battle(bot1, bot2)

    winner_bot = BOT_REGISTRY.get(result.winner_gin)
    loser_bot = BOT_REGISTRY.get(result.loser_gin)

    if winner_bot is not None and loser_bot is not None:
        if result.ko_occurred:
            mark_bot_ko(loser_bot)

        if winner_bot.get("status") in ("KO", "RECOVERING"):
            winner_bot["status"] = "READY"
            winner_bot["recovery_ends_at"] = None

        apply_elo_change(winner_bot, loser_bot)
        apply_battle_progression(winner_bot, loser_bot, result.ko_occurred)

    BATTLE_COUNTER += 1
    battle_id = BATTLE_COUNTER

    battle_record = {
        "battle_id": battle_id,
        "winner_gin": result.winner_gin,
        "winner_name": result.winner_name,
        "loser_gin": result.loser_gin,
        "loser_name": result.loser_name,
        "total_turns": result.total_turns,
        "ko_occurred": result.ko_occurred,
        "started_at": result.started_at,
        "ended_at": result.ended_at,
        "turns": [
            {
                "turn_number": t.turn_number,
                "acting_gin": t.acting_gin,
                "acting_name": t.acting_name,
                "target_gin": t.target_gin,
                "target_name": t.target_name,
                "ability_used": t.ability_used,
                "damage_dealt": t.damage_dealt,
                "crit": t.crit,
                "hit": t.hit,
                "energy_before": t.energy_before,
                "energy_after": t.energy_after,
                "hp_before_target": t.hp_before_target,
                "hp_after_target": t.hp_after_target,
                "notes": t.notes,
            }
            for t in result.turns
        ],
    }

    BATTLE_HISTORY[battle_id] = battle_record

    return BattleResultResponse(
        battle_id=battle_id,
        winner_gin=result.winner_gin,
        winner_name=result.winner_name,
        loser_gin=result.loser_gin,
        loser_name=result.loser_name,
        total_turns=result.total_turns,
        ko_occurred=result.ko_occurred,
        started_at=result.started_at,
        ended_at=result.ended_at,
        turns=[
            TurnLogResponse(**t) for t in battle_record["turns"]
        ],
    )


# ---------- Endpoints ----------

@router.post("/run", response_model=BattleResultResponse)
def run_battle_endpoint(payload: BattleRequest):
    bot1 = get_bot_by_gin(payload.bot1_gin)
    bot2 = get_bot_by_gin(payload.bot2_gin)

    if bot1 is None:
        raise HTTPException(status_code=404, detail=f"Bot not found: {payload.bot1_gin}")
    if bot2 is None:
        raise HTTPException(status_code=404, detail=f"Bot not found: {payload.bot2_gin}")

    ensure_bot_ready_for_battle(bot1, payload.bot1_gin)
    ensure_bot_ready_for_battle(bot2, payload.bot2_gin)

    return _run_battle_and_record(bot1, bot2)


@router.post("/matchmake", response_model=BattleResultResponse)
def matchmake_and_battle(payload: MatchmakeRequest):
    """
    Finds the closest-ELO READY battle bot and runs a battle.
    """
    challenger = get_bot_by_gin(payload.bot_gin)
    if challenger is None:
        raise HTTPException(status_code=404, detail=f"Bot not found: {payload.bot_gin}")

    ensure_bot_ready_for_battle(challenger, payload.bot_gin)

    challenger_elo = int(challenger.get("elo", 1000))

    candidates: List[Dict[str, Any]] = []
    for bot in BOT_REGISTRY.values():
        if bot["gin"] == challenger["gin"]:
            continue
        if bot.get("type") != "battle":
            continue
        refresh_bot_status(bot)
        if bot.get("status", "READY") != "READY":
            continue
        candidates.append(bot)

    if not candidates:
        raise HTTPException(status_code=400, detail="No suitable opponents available.")

    candidates.sort(key=lambda b: abs(int(b.get("elo", 1000)) - challenger_elo))
    opponent = candidates[0]

    return _run_battle_and_record(challenger, opponent)


@router.post("/tournament", response_model=TournamentResponse)
def run_tournament(payload: TournamentRequest):
    """
    Simple single-elimination tournament.
    Requires 2, 4, or 8 battle bots.
    """
    gins = payload.bot_gins
    n = len(gins)
    if n not in (2, 4, 8):
        raise HTTPException(status_code=400, detail="Tournament size must be 2, 4, or 8 bots.")

    bots: List[Dict[str, Any]] = []
    for gin in gins:
        bot = get_bot_by_gin(gin)
        if bot is None:
            raise HTTPException(status_code=404, detail=f"Bot not found: {gin}")
        ensure_bot_ready_for_battle(bot, gin)
        bots.append(bot)

    random.shuffle(bots)

    round_number = 1
    matches: List[TournamentMatchResult] = []

    while len(bots) > 1:
        next_round: List[Dict[str, Any]] = []
        for i in range(0, len(bots), 2):
            bot1 = bots[i]
            bot2 = bots[i + 1]

            result = _run_battle_and_record(bot1, bot2)

            match = TournamentMatchResult(
                round_number=round_number,
                battle_id=result.battle_id,
                bot1_gin=bot1["gin"],
                bot2_gin=bot2["gin"],
                winner_gin=result.winner_gin,
                loser_gin=result.loser_gin,
            )
            matches.append(match)

            winner_bot = BOT_REGISTRY[result.winner_gin]
            next_round.append(winner_bot)

        bots = next_round
        round_number += 1

    champion = bots[0]["gin"]

    return TournamentResponse(
        champion_gin=champion,
        matches=matches,
    )


@router.get("/history/{battle_id}", response_model=BattleResultResponse)
def get_battle_history(battle_id: int):
    """
    Replay-style endpoint: returns full battle log by ID.
    """
    record = BATTLE_HISTORY.get(battle_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Battle not found")

    return BattleResultResponse(
        battle_id=record["battle_id"],
        winner_gin=record["winner_gin"],
        winner_name=record["winner_name"],
        loser_gin=record["loser_gin"],
        loser_name=record["loser_name"],
        total_turns=record["total_turns"],
        ko_occurred=record["ko_occurred"],
        started_at=record["started_at"],
        ended_at=record["ended_at"],
        turns=[TurnLogResponse(**t) for t in record["turns"]],
    )
