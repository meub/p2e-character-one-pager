"""Normalized data model for a PF2e character."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Identity(BaseModel):
    name: str = "Unknown"
    level: int = 1
    char_class: str = "Unknown"
    ancestry: str = "Unknown"
    heritage: str = ""
    background: str = ""
    alignment: str = ""
    gender: str = ""
    age: str = ""
    deity: str = ""
    size: str = "Medium"
    languages: list[str] = Field(default_factory=list)


class Ability(BaseModel):
    name: str
    score: int
    modifier: int


class Abilities(BaseModel):
    str_: Ability = Field(alias="str")
    dex: Ability
    con: Ability
    int_: Ability = Field(alias="int")
    wis: Ability
    cha: Ability

    model_config = {"populate_by_name": True}

    def as_list(self) -> list[Ability]:
        return [self.str_, self.dex, self.con, self.int_, self.wis, self.cha]


class Defense(BaseModel):
    ac: int = 10
    hp: int = 0
    fortitude: int = 0
    fort_prof: int = 0
    reflex: int = 0
    reflex_prof: int = 0
    will: int = 0
    will_prof: int = 0
    perception: int = 0
    perception_prof: int = 0
    resistances: list[str] = Field(default_factory=list)


class Mobility(BaseModel):
    speed: int = 25


class Skill(BaseModel):
    name: str
    modifier: int
    prof_rank: int = 0  # 0=untrained,2=T,4=E,6=M,8=L


class Feat(BaseModel):
    name: str
    feat_type: str = ""  # class, skill, general, ancestry, archetype, heritage
    level: int = 0
    source: str = ""


class Weapon(BaseModel):
    name: str
    display: str = ""
    attack: int = 0
    damage_dice: str = ""
    damage_bonus: int = 0
    damage_type: str = ""
    traits: list[str] = Field(default_factory=list)
    material: str = ""


class ItemEntry(BaseModel):
    name: str
    qty: int = 1
    invested: bool = False


class Money(BaseModel):
    cp: int = 0
    sp: int = 0
    gp: int = 0
    pp: int = 0

    def display(self) -> str:
        parts = []
        if self.pp:
            parts.append(f"{self.pp} pp")
        if self.gp:
            parts.append(f"{self.gp} gp")
        if self.sp:
            parts.append(f"{self.sp} sp")
        if self.cp:
            parts.append(f"{self.cp} cp")
        return ", ".join(parts) if parts else "0 gp"


class SpellEntry(BaseModel):
    spell_level: int
    spells: list[str] = Field(default_factory=list)


class CasterModel(BaseModel):
    name: str
    tradition: str = ""
    casting_type: str = ""  # prepared, spontaneous
    ability: str = ""
    proficiency: int = 0
    spell_dc: int = 0
    spell_attack: int = 0
    focus_points: int = 0
    innate: bool = False
    per_day: list[int] = Field(default_factory=list)
    spells: list[SpellEntry] = Field(default_factory=list)
    prepared: list[SpellEntry] = Field(default_factory=list)


class FocusSpell(BaseModel):
    name: str
    tradition: str = ""


class CharacterModel(BaseModel):
    identity: Identity = Field(default_factory=Identity)
    abilities: Abilities | None = None
    defense: Defense = Field(default_factory=Defense)
    mobility: Mobility = Field(default_factory=Mobility)
    skills: list[Skill] = Field(default_factory=list)
    lores: list[Skill] = Field(default_factory=list)
    feats: list[Feat] = Field(default_factory=list)
    specials: list[str] = Field(default_factory=list)
    weapons: list[Weapon] = Field(default_factory=list)
    items: list[ItemEntry] = Field(default_factory=list)
    money: Money = Field(default_factory=Money)
    spellcasters: list[CasterModel] = Field(default_factory=list)
    focus_points: int = 0
    focus_spells: list[FocusSpell] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
