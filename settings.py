# settings.py - every tunable value lives here (easy balancing + bug toggles)
WIDTH, HEIGHT, FPS = 960, 640, 60
WORLD_W, WORLD_H = 5000, 3500
MAX_STAT, CAPACITY = 100.0, 30

# Player
WALK_SPEED, SPRINT_SPEED = 150, 240
SPRINT_DRAIN, STAMINA_REGEN = 22.0, 14.0
BASE_DAMAGE, SPEAR_BONUS = 5, 10
ATTACK_COOLDOWN, ATTACK_RANGE, ATTACK_STAMINA = 0.5, 60, 8
GATHER_REACH = 55

# Survival (per second)
HUNGER_DRAIN, THIRST_DRAIN, WARMTH_DRAIN = 0.6, 0.9, 0.8
FIRE_WARMTH, FIRE_RADIUS = 9.0, 110
SHELTER_RADIUS, SAFE_RADIUS = 80, 110
SHELTER_KEEPS = 0.25          # shelter/cave keeps only 25% of the cold
STARVE_DAMAGE, REGEN = 2.0, 1.5
BLIZZARD_FACTOR = 2.2
TUTORIAL_DRAIN_SCALE = 0.35   # gentle survival drain while learning

# Animals
AGGRO_RANGE, BITE_RANGE, BITE_COOLDOWN, FLEE_RANGE = 260, 34, 1.2, 160
RESCUE_RADIUS = 140

# ---- BUG SWITCHES (True = inject the original bug, for reproduction) ----
BUGS = {"gather": False, "craft_check": False, "weapon": False, "cooldown": False}

ITEM_EFFECTS = {
    "berries":     {"hunger": 10},
    "raw_meat":    {"hunger": 8, "health": -5},
    "cooked_meat": {"hunger": 30, "warmth": 5},
    "ice":         {"thirst": 15, "warmth": -6},
}

RECIPES = {  # insertion order = key order (1-4)
    "campfire": {"label": "Campfire", "cost": {"wood": 3, "stone": 2}},
    "spear":    {"label": "Spear",    "cost": {"wood": 2, "stone": 1}},
    "shelter":  {"label": "Shelter",  "cost": {"wood": 6, "stone": 2}},
    "beacon":   {"label": "Signal Beacon", "cost": {"wood": 8, "stone": 4}},
}

NODE_TYPES = {
    "tree": {"item": "wood",    "amount": 6, "yield": 2, "radius": 22, "color": (34, 110, 60)},
    "rock": {"item": "stone",   "amount": 6, "yield": 2, "radius": 18, "color": (130, 135, 145)},
    "bush": {"item": "berries", "amount": 3, "yield": 1, "radius": 16, "color": (60, 140, 80)},
    "ice":  {"item": "ice",     "amount": 4, "yield": 2, "radius": 20, "color": (150, 210, 245)},
}

ANIMAL_TYPES = {
    "hare": {"hp": 12, "speed": 130, "damage": 0,  "hostile": False, "radius": 10,
             "color": (245, 245, 250), "loot": {"raw_meat": 1}},
    "wolf": {"hp": 40, "speed": 110, "damage": 10, "hostile": True,  "radius": 15,
             "color": (85, 85, 95),   "loot": {"raw_meat": 2}},
    "pup":  {"hp": 15, "speed": 80,  "damage": 3,  "hostile": True,  "radius": 11,
             "color": (150, 150, 162), "loot": {"raw_meat": 1}},
}

STORY_INTRO = [
    "Dr. Mara Santos, a glaciologist from Laguna, Philippines, boarded a cargo plane carrying ice-core samples "
    "that could help predict coastal flooding for millions of people.",
    "A whiteout storm tore the plane apart over the Arctic ice shelf. The pilot did not survive. Mara wakes in the "
    "wreckage: the radio is smashed, her hands are numb, and the wind is rising.",
    "Her last satellite ping placed a rescue patrol along the north-east ridge. She must reach the red rescue flag "
    "and build a Signal Beacon before the cold, hunger, or wolves finish her.",
    "Gather wood and stone, craft fire, shelter and a spear, hunt carefully, and survive the blizzards.",
]