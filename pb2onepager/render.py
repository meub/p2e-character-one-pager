"""Render CharacterModel + Profile into a single-page HTML file."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .model import CharacterModel
from .parse import PROF_LABEL
from .profile import Profile
from .spells import SPELL_DESCRIPTIONS

ASSETS_DIR = Path(__file__).parent / "assets"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Class features that are implied by the class/heritage and don't need to be shown
IMPLIED_SPECIALS = {
    "Wizard Spellcasting",
    "Spellbook",
    "Expert Spellcaster",
    "Reflex Expertise",
    "Lightning Reflexes",
    "Weapon Specialization",
    "Great Fortitude",
    "Resolve",
    "Alertness",
    "General Training",
    "Skill Training",
}


def _filter_specials(specials: list[str], heritage: str) -> list[str]:
    """Remove implied/redundant class features."""
    filtered = []
    for s in specials:
        if s in IMPLIED_SPECIALS:
            continue
        # Heritage is already shown in the subtitle
        if s == heritage:
            continue
        # Proficiency bumps like "Expert Foo" or "Master Foo" are shown in numbers
        lower = s.lower()
        if any(lower.startswith(p) for p in ("expert ", "master ", "legendary ")) and \
           any(w in lower for w in ("spellcaster", "reflex", "fortitude", "will", "perception")):
            continue
        filtered.append(s)
    return filtered


FEAT_GROUP_ORDER = [
    ("class", "Class Feats"),
    ("archetype", "Archetype Feats"),
    ("ancestry", "Ancestry Feats"),
    ("heritage", "Heritage"),
    ("skill", "Skill Feats"),
    ("general", "General Feats"),
    ("awarded", "Awarded Feats"),
]


def _load_css(filename: str) -> str:
    path = ASSETS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _fmt_mod(value: int) -> str:
    return f"+{value}" if value >= 0 else str(value)


def _fmt_bonus(value: int) -> str:
    if value > 0:
        return f"+{value}"
    elif value < 0:
        return str(value)
    return ""


def _prof_label(rank: int) -> str:
    return PROF_LABEL.get(rank, "")


def _group_feats(char: CharacterModel) -> OrderedDict[str, list]:
    groups: OrderedDict[str, list] = OrderedDict()
    for key, label in FEAT_GROUP_ORDER:
        matching = [f for f in char.feats if f.feat_type == key]
        if matching:
            groups[label] = matching
    # Catch any uncategorized
    known_types = {k for k, _ in FEAT_GROUP_ORDER}
    other = [f for f in char.feats if f.feat_type not in known_types]
    if other:
        groups["Other"] = other
    return groups


def render(
    char: CharacterModel,
    profile: Profile,
    page_size: str = "letter",
    theme: str = "default",
    font_source: str = "google",
    max_skills: int = 8,
    include_prepared: bool = True,
    include_known: bool = False,
) -> str:
    base_css = _load_css("base.css")
    print_css = _load_css("print.css")
    theme_css = _load_css(f"themes/{theme}.css")

    if page_size == "a4":
        print_css = print_css.replace("size: letter;", "size: A4;")

    # Select top skills by modifier (trained+ only, then fill with best untrained)
    trained = [s for s in char.skills if s.prof_rank > 0]
    trained.sort(key=lambda s: (-s.modifier, s.name))
    lores = sorted(char.lores, key=lambda s: (-s.modifier, s.name))
    display_skills = trained + lores
    if len(display_skills) < max_skills:
        untrained = sorted(
            [s for s in char.skills if s.prof_rank == 0],
            key=lambda s: (-s.modifier, s.name),
        )
        display_skills.extend(untrained[: max_skills - len(display_skills)])

    grouped_feats = _group_feats(char)
    key_features = _filter_specials(char.specials, char.identity.heritage)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("onepager.html.j2")

    html = template.render(
        char=char,
        profile=profile,
        base_css=base_css,
        print_css=print_css,
        theme_css=theme_css,
        font_source=font_source,
        display_skills=display_skills,
        grouped_feats=grouped_feats,
        include_prepared=include_prepared,
        include_known=include_known,
        key_features=key_features,
        spell_desc=SPELL_DESCRIPTIONS,
        fmt_mod=_fmt_mod,
        fmt_bonus=_fmt_bonus,
        prof_label=_prof_label,
    )
    return html
