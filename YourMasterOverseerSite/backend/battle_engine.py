# battle_engine.py

from dataclasses import dataclass
from typing import List, Dict, Any
import random
import math
import time


# ---------- Core data structures ----------

@dataclass
class BotStats:
    attack: int
    defense: int
    speed: int
    accuracy: int
    evasion: int
    stamina: int
    luck: int


@dataclass
class Ability:
    name: str
    description: str
    energy_cost: int
    power: int          # base damage scaling
    accuracy_mod: int   # +/- to accuracy
    crit_bonus: int     # extra crit chance
    type: str           # "light", "heavy", "utility", "ultimate"


@dataclass
class PassiveTrait:
    name: str
    description: str


@dataclass
class CombatProfile:
    gin: str
    name: str
    stats: BotStats
    max_hp: int
    current_hp: int
    max_energy: int
    current_energy: int
    abilities: List[Ability]
    ultimate: Ability
    passive: PassiveTrait


@dataclass
class TurnLog:
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


@dataclass
class BattleResult:
    winner_gin: str
    winner_name: str
    loser_gin: str
    loser_name: str
    turns: List[TurnLog]
    total_turns: int
    ko_occurred: bool
    started_at: int
    ended_at: int


# ---------- HP & Energy formulas ----------

def compute_hp(stats: BotStats) -> int:
    # HP = defense * 2 + stamina * 3 + luck
    return stats.defense * 2 + stats.stamina * 3 + stats.luck


def compute_energy_max(stats: BotStats) -> int:
    # Energy = stamina * 2 (simple, scalable)
    return stats.stamina * 2


def energy_regen_per_turn(stats: BotStats) -> int:
    # Flat regen for now; can later scale with stamina or luck
    return 10


# ---------- Ability generation (auto, per bot) ----------

def generate_passive_for_bot(name: str, stats: BotStats) -> PassiveTrait:
    # Simple name + stat‑aware passive
    if stats.evasion > stats.defense:
        return PassiveTrait(
            name="Phantom Frame",
            description="High evasion: +10% effective evasion when HP is below 50%."
        )
    elif stats.defense > stats.speed:
        return PassiveTrait(
            name="Reinforced Alloy",
            description="High defense: reduces incoming damage by ~10%."
        )
    else:
        return PassiveTrait(
            name="Critical Matrix",
            description="High luck: +10% crit chance when HP is below 50%."
        )


def generate_core_abilities_for_bot(name: str, stats: BotStats) -> List[Ability]:
    base_name = name if len(name) <= 12 else name[:12]

    light = Ability(
        name=f"{base_name} Jab",
        description="A quick, low‑energy strike.",
        energy_cost=5,
        power=10,
        accuracy_mod=10,
        crit_bonus=0,
        type="light",
    )

    heavy = Ability(
        name=f"{base_name} Burst",
        description="A powerful, high‑energy attack.",
        energy_cost=15,
        power=22,
        accuracy_mod=-5,
        crit_bonus=5,
        type="heavy",
    )

    utility = Ability(
        name=f"{base_name} Veil",
        description="Utility move that slightly boosts evasion (simulated via accuracy penalty to enemy this turn).",
        energy_cost=10,
        power=0,
        accuracy_mod=0,
        crit_bonus=0,
        type="utility",
    )

    return [light, heavy, utility]


def generate_ultimate_for_bot(name: str, stats: BotStats) -> Ability:
    base_name = name if len(name) <= 10 else name[:10]
    return Ability(
        name=f"{base_name} Eclipse",
        description="Signature ultimate attack with high damage and crit chance.",
        energy_cost=30,
        power=40,
        accuracy_mod=0,
        crit_bonus=15,
        type="ultimate",
    )


# ---------- Overdrive & passive effects ----------

def is_overdrive_active(bot: CombatProfile) -> bool:
    return bot.current_hp <= bot.max_hp * 0.25


def apply_passive_damage_modifiers(
    bot: CombatProfile,
    incoming_damage: int,
) -> int:
    # Simple passive hooks
    if "Reinforced Alloy" in bot.passive.name:
        incoming_damage = math.floor(incoming_damage * 0.9)
    return max(incoming_damage, 0)


def apply_passive_evasion_bonus(
    bot: CombatProfile,
    effective_evasion: int,
) -> int:
    if "Phantom Frame" in bot.passive.name and bot.current_hp <= bot.max_hp * 0.5:
        effective_evasion += 10
    return effective_evasion


def apply_passive_crit_bonus(
    bot: CombatProfile,
    base_crit_chance: int,
) -> int:
    if "Critical Matrix" in bot.passive.name and bot.current_hp <= bot.max_hp * 0.5:
        base_crit_chance += 10
    return base_crit_chance


# ---------- Core battle logic ----------

def build_combat_profile(bot_data: Dict[str, Any]) -> CombatProfile:
    stats = BotStats(
        attack=bot_data["stats"]["attack"],
        defense=bot_data["stats"]["defense"],
        speed=bot_data["stats"]["speed"],
        accuracy=bot_data["stats"]["accuracy"],
        evasion=bot_data["stats"]["evasion"],
        stamina=bot_data["stats"]["stamina"],
        luck=bot_data["stats"]["luck"],
    )

    max_hp = compute_hp(stats)
    max_energy = compute_energy_max(stats)

    abilities = generate_core_abilities_for_bot(bot_data["name"], stats)
    ultimate = generate_ultimate_for_bot(bot_data["name"], stats)
    passive = generate_passive_for_bot(bot_data["name"], stats)

    return CombatProfile(
        gin=bot_data["gin"],
        name=bot_data["name"],
        stats=stats,
        max_hp=max_hp,
        current_hp=max_hp,
        max_energy=max_energy,
        current_energy=max_energy,
        abilities=abilities,
        ultimate=ultimate,
        passive=passive,
    )


def choose_ability_for_turn(bot: CombatProfile) -> Ability:
    """
    Simple AI:
    - If overdrive and enough energy: try ultimate
    - Else if enough energy for heavy: sometimes heavy
    - Else use light
    - Utility is not deeply modeled yet; can be expanded later
    """
    if is_overdrive_active(bot) and bot.current_energy >= bot.ultimate.energy_cost:
        return bot.ultimate

    heavy = next((a for a in bot.abilities if a.type == "heavy"), None)
    light = next((a for a in bot.abilities if a.type == "light"), None)

    if heavy and bot.current_energy >= heavy.energy_cost and random.random() < 0.5:
        return heavy

    if light and bot.current_energy >= light.energy_cost:
        return light

    # If no energy for anything, just "wait" (no ability)
    return None


def run_single_attack(
    attacker: CombatProfile,
    defender: CombatProfile,
    ability: Ability,
    turn_number: int,
) -> TurnLog:
    notes: List[str] = []

    energy_before = attacker.current_energy
    hp_before_target = defender.current_hp

    if ability is None:
        # No energy / skip
        regen = energy_regen_per_turn(attacker.stats)
        attacker.current_energy = min(attacker.max_energy, attacker.current_energy + regen)
        notes.append("No usable ability; attacker recovers energy.")
        return TurnLog(
            turn_number=turn_number,
            acting_gin=attacker.gin,
            acting_name=attacker.name,
            target_gin=defender.gin,
            target_name=defender.name,
            ability_used="None",
            damage_dealt=0,
            crit=False,
            hit=False,
            energy_before=energy_before,
            energy_after=attacker.current_energy,
            hp_before_target=hp_before_target,
            hp_after_target=defender.current_hp,
            notes=notes,
        )

    # Pay energy cost
    attacker.current_energy -= ability.energy_cost
    if attacker.current_energy < 0:
        attacker.current_energy = 0

    # Base accuracy & evasion
    base_accuracy = attacker.stats.accuracy + ability.accuracy_mod
    base_evasion = defender.stats.evasion

    # Passive evasion bonus
    base_evasion = apply_passive_evasion_bonus(defender, base_evasion)

    # Hit chance
    hit_chance = max(10, min(95, base_accuracy - base_evasion + 50))
    roll = random.randint(1, 100)

    if roll > hit_chance:
        # Miss
        notes.append(f"Attack missed (roll {roll} > hit chance {hit_chance}).")
        # Regen some energy even on miss
        attacker.current_energy = min(
            attacker.max_energy,
            attacker.current_energy + energy_regen_per_turn(attacker.stats) // 2,
        )
        return TurnLog(
            turn_number=turn_number,
            acting_gin=attacker.gin,
            acting_name=attacker.name,
            target_gin=defender.gin,
            target_name=defender.name,
            ability_used=ability.name,
            damage_dealt=0,
            crit=False,
            hit=False,
            energy_before=energy_before,
            energy_after=attacker.current_energy,
            hp_before_target=hp_before_target,
            hp_after_target=defender.current_hp,
            notes=notes,
        )

    # Hit: compute damage
    base_damage = ability.power + attacker.stats.attack - defender.stats.defense
    base_damage = max(base_damage, 1)

    # Crit chance
    crit_chance = 5 + attacker.stats.luck // 10 + ability.crit_bonus
    crit_chance = apply_passive_crit_bonus(attacker, crit_chance)
    crit_roll = random.randint(1, 100)
    crit = crit_roll <= crit_chance
    if crit:
        base_damage = math.floor(base_damage * 1.5)
        notes.append(f"Critical hit! (roll {crit_roll} <= crit chance {crit_chance}).")

    # Overdrive bonus
    if is_overdrive_active(attacker):
        base_damage = math.floor(base_damage * 1.2)
        notes.append("Overdrive active: damage boosted.")

    # Apply defender passive
    final_damage = apply_passive_damage_modifiers(defender, base_damage)

    defender.current_hp = max(defender.current_hp - final_damage, 0)

    # Energy regen after attack
    attacker.current_energy = min(
        attacker.max_energy,
        attacker.current_energy + energy_regen_per_turn(attacker.stats),
    )

    return TurnLog(
        turn_number=turn_number,
        acting_gin=attacker.gin,
        acting_name=attacker.name,
        target_gin=defender.gin,
        target_name=defender.name,
        ability_used=ability.name,
        damage_dealt=final_damage,
        crit=crit,
        hit=True,
        energy_before=energy_before,
        energy_after=attacker.current_energy,
        hp_before_target=hp_before_target,
        hp_after_target=defender.current_hp,
        notes=notes,
    )


def run_battle(bot1_data: Dict[str, Any], bot2_data: Dict[str, Any]) -> BattleResult:
    """
    Turn‑based, unlimited rounds until one bot hits 0 HP.
    No persistence changes here — KO/recovery wiring can be added later.
    """
    random.seed()  # ensure randomness per battle

    started_at = int(time.time())

    bot1 = build_combat_profile(bot1_data)
    bot2 = build_combat_profile(bot2_data)

    turns: List[TurnLog] = []
    turn_number = 1

    # Determine initial order by speed
    if bot2.stats.speed > bot1.stats.speed:
        attacker, defender = bot2, bot1
    else:
        attacker, defender = bot1, bot2

    while bot1.current_hp > 0 and bot2.current_hp > 0:
        # Attacker's turn
        ability = choose_ability_for_turn(attacker)
        log = run_single_attack(attacker, defender, ability, turn_number)
        turns.append(log)
        if defender.current_hp <= 0:
            break

        turn_number += 1

        # Swap roles
        attacker, defender = defender, attacker

    ended_at = int(time.time())

    if bot1.current_hp > 0:
        winner, loser = bot1, bot2
    else:
        winner, loser = bot2, bot1

    return BattleResult(
        winner_gin=winner.gin,
        winner_name=winner.name,
        loser_gin=loser.gin,
        loser_name=loser.name,
        turns=turns,
        total_turns=len(turns),
        ko_occurred=True,
        started_at=started_at,
        ended_at=ended_at,
    )
