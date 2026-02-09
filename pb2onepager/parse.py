"""Parse Pathbuilder 2e JSON into CharacterModel."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .model import (
    Abilities,
    Ability,
    CasterModel,
    CharacterModel,
    Defense,
    Feat,
    FocusSpell,
    Identity,
    ItemEntry,
    Mobility,
    Money,
    Skill,
    SpellEntry,
    Weapon,
)

PROF_LABEL = {0: "U", 2: "T", 4: "E", 6: "M", 8: "L"}

SKILL_NAMES = [
    "acrobatics", "arcana", "athletics", "crafting", "deception",
    "diplomacy", "intimidation", "medicine", "nature", "occultism",
    "performance", "religion", "society", "stealth", "survival", "thievery",
]

ABILITY_FOR_SKILL: dict[str, str] = {
    "acrobatics": "dex", "arcana": "int", "athletics": "str",
    "crafting": "int", "deception": "cha", "diplomacy": "cha",
    "intimidation": "cha", "medicine": "wis", "nature": "wis",
    "occultism": "int", "performance": "cha", "religion": "wis",
    "society": "int", "stealth": "dex", "survival": "wis",
    "thievery": "dex",
}

FEAT_TYPE_MAP = {
    "Class Feat": "class",
    "Skill Feat": "skill",
    "General Feat": "general",
    "Ancestry Feat": "ancestry",
    "Archetype Feat": "archetype",
    "Heritage": "heritage",
    "Awarded Feat": "awarded",
}


def _mod(score: int) -> int:
    return math.floor((score - 10) / 2)


def _get(d: dict, *keys: str, default: Any = None) -> Any:
    for k in keys:
        if d is None:
            return default
        d = d.get(k, None)  # type: ignore[assignment]
    if d is None:
        return default
    return d


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "build" in data:
        return data["build"]
    return data


def parse_identity(b: dict) -> Identity:
    return Identity(
        name=b.get("name", "Unknown"),
        level=b.get("level", 1),
        char_class=b.get("class", "Unknown"),
        ancestry=b.get("ancestry", "Unknown"),
        heritage=b.get("heritage", ""),
        background=b.get("background", ""),
        alignment=b.get("alignment", ""),
        gender=b.get("gender", ""),
        age=str(b.get("age", "")),
        deity=b.get("deity", ""),
        size=b.get("sizeName", "Medium"),
        languages=b.get("languages", []),
    )


def parse_abilities(b: dict) -> Abilities:
    ab = b.get("abilities", {})
    def _a(key: str, label: str) -> Ability:
        score = ab.get(key, 10)
        return Ability(name=label, score=score, modifier=_mod(score))

    return Abilities(**{
        "str": _a("str", "STR"),
        "dex": _a("dex", "DEX"),
        "con": _a("con", "CON"),
        "int": _a("int", "INT"),
        "wis": _a("wis", "WIS"),
        "cha": _a("cha", "CHA"),
    })


def _prof_bonus(level: int, prof_rank: int) -> int:
    if prof_rank == 0:
        return 0
    return level + prof_rank


def _save_mod(level: int, prof_rank: int, ability_mod: int) -> int:
    return _prof_bonus(level, prof_rank) + ability_mod


def parse_defense(b: dict, abilities: Abilities) -> Defense:
    level = b.get("level", 1)
    profs = b.get("proficiencies", {})

    ac_total = _get(b, "acTotal", "acTotal", default=10)

    con_mod = abilities.con.modifier
    attrs = b.get("attributes", {})
    ancestry_hp = attrs.get("ancestryhp", 0)
    class_hp = attrs.get("classhp", 0)
    bonus_hp = attrs.get("bonushp", 0)
    bonus_hp_per_level = attrs.get("bonushpPerLevel", 0)

    # Check for Toughness feat
    has_toughness = any(
        f[0] == "Toughness" for f in b.get("feats", []) if isinstance(f, (list, tuple)) and len(f) > 0
    )
    toughness_hp = level if has_toughness else 0

    hp = ancestry_hp + (class_hp + con_mod + bonus_hp_per_level) * level + bonus_hp + toughness_hp

    fort_prof = profs.get("fortitude", 0)
    ref_prof = profs.get("reflex", 0)
    will_prof = profs.get("will", 0)
    perc_prof = profs.get("perception", 0)

    return Defense(
        ac=ac_total,
        hp=hp,
        fortitude=_save_mod(level, fort_prof, con_mod),
        fort_prof=fort_prof,
        reflex=_save_mod(level, ref_prof, abilities.dex.modifier),
        reflex_prof=ref_prof,
        will=_save_mod(level, will_prof, abilities.wis.modifier),
        will_prof=will_prof,
        perception=_save_mod(level, perc_prof, abilities.wis.modifier),
        perception_prof=perc_prof,
        resistances=b.get("resistances", []),
    )


def parse_skills(b: dict, abilities: Abilities) -> list[Skill]:
    level = b.get("level", 1)
    profs = b.get("proficiencies", {})
    skills: list[Skill] = []

    for skill_name in SKILL_NAMES:
        prof_rank = profs.get(skill_name, 0)
        ability_key = ABILITY_FOR_SKILL.get(skill_name, "dex")
        attr = ability_key
        if attr == "str":
            attr = "str_"
        elif attr == "int":
            attr = "int_"
        ability_mod = getattr(abilities, attr).modifier
        mod = _prof_bonus(level, prof_rank) + ability_mod
        skills.append(Skill(
            name=skill_name.capitalize(),
            modifier=mod,
            prof_rank=prof_rank,
        ))

    return skills


def parse_lores(b: dict, abilities: Abilities) -> list[Skill]:
    level = b.get("level", 1)
    lores = b.get("lores", [])
    result: list[Skill] = []
    int_mod = abilities.int_.modifier
    for lore in lores:
        if isinstance(lore, (list, tuple)) and len(lore) >= 2:
            name, rank = lore[0], lore[1]
            mod = _prof_bonus(level, rank) + int_mod
            result.append(Skill(name=f"{name} Lore", modifier=mod, prof_rank=rank))
    return result


def parse_feats(b: dict) -> list[Feat]:
    raw_feats = b.get("feats", [])
    feats: list[Feat] = []
    for f in raw_feats:
        if not isinstance(f, (list, tuple)) or len(f) < 4:
            continue
        name = f[0]
        sub_choice = f[1]
        raw_type = f[2]
        feat_level = f[3] if isinstance(f[3], int) else 0
        feat_type = FEAT_TYPE_MAP.get(raw_type, raw_type)
        display_name = f"{name} ({sub_choice})" if sub_choice else name
        feats.append(Feat(
            name=display_name,
            feat_type=feat_type,
            level=feat_level,
        ))
    return feats


def parse_weapons(b: dict) -> list[Weapon]:
    raw = b.get("weapons", [])
    weapons: list[Weapon] = []
    for w in raw:
        die = w.get("die", "d4")
        striking = w.get("str", "")
        if striking == "striking":
            dice_count = 2
        elif striking == "greaterStriking":
            dice_count = 3
        elif striking == "majorStriking":
            dice_count = 4
        else:
            dice_count = 1
        damage_dice = f"{dice_count}{die}"

        weapons.append(Weapon(
            name=w.get("name", "Unknown"),
            display=w.get("display", w.get("name", "Unknown")),
            attack=w.get("attack", 0),
            damage_dice=damage_dice,
            damage_bonus=w.get("damageBonus", 0),
            damage_type=w.get("damageType", ""),
            material=w.get("mat", ""),
        ))
    return weapons


def parse_items(b: dict) -> tuple[list[ItemEntry], Money]:
    raw = b.get("equipment", [])
    items: list[ItemEntry] = []
    for entry in raw:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            name = entry[0]
            qty = entry[1] if isinstance(entry[1], int) else 1
            invested = len(entry) >= 3 and entry[2] == "Invested"
            items.append(ItemEntry(name=name, qty=qty, invested=invested))

    raw_money = b.get("money", {})
    money = Money(
        cp=raw_money.get("cp", 0),
        sp=raw_money.get("sp", 0),
        gp=raw_money.get("gp", 0),
        pp=raw_money.get("pp", 0),
    )
    return items, money


def parse_spellcasters(b: dict, abilities: Abilities) -> list[CasterModel]:
    level = b.get("level", 1)
    raw_casters = b.get("spellCasters", [])
    casters: list[CasterModel] = []

    for rc in raw_casters:
        ability_key = rc.get("ability", "int")
        if ability_key == "str":
            ability_mod = abilities.str_.modifier
        elif ability_key == "int":
            ability_mod = abilities.int_.modifier
        else:
            ability_mod = getattr(abilities, ability_key, abilities.int_).modifier
        prof = rc.get("proficiency", 0)
        prof_bonus = _prof_bonus(level, prof)
        spell_dc = 10 + prof_bonus + ability_mod
        spell_attack = prof_bonus + ability_mod

        spells: list[SpellEntry] = []
        for s in rc.get("spells", []):
            spells.append(SpellEntry(
                spell_level=s.get("spellLevel", 0),
                spells=s.get("list", []),
            ))
        spells.sort(key=lambda x: x.spell_level)

        prepared: list[SpellEntry] = []
        for p in rc.get("prepared", []):
            prepared.append(SpellEntry(
                spell_level=p.get("spellLevel", 0),
                spells=p.get("list", []),
            ))
        prepared.sort(key=lambda x: x.spell_level)

        casters.append(CasterModel(
            name=rc.get("name", "Unknown"),
            tradition=rc.get("magicTradition", ""),
            casting_type=rc.get("spellcastingType", ""),
            ability=ability_key.upper(),
            proficiency=prof,
            spell_dc=spell_dc,
            spell_attack=spell_attack,
            focus_points=rc.get("focusPoints", 0),
            innate=rc.get("innate", False),
            per_day=rc.get("perDay", []),
            spells=spells,
            prepared=prepared,
        ))

    return casters


def parse_focus(b: dict) -> tuple[int, list[FocusSpell]]:
    focus_points = b.get("focusPoints", 0)
    focus_data = b.get("focus", {})
    spells: list[FocusSpell] = []

    for tradition, abilities_dict in focus_data.items():
        if not isinstance(abilities_dict, dict):
            continue
        for _ability_key, details in abilities_dict.items():
            if not isinstance(details, dict):
                continue
            for spell_name in details.get("focusSpells", []):
                spells.append(FocusSpell(name=spell_name, tradition=tradition))
            for spell_name in details.get("focusCantrips", []):
                spells.append(FocusSpell(name=spell_name, tradition=tradition))

    return focus_points, spells


def parse_specials(b: dict) -> list[str]:
    return b.get("specials", [])


def parse(path: str | Path) -> CharacterModel:
    b = load_json(path)

    identity = parse_identity(b)
    abilities = parse_abilities(b)
    defense = parse_defense(b, abilities)
    skills = parse_skills(b, abilities)
    lores = parse_lores(b, abilities)
    feats = parse_feats(b)
    weapons = parse_weapons(b)
    items, money = parse_items(b)
    spellcasters = parse_spellcasters(b, abilities)
    focus_points, focus_spells = parse_focus(b)
    specials = parse_specials(b)

    speed = b.get("attributes", {}).get("speed", 25)
    speed_bonus = b.get("attributes", {}).get("speedBonus", 0)

    return CharacterModel(
        identity=identity,
        abilities=abilities,
        defense=defense,
        mobility=Mobility(speed=speed + speed_bonus),
        skills=skills,
        lores=lores,
        feats=feats,
        specials=specials,
        weapons=weapons,
        items=items,
        money=money,
        spellcasters=spellcasters,
        focus_points=focus_points,
        focus_spells=focus_spells,
    )
