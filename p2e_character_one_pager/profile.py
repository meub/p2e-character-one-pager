"""Profile a character as caster, martial, or hybrid to control layout emphasis."""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import CharacterModel


@dataclass
class Profile:
    profile_type: str  # "caster" | "martial" | "hybrid"
    section_order: list[str] = field(default_factory=list)
    max_skills: int = 8
    max_feats: int | None = None
    max_spells_per_rank: int = 10


CASTER_SECTIONS = ["defense", "skills", "weapons", "spellcasting", "focus", "items"]
MARTIAL_SECTIONS = ["defense", "weapons", "skills", "items", "spellcasting", "focus"]
HYBRID_SECTIONS = ["defense", "weapons", "skills", "spellcasting", "focus", "items"]


def classify(char: CharacterModel, override: str | None = None) -> Profile:
    if override and override != "auto":
        profile_type = override
    else:
        profile_type = _auto_classify(char)

    if profile_type == "caster":
        sections = CASTER_SECTIONS
    elif profile_type == "martial":
        sections = MARTIAL_SECTIONS
    else:
        sections = HYBRID_SECTIONS

    return Profile(
        profile_type=profile_type,
        section_order=list(sections),
    )


def _auto_classify(char: CharacterModel) -> str:
    caster_score = 0
    for caster in char.spellcasters:
        if caster.innate:
            continue
        spell_count = sum(len(se.spells) for se in caster.spells)
        caster_score += spell_count
        slot_count = sum(s for s in caster.per_day if s > 0)
        caster_score += slot_count
        if caster.prepared:
            caster_score += 5

    martial_score = len(char.weapons) * 3
    if char.weapons:
        martial_score += max(w.attack for w in char.weapons)

    if caster_score >= 20 and martial_score < 15:
        return "caster"
    elif martial_score >= 15 and caster_score < 10:
        return "martial"
    elif caster_score >= 10:
        return "hybrid"
    else:
        return "martial"
