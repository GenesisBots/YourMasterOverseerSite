from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random
import time
from typing import List, Dict, Any, Optional

router = APIRouter(
    prefix="/api/bots",
    tags=["bots"]
)

# ============================
# BOT REGISTRY (in-memory)
# ============================
BOT_REGISTRY: Dict[str, Dict[str, Any]] = {}


# ============================
# MODELS
# ============================
class MintRequest(BaseModel):
    type: str
    name: Optional[str] = None
    # Optional: player-selected card style for *their* bots
    card_style: Optional[str] = None
    # Optional: mark as npc/store bot so style is auto-assigned
    role: Optional[str] = None  # "player", "npc", "store", etc.
    region: Optional[str] = None  # for region-themed style weighting


class CardStyleUpdateRequest(BaseModel):
    gin: str
    card_style: str


# ============================
# GIN GENERATOR
# ============================
def generate_gin(bot_type: str):
    segment1 = random.randint(1000, 9999)
    segment2 = random.randint(1000, 9999)

    bot_type = bot_type.upper()

    if bot_type == "BATTLE":
        return f"GIN-BOT-BATTLE-{segment1}-{segment2}"
    elif bot_type == "TRADING":
        return f"GIN-BOT-TRADING-{segment1}-{segment2}"
    elif bot_type == "EVOLUTION":
        return f"GIN-BOT-EVO-{segment1}-{segment2}"
    else:
        return f"GIN-BOT-UNKNOWN-{segment1}-{segment2}"


# ============================
# AUTO NAME GENERATOR
# ============================
BATTLE_NAMES = ["Ironfang", "ShadowFrame", "VX-9 Sentinel", "Kappa-Strike", "Omega Warden"]
TRADING_NAMES = ["TradeUnit-Sigma", "Quantum Ledger", "MarketWeaver", "SignalNode-7", "AlphaFlow"]
EVOLUTION_NAMES = ["Evo-Sprout-7", "Genome-Delta", "MorphUnit-3", "Echelon-42", "BioFrame-9"]

def auto_name(bot_type: str):
    if bot_type == "battle":
        return random.choice(BATTLE_NAMES)
    elif bot_type == "trading":
        return random.choice(TRADING_NAMES)
    elif bot_type == "evolution":
        return random.choice(EVOLUTION_NAMES)
    return "Unnamed-Bot"


# ============================
# STAT PROFILES
# ============================
def generate_stats(bot_type: str):
    if bot_type == "battle":
        return {
            "attack": random.randint(20, 80),
            "defense": random.randint(20, 80),
            "speed": random.randint(20, 80),
            "accuracy": random.randint(20, 80),
            "evasion": random.randint(20, 80),
            "stamina": random.randint(20, 80),
            "luck": random.randint(1, 100)
        }

    elif bot_type == "trading":
        return {
            "signal_strength": random.randint(20, 80),
            "risk_tolerance": random.randint(1, 100),
            "execution_speed": random.randint(20, 80),
            "market_awareness": random.randint(20, 80),
            "pattern_recognition": random.randint(20, 80),
            "latency_score": random.randint(1, 100),
            "stability": random.randint(20, 80)
        }

    elif bot_type == "evolution":
        return {
            "mutation_rate": random.uniform(0.01, 0.15),
            "fitness_score": random.randint(20, 80),
            "adaptability": random.randint(20, 80),
            "complexity": random.randint(20, 80),
            "resilience": random.randint(20, 80)
        }

    return {}


# ============================
# LEAGUE / ELO / XP HELPERS
# ============================
def get_league_for_elo(elo: int) -> str:
    if elo < 1000:
        return "Bronze"
    elif elo < 1200:
        return "Silver"
    elif elo < 1400:
        return "Gold"
    elif elo < 1600:
        return "Platinum"
    else:
        return "Diamond"


def refresh_bot_status(bot: Dict[str, Any]):
    now = int(time.time())
    status = bot.get("status", "READY")
    recovery_ends_at = bot.get("recovery_ends_at")

    if status in ("KO", "RECOVERING") and recovery_ends_at is not None:
        if now >= recovery_ends_at:
            bot["status"] = "READY"
            bot["recovery_ends_at"] = None


def gain_xp(bot: Dict[str, Any], amount: int):
    if bot.get("type") != "battle":
        return

    xp = int(bot.get("xp", 0))
    level = int(bot.get("level", 1))

    xp += amount
    while xp >= level * 100:
        xp -= level * 100
        level += 1

    bot["xp"] = xp
    bot["level"] = level


# ============================
# CARD SYSTEM
# ============================

CARD_STYLES = [
    "neon_tech",
    "mecha_blueprint",
    "cosmic_core",
    "industrial_forged",
    "elemental_core",
    "holo_mythic",
    "corrupted_void",
    "prismatic_legendary",
]

# Base rarity tiers
RARITY_WEIGHTS = {
    "common": 60,
    "rare": 25,
    "epic": 10,
    "legendary": 4,
    "mythic": 1,
}

# Style weights by rarity (simple mapping)
STYLE_BY_RARITY = {
    "common": ["neon_tech", "industrial_forged", "mecha_blueprint"],
    "rare": ["cosmic_core", "elemental_core"],
    "epic": ["cosmic_core", "elemental_core", "industrial_forged"],
    "legendary": ["prismatic_legendary", "cosmic_core"],
    "mythic": ["holo_mythic", "corrupted_void"],
}

# Region → style bias
REGION_STYLE_BIAS = {
    "factory": ["industrial_forged", "mecha_blueprint"],
    "cosmic": ["cosmic_core", "prismatic_legendary"],
    "elemental": ["elemental_core"],
    "void": ["corrupted_void", "holo_mythic"],
}


def weighted_choice(weight_map: Dict[str, int]) -> str:
    total = sum(weight_map.values())
    r = random.uniform(0, total)
    upto = 0
    for key, w in weight_map.items():
        if upto + w >= r:
            return key
        upto += w
    # fallback
    return list(weight_map.keys())[0]


def pick_rarity() -> str:
    return weighted_choice(RARITY_WEIGHTS)


def pick_style_for_rarity_and_region(rarity: str, region: Optional[str]) -> str:
    base_styles = STYLE_BY_RARITY.get(rarity, ["neon_tech"])

    # Region bias: add region styles with extra weight
    region_styles = REGION_STYLE_BIAS.get(region or "", [])
    pool: Dict[str, int] = {}

    # Base styles
    for s in base_styles:
        pool[s] = pool.get(s, 0) + 5

    # Region styles get extra weight
    for s in region_styles:
        pool[s] = pool.get(s, 0) + 10

    # If pool somehow empty, fallback
    if not pool:
        pool = {s: 1 for s in base_styles}

    return weighted_choice(pool)


def auto_generate_card_metadata(role: Optional[str], region: Optional[str]) -> Dict[str, Any]:
    """
    For NPC/store bots: rarity + style + holo + basic URLs.
    For now, URLs are placeholders the UI can map to assets.
    """
    rarity = pick_rarity()
    style = pick_style_for_rarity_and_region(rarity, region)

    # Simple holo logic: only epic/legendary/mythic can be holo
    holo = rarity in ("epic", "legendary", "mythic") and (random.random() < 0.3)

    return {
        "card_style": style,
        "rarity": rarity,
        "holo": holo,
        "portrait_url": None,  # UI or a later service can fill this
        "frame_key": f"{style}_{rarity}",
        "vfx_pack": style,     # UI can map style → VFX pack
        "role": role or "npc",
        "region": region,
    }


def default_player_card_metadata(selected_style: Optional[str]) -> Dict[str, Any]:
    style = selected_style if selected_style in CARD_STYLES else "neon_tech"
    return {
        "card_style": style,
        "rarity": "common",
        "holo": False,
        "portrait_url": None,
        "frame_key": f"{style}_common",
        "vfx_pack": style,
        "role": "player",
        "region": None,
    }


# ============================
# ENDPOINT: LIST BOTS
# ============================
@router.get("/list")
def list_bots():
    for bot in BOT_REGISTRY.values():
        refresh_bot_status(bot)
    return list(BOT_REGISTRY.values())


# ============================
# ENDPOINT: GET BOT BY GIN
# ============================
@router.get("/get/{gin}")
def get_bot(gin: str):
    if gin not in BOT_REGISTRY:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot = BOT_REGISTRY[gin]
    refresh_bot_status(bot)
    return bot


# ============================
# ENDPOINT: LEADERBOARD
# ============================
@router.get("/leaderboard")
def leaderboard(limit: int = 50):
    bots = []
    for bot in BOT_REGISTRY.values():
        refresh_bot_status(bot)
        if bot.get("type") == "battle":
            bots.append(bot)

    bots.sort(key=lambda b: int(b.get("elo", 1000)), reverse=True)
    return bots[:limit]


# ============================
# ENDPOINT: MINT BOT (UPDATED)
# ============================
from gc_payments import GCPayments

gc = GCPayments()

@router.post("/mint")
def mint_bot(request: MintRequest):

    bot_type = request.type.lower()

    if bot_type not in ["battle", "trading", "evolution"]:
        raise HTTPException(status_code=400, detail="Invalid bot type")

    # ----------------------------
    # Simulated GC payment
    # ----------------------------
    # In the future, replace sender/receiver with real wallet addresses.
    txid = gc.transfer_gc(
        sender="user_wallet_placeholder",
        receiver="treasury_placeholder",
        amount=10  # or dynamic cost later
    )

    # ----------------------------
    # Bot creation logic
    # ----------------------------
    gin = generate_gin(bot_type)
    name = request.name if request.name else auto_name(bot_type)
    stats = generate_stats(bot_type)

    bot: Dict[str, Any] = {
        "gin": gin,
        "name": name,
        "type": bot_type,
        "stats": stats,
        "generation": 1,
        "lineage": [],
        "created_at": int(time.time()),
        "txid": txid,  # ⭐ NEW: return simulated txid
    }

    # Battle-specific progression
    if bot_type == "battle":
        bot["status"] = "READY"
        bot["recovery_ends_at"] = None
        bot["elo"] = 1000
        bot["league"] = get_league_for_elo(bot["elo"])
        bot["xp"] = 0
        bot["level"] = 1
        bot["wins"] = 0
        bot["losses"] = 0

    # Card metadata
    role = request.role or "player"
    region = request.region

    if role == "player":
        card_meta = default_player_card_metadata(request.card_style)
    else:
        card_meta = auto_generate_card_metadata(role, region)

    bot.update(card_meta)

    BOT_REGISTRY[gin] = bot
    return bot


# ============================
# ENDPOINT: UPDATE CARD STYLE (PLAYER OVERRIDE)
# ============================
@router.post("/card/update-style")
def update_card_style(payload: CardStyleUpdateRequest):
    gin = payload.gin
    if gin not in BOT_REGISTRY:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot = BOT_REGISTRY[gin]

    if bot.get("role") != "player":
        raise HTTPException(status_code=400, detail="Only player-owned bots can change card style.")

    if payload.card_style not in CARD_STYLES:
        raise HTTPException(status_code=400, detail="Invalid card style.")

    bot["card_style"] = payload.card_style
    bot["frame_key"] = f"{payload.card_style}_{bot.get('rarity', 'common')}"
    bot["vfx_pack"] = payload.card_style

    return bot