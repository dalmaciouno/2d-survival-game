# ❄️ Frostbound: Arctic Survival

A 2D top-down survival game prototype built with **Python** and **Pygame**.
Play as Dr. Mara Santos, a glaciologist stranded on an Arctic ice shelf after a plane crash. Gather supplies, craft gear, fight off wolves, survive blizzards, and reach the rescue point to light a Signal Beacon.

> Made for **CSEG1 Game Concepts and Production**, Final Laboratory Examination (Set B), University of Cabuyao, College of Computing Studies, AY 2026-2027.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [How to Run the Game](#how-to-run-the-game)
- [Controls](#controls)
- [How to Play](#how-to-play)
- [Running the Test Suite](#running-the-test-suite)
- [Reproducing the Bugs](#reproducing-the-bugs)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)

---

## Features

- **Survival stats:** health, stamina, warmth, hunger, and thirst.
- **Resource gathering:** trees (wood), rocks (stone), bushes (berries), and ice (water). Sources deplete.
- **Crafting:** Campfire, Spear, Shelter, and Signal Beacon.
- **Combat:** hares (passive), wolf pups, and wolves, with a stamina-costing attack and cooldown.
- **Weather:** periodic blizzards that double cold drain.
- **Safe zones:** ice caves that reduce cold.
- **13-step interactive tutorial** ordered from basic to advanced, with arrows, glowing rings, and on-screen feedback messages.
- **Story intro** and win/lose screens.
- **Built-in test harness** with 15 test cases and 4 injectable bugs for before/after debugging evidence.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| Pygame | 2.x |
| OS | Windows, macOS, or Linux |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/frostbound.git
cd frostbound
```

(Or click **Code → Download ZIP** on GitHub, extract it, and open a terminal in the extracted folder.)

### 2. (Recommended) Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pygame
```

Or, if the repo includes a `requirements.txt` containing the line `pygame`:

```bash
pip install -r requirements.txt
```

---

## How to Run the Game

From the project folder, run:

```bash
python main.py
```

On macOS/Linux you may need `python3 main.py`.

A 960×640 window will open with the story screen. Press **ENTER** to start the tutorial.

---

## Controls

| Key | Action |
|---|---|
| `W` `A` `S` `D` / Arrow keys | Move |
| `SHIFT` (hold) | Sprint (drains stamina) |
| `E` | Gather from the nearest tree, rock, bush, or ice |
| `SPACE` (hold) | Attack nearby animals |
| `R` | Eat (cooked meat, berries, then raw meat) |
| `T` | Drink (uses ice) |
| `F` | Cook raw meat (stand near a campfire) |
| `1` | Craft Campfire (3 wood, 2 stone) |
| `2` | Craft Spear (2 wood, 1 stone) |
| `3` | Craft Shelter (6 wood, 2 stone) |
| `4` | Craft Signal Beacon (8 wood, 4 stone; only inside the red rescue ring) |
| `ENTER` | Continue / confirm / restart |
| `K` | Skip the tutorial |

---

## How to Play

**Goal:** Travel to the red **Rescue Point** in the far north-east of the map (distance shown at the top-right) and craft a **Signal Beacon** inside the red ring.

**Survival tips**

- If **warmth, hunger, or thirst** hits 0, you start losing health.
- Stand near a **campfire** to restore warmth and to cook meat.
- **Ice caves** (blue zones) and **shelters** slow the cold.
- **Blizzards** double cold drain: find fire or a cave.
- Craft a **spear** before fighting wolves (damage 5 → 15).
- Raw meat costs health; **cook it** first.
- Resource nodes run out, so keep moving toward the rescue point.

**Tutorial:** The 13 steps cover stats, movement, sprinting, gathering, crafting, warmth, eating, drinking, spear crafting, combat, cooking, and the mission briefing. Survival drain is slowed to 35% while you learn.

---

## Running the Test Suite

The test harness runs 15 test cases twice: first with the bugs injected (**BEFORE FIX**), then with the corrected code (**AFTER FIX**).

```bash
python test_runner.py
```

It prints a results table for both phases and writes **`test_report.csv`** containing the scenario, expected result, actual result, and PASS/FAIL status for each case.

**Expected outcome:** several FAILs in the BEFORE FIX phase and `15/15 passed` in the AFTER FIX phase.

---

## Reproducing the Bugs

Four bugs can be switched on in `settings.py`:

```python
BUGS = {"gather": False, "craft_check": False, "weapon": False, "cooldown": False}
```

| Switch | Bug when `True` |
|---|---|
| `gather` | Resource nodes never deplete / over-yield |
| `craft_check` | Items can be crafted without all materials |
| `weapon` | Spear damage bonus is ignored |
| `cooldown` | Attack cooldown is ignored (hits every frame) |

Set a switch to `True`, run `python main.py`, observe the bug, then set it back to `False` to confirm the fix. Keep all switches `False` for normal play.

---

## Project Structure

```
frostbound/
├── main.py          # Entry point
├── settings.py      # Balance values, recipes, story text, bug switches
├── items.py         # Inventory class (capacity, crafting)
├── entities.py      # ResourceNode and Animal classes
├── player.py        # Player stats, movement, combat, consuming items
├── world.py         # World generation, weather, structures, safe zones
├── tutorial.py      # Step and Tutorial classes (13-step onboarding)
├── ui.py            # HUD, world rendering, tutorial overlay, screens
├── game.py          # Game loop, input handling, state machine
├── test_runner.py   # Test cases + before/after evidence (test_report.csv)
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pygame'` | Run `pip install pygame` (make sure your virtual environment is active). |
| `python` is not recognized (Windows) | Reinstall Python and tick **Add Python to PATH**, or use `py main.py`. |
| `pip install pygame` fails on a very new Python version | Try `pip install pygame-ce` (a drop-in replacement) or use Python 3.11/3.12. |
| Window opens but runs slowly | Close other heavy apps. The game targets 60 FPS. |
| `ImportError` for `settings`, `items`, etc. | Run commands from inside the project folder so the modules are found. |

---

## Credits

- **Course:** CSEG1 Game Concepts and Production
- **Institution:** University of Cabuyao, College of Computing Studies
- **Developer:** _Your Name_
- **Instructor:** Renzo Evangelista
- **Built with:** [Python](https://www.python.org/) and [Pygame](https://www.pygame.org/)

---

## License

This project was created for academic purposes. Add a license of your choice (e.g., MIT) if you plan to share it publicly.