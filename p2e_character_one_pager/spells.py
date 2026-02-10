"""Brief spell descriptions for PF2e spells."""

SPELL_DESCRIPTIONS: dict[str, str] = {
    # Arcane Cantrips
    "Detect Magic": "Sense magical auras in a 30-foot emanation.",
    "Electric Arc": "Zap one or two creatures within 30 ft for 1d4+ability electricity damage (basic Reflex).",
    "Light": "Make an object glow as bright as a torch for 1 hour.",
    "Message": "Whisper a message to a creature within 120 ft that only the target can hear.",
    "Prestidigitation": "Perform a minor magical trick — cook, lift, clean, make sounds, etc.",
    "Read Aura": "Detect whether an object is magical and determine its school.",
    "Shield": "Raise a magical shield granting +1 AC. Can Shield Block for 5 damage.",
    "Telekinetic Hand": "Remotely manipulate a small unattended object within 30 ft.",
    "Telekinetic Projectile": "Hurl a loose object at a creature for 1d6+ability bludgeoning, piercing, or slashing.",

    # Arcane Rank 1
    "Charm": "A creature within 30 ft becomes friendly to you (Will save). Hostile creatures are immune.",
    "Command": "Speak a one-word command a creature must obey on its turn (Will save).",
    "Fear": "Frighten a creature within 30 ft (Will save). Frightened 1, or 2 on crit fail; fleeing on crit fail.",
    "Grease": "Coat a 4-square area in grease. Creatures must balance (Reflex) or fall prone.",
    "Illusory Object": "Create a visual illusion of an object up to 20-ft cube within 500 ft.",
    "Leaden Steps": "Impede a creature's movement — 10-ft status penalty to Speed (Fort save).",
    "Mystic Armor": "Ward yourself with magical force, gaining a +1 item bonus to AC (like Mage Armor).",

    # Arcane Rank 2
    "Blur": "Target becomes concealed (20% miss chance) for 1 minute.",
    "Dispel Magic": "Counteract a spell effect. Counteract check vs the spell's DC.",
    "Invisibility": "Target becomes invisible for 10 minutes or until it takes a hostile action.",
    "Laughing Fit": "Target is overcome with laughter — slowed 1 (Will save). Crit fail: prone and slowed.",
    "Resist Energy": "Grant resistance 5 to one energy type (acid, cold, electricity, fire, sonic) for 10 min.",
    "Stupefy": "Dull a creature's mind — clumsy 1 and stupefied 1 (Will save).",
    "Sudden Bolt": "A bolt of lightning strikes a creature for 4d12 electricity (basic Reflex).",
    "Telekinetic Maneuver": "Perform a Disarm, Shove, or Trip using spell attack vs target's Fortitude DC.",

    # Arcane Rank 3
    "Fireball": "A 20-ft burst within 500 ft deals 6d6 fire damage (basic Reflex).",
    "Haste": "Target gains quickened 1 for 1 minute — extra action for Strike or Stride.",
    "Lightning Bolt": "A 120-ft line of lightning deals 4d12 electricity (basic Reflex).",
    "Slow": "Slow a creature — it becomes slowed 1 for 1 minute (Fort save).",

    # Arcane Rank 4
    "Containment": "Trap a creature in a magical prison — they can't leave a 10-ft emanation (Will save).",
    "Translocate": "Teleport yourself up to 120 ft to a location you can see.",
    "Wall of Fire": "Create a 60-ft line of fire. Passing through deals 4d6 fire; adjacent takes 1d6.",

    # Divine Cantrips
    "Guidance": "Grant a creature +1 status bonus to one attack, Perception, save, or skill check.",
    "Stabilize": "Stabilize a dying creature within 30 ft — stops dying but remains unconscious.",

    # Divine Spells
    "Heal": "Restore 1d8 HP per rank to a living target, or damage undead. 1-action touch, 2-action 30 ft ranged, 3-action 30 ft emanation.",
    "Bless": "30-ft emanation centered on you grants +1 status bonus to attack rolls for allies.",

    # Focus Spells
    "Hand of the Apprentice": "Hurl your melee weapon at a target within 500 ft using a spell attack roll, dealing weapon damage.",
    "Interdisciplinary Incantation": "Cast a non-arcane spell from another tradition's list that you have in your spellbook.",
}
