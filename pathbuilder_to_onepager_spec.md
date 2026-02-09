# Pathbuilder 2e → One‑Pager HTML Generator (Python) — Product + Technical Spec

## 1) Product spec

### 1.1 Goal
Create a command-line Python script that ingests a **Pathbuilder 2e JSON export** and outputs a **single-page HTML character one-pager** optimized for:
- quick at-table reference
- printing to a single page (Letter by default)
- dense but readable presentation in two columns
- “smart” section emphasis based on the character (caster vs martial, etc.)

### 1.2 Target users
- PF2e players who maintain their character in Pathbuilder
- GMs who want quick references for NPCs/PCs
- Players who want a printable / shareable “cheat sheet” style summary

### 1.3 Success criteria
- Output renders as a **single page** in print preview for typical characters (levels 1–12) without manual edits in most cases.
- Two-column layout remains readable on screen and prints cleanly.
- Key numbers (AC/HP/saves/perception/speed, spell DC, attack modifiers) are prominent and easy to scan.
- Layout adapts for common archetypes (caster, martial, mixed), prioritizing the sections that matter.

### 1.4 Non-goals
- Full rules text embedding for feats/spells/items (too verbose & licensing concerns)
- Multi-page sheets (intentionally constrained)
- Live/interactive character sheet app (static output only)

### 1.5 Inputs / outputs
**Input**
- Pathbuilder JSON export file (`.json`) from Pathbuilder 2e.

**Output**
- `character_name_onepager.html` (single file)
  - Uses Alegreya (import via Google Fonts by default)
  - Optional “self-contained” mode that embeds CSS and optionally inlines fonts (advanced)

### 1.6 Primary user flow
1. User exports character JSON from Pathbuilder
2. User runs:
   ```bash
   pb2onepager build coren.json --out coren.html
   ```
3. Opens HTML in browser or prints to PDF

### 1.7 Layout requirements
- **Two columns** for the main body (CSS columns or grid-based)
- Fixed **header** at top (name, level/class, key stats)
- Section blocks with compact typography and clear hierarchy:
  - Header: very large name
  - Subheader: class/level/ancestry/background
  - Stat bar: AC/HP/Perception/Speed + saves + spell DC/attack where relevant
- Print styles:
  - `@page` size Letter (default) with margin controls
  - Avoid column breaks inside section blocks where possible

### 1.8 Adaptive “character type” rules
The generator should choose a **profile** based on JSON content, not manual user configuration:

**Caster-heavy profile** (example: Wizard, Cleric, Druid, etc.)  
Triggered when:
- One or more `spellCasters` present with meaningful slots/spells, OR
- Spell list length above threshold

Emphasize:
- Spellcasting summary (DC/attack, tradition, prepared/per-day)
- Cantrips / focus spells
- Prepared list (if present) prioritized over “known” list
- Wands/staves highlighted in items

**Martial-heavy profile**  
Triggered when:
- Multiple weapons, strong attack bonuses, or no spellcasting

Emphasize:
- Attacks block
- Key actions/abilities/feats
- Defensive stats, resistances, mobility
- Consumables & utility items

**Hybrid profile**  
Triggered when both are significant (e.g., Magus, Warpriest, caster archetype)  
Balanced emphasis:
- Smaller spell section + strong combat block

### 1.9 Content requirements (minimum)
- Identity: name, level, class, ancestry/heritage, background, alignment (if present)
- Abilities: STR/DEX/CON/INT/WIS/CHA (score + modifier)
- Core combat: AC, HP, Speed, Perception, Saves
- Skills: top N by modifier (configurable; default 8)
- Feats/features: a compact list grouped by type (class/skill/general/ancestry/archetype) with levels
- Items: invested + key combat/utility items; money
- Spells: per caster/tradition with rich caster summary if caster-heavy

### 1.10 Config options (CLI flags)
- `--page-size letter|a4` (default letter)
- `--theme default|dark|minimal` (default default)
- `--profile auto|caster|martial|hybrid` (default auto)
- `--skills 8` number of skills shown
- `--feats 10` cap or “auto”
- `--include-prepared true|false` (default true)
- `--include-known true|false` (default false unless no prepared list)
- `--font-source google|local|none` (default google)
- `--debug` dumps derived computed fields to a JSON beside the output

---

## 2) Technical spec

### 2.1 High-level architecture
A small Python package with:
- **Parser / Normalizer**: loads Pathbuilder JSON and produces a normalized internal model (`CharacterModel`)
- **Profiler**: determines layout/content emphasis (caster/martial/hybrid)
- **Renderer**: uses a template engine (Jinja2 recommended) to produce HTML + CSS
- **Post-processor**: ensures print CSS is set; optional minification

**Recommended stack**
- Python 3.11+
- `pydantic` (optional but nice for validation)
- `jinja2` for templating
- `click` or `typer` for CLI

### 2.2 Repository layout
```
pb2onepager/
  __init__.py
  cli.py
  parse.py
  model.py
  profile.py
  render.py
  assets/
    base.css
    print.css
    themes/
      default.css
      dark.css
  templates/
    onepager.html.j2
tests/
  test_parse.py
  test_render.py
```

### 2.3 Data model (normalized)
Create a `CharacterModel` with fields that are consistent even if Pathbuilder JSON varies by class/archetype.

Core:
- `identity`: name, level, class, ancestry, heritage, background, alignment, languages
- `abilities`: scores + modifiers
- `defense`: ac, hp, saves, perception
- `mobility`: speed
- `skills`: list of (name, mod, profRank)
- `feats`: list of (name, type, level, source)
- `weapons`: list of (name, attack, damageDice, damageBonus, traits/material)
- `items`: invested, other, money
- `spellcasting`: list of `CasterModel` entries
- `focus`: focus points, focus spells
- `notes`: derived notes (e.g., “Arcane Thesis”, “Arcane School”)

**Why normalize?**  
Pathbuilder exports can have optional fields and different shapes; normalization isolates templates from churn.

### 2.4 Parsing logic details
- Input JSON seems to match a `build` structure.
- Use defensive parsing:
  - missing fields should not crash rendering; show “—”
- Compute ability modifiers:
  - `mod = floor((score - 10)/2)` (integer division)
- HP:
  - Prefer a direct HP field if present in some exports (if not, compute from ancestryhp/classhp/level/con + bonus hp/level + toughness, etc.)
  - Keep both `hp_reported` (if present) and `hp_calculated` so templates can show calculated when missing.

### 2.5 Profiler rules
Produce a `Profile` object with:
- `profile_type`: caster|martial|hybrid
- `section_weights`: e.g. `{"spells": 1.3, "weapons": 0.8}`
- `caps`: e.g. `max_spells_per_rank`, `max_items`, `max_feats`
- `section_order`: list of sections in priority

Suggested heuristics:
- `caster_score = sum(len(caster.spells) for each caster)` + presence of `prepared` + nonzero `perDay` slots
- `martial_score = len(weapons) * 2 + max_attack_bonus + armor_presence`
- classify based on ratio and thresholds

### 2.6 Rendering (HTML template)
Use one main template `onepager.html.j2` with blocks:
- Header
- Left column sections
- Right column sections

**Two-column layout approach**  
Prefer CSS Grid to avoid weird column-breaking:
- A wrapper with `display: grid; grid-template-columns: 1fr 1fr; gap: 16px;`
- Each column contains stacked “cards”
- In print, keep grid; ensure it fits page width

**Page sizing**
- Print styles:
  ```css
  @page { size: letter; margin: 0.35in; }
  html, body { height: 100%; }
  ```
- Use `break-inside: avoid;` on section cards.

**Typography**
- Alegreya imported in `<head>`:
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Alegreya:wght@400;600;700&display=swap" rel="stylesheet">
  ```
- Use a compact scale:
  - Name: 28–34px
  - Section headers: ~12–14px with small-caps styling
  - Body: 10–11px

### 2.7 Spell rendering requirements (caster profile)
For each caster (Wizard/Cleric/etc.), display:
- Tradition, ability, proficiency rank (if available), spell attack mod, spell DC
- Slots per rank (from `perDay`)
- Prepared spells by rank (if `prepared` present)
- Known/available spell list separately but compact (optional toggle)
- Cantrips grouped
- Focus spells and focus points (if present)

Wizard-specific emphasis:
- Show thesis, school, bonded item, focus spells prominently if available
- For prepared list, show up to N spells per rank; overflow collapsed into “+X more” line

### 2.8 Items rendering requirements
- Grouping:
  1) Invested items
  2) Worn/held (if available)
  3) Consumables (potions, scrolls, etc.) if detectable by name or tag
- Money line compact: `14 gp, 8 sp`
- Weapons block includes attack + damage summary lines

### 2.9 Safety and robustness
- Fail gracefully:
  - If JSON parsing fails: clear error message with file path
  - If sections are empty: hide them
- Deterministic output: same JSON => same HTML
- No network calls besides optional Google Fonts import (can be disabled)

### 2.10 Testing strategy
- Unit tests:
  - Parse ability modifiers, AC block, spellcasting summary
  - Profiler classification (caster vs martial vs hybrid)
  - Render smoke test: output contains required sections
- Golden file tests:
  - Store sample JSONs and compare normalized output JSON snapshots

### 2.11 Performance
- Target runtime: < 200ms typical
- No heavy dependencies; all local rendering

---

## 3) Acceptance criteria checklist
- [ ] Running CLI against a Pathbuilder JSON creates a valid HTML file
- [ ] HTML uses Alegreya and prints cleanly to one page
- [ ] Two-column layout maintained in print and screen
- [ ] Caster-heavy characters show expanded spell info (DC/attack, slots, prepared by rank)
- [ ] Martial-heavy characters prioritize attacks/defenses/feats
- [ ] Hybrid characters show balanced sections
- [ ] Empty sections are omitted automatically
- [ ] Optional flags work (`--page-size`, `--profile`, caps)
