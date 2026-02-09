# pb2onepager

A CLI tool that converts [Pathbuilder 2e](https://pathbuilder2e.com/) character exports into single-page HTML character sheets, optimized for printing and quick table reference.

## Installation

Requires Python 3.11+.

```bash
pip install -e .
```

## Usage

Export your character from Pathbuilder 2e as JSON, then run:

```bash
pb2onepager build character.json
```

This produces `character_onepager.html` — a self-contained HTML file you can open in any browser or print to PDF.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o, --out` | `{name}_onepager.html` | Output file path |
| `--page-size` | `letter` | Page format: `letter` or `a4` |
| `--theme` | `default` | Visual theme: `default` (light) or `dark` |
| `--profile` | `auto` | Layout emphasis: `auto`, `caster`, `martial`, or `hybrid` |
| `--skills` | `8` | Number of skills to display |
| `--include-prepared / --no-include-prepared` | `true` | Show prepared spell lists |
| `--include-known / --no-include-known` | `false` | Show all known/available spells |
| `--font-source` | `google` | Font loading: `google` (Alegreya via Google Fonts) or `none` |
| `--debug` | off | Also output a `.debug.json` with the normalized character model |

### Examples

```bash
# Basic usage
pb2onepager build wizard.json

# Dark theme, A4 paper
pb2onepager build wizard.json --theme dark --page-size a4

# Force caster layout, show 12 skills
pb2onepager build wizard.json --profile caster --skills 12

# Custom output path
pb2onepager build wizard.json -o sheets/my_wizard.html
```

## How It Works

1. **Parse** — Reads the Pathbuilder JSON export and normalizes it into a structured character model (ability modifiers, proficiency bonuses, save totals, skill modifiers, spell DCs, weapon attack/damage).

2. **Profile** — Auto-detects whether the character is a caster, martial, or hybrid based on spell counts and weapon stats. This determines which sections appear first in the layout so the most relevant information is "above the fold."

3. **Render** — Feeds the character data into a Jinja2 template with embedded CSS. The output is a single self-contained HTML file with no external dependencies (aside from an optional Google Fonts link).

### Character Profiles

| Profile | Prioritized Sections |
|---------|---------------------|
| Caster | Defense, Skills, Weapons, **Spellcasting**, Focus, Items |
| Martial | Defense, **Weapons**, Skills, Items, Spellcasting, Focus |
| Hybrid | Defense, **Weapons**, Skills, **Spellcasting**, Focus, Items |

## Project Structure

```
pb2onepager/
├── cli.py          # Click CLI entry point
├── parse.py        # Pathbuilder JSON → CharacterModel
├── model.py        # Pydantic data models
├── profile.py      # Caster/martial/hybrid classification
├── render.py       # Jinja2 template rendering + CSS loading
├── spells.py       # Inline spell description dictionary
├── assets/
│   ├── base.css    # Core layout and typography
│   ├── print.css   # Print media / @page rules
│   └── themes/     # default.css, dark.css
└── templates/
    └── onepager.html.j2
```

## Dependencies

- [pydantic](https://docs.pydantic.dev/) — data validation and serialization
- [Jinja2](https://jinja.palletsprojects.com/) — HTML template rendering
- [Click](https://click.palletsprojects.com/) — CLI framework
