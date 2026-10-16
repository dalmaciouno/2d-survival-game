# test_runner.py - solo test harness: runs every case with bugs ON, then OFF
import csv
import settings as S
from items import Inventory
from entities import ResourceNode, Animal
from player import Player

def _fight(spear=False):
    p = Player(100, 100)
    p.has_spear = spear
    return p, Animal("wolf", 130, 100)         # wolf 30 px away, 40 HP

def tc01():
    inv, n = Inventory(), ResourceNode("tree", 0, 0)
    n.gather(inv); return (inv.count("wood"), n.amount)
def tc02():
    inv, n = Inventory(), ResourceNode("tree", 0, 0)
    for _ in range(5): n.gather(inv)
    return (inv.count("wood"), n.amount)
def tc03():
    inv, n = Inventory(), ResourceNode("tree", 0, 0)
    n.amount = 1; n.gather(inv); return (inv.count("wood"), n.amount)
def tc04():
    inv = Inventory(); inv.add("wood", 3)
    ok, _ = inv.craft("campfire"); return (ok, inv.count("wood"), inv.count("stone"))
def tc05():
    inv = Inventory(); inv.add("wood", 3); inv.add("stone", 2)
    ok, _ = inv.craft("campfire"); return (ok, inv.count("wood"), inv.count("stone"))
def tc06():
    inv = Inventory(); inv.add("wood", 5); inv.add("stone", 3)
    ok, _ = inv.craft("spear"); return (ok, inv.count("wood"), inv.count("stone"))
def tc07():
    p, wolf = _fight(); p.try_attack([wolf]); return wolf.health
def tc08():
    p, wolf = _fight(True); p.try_attack([wolf]); return wolf.health
def tc09():
    p, wolf = _fight(True); p.try_attack([wolf]); p.try_attack([wolf]); return wolf.health
def tc10():
    p, wolf = _fight(True); p.try_attack([wolf])
    p.update_survival(0.6); p.try_attack([wolf]); return wolf.health
def tc11():
    p, wolf = Player(100, 100), Animal("wolf", 120, 100)
    wolf.update(0.016, p); return p.health
def tc12():
    p = Player(0, 0); p.hunger = 98; p.inventory.add("berries", 1)
    p.consume("eat"); return p.hunger
def tc13():
    inv = Inventory(); inv.add("wood", 40); return inv.count("wood")
def tc14():
    p = Player(0, 0); p.warmth = 50
    p.update_survival(1.0, 1.0, near_fire=True); return round(p.warmth, 1)
def tc15():
    p = Player(0, 0); p.update_survival(1.0, S.BLIZZARD_FACTOR); return round(p.warmth, 1)

CASES = [
 ("TC-01", "Gather once from a tree (6 wood, yields 2)", (2, 4), tc01),
 ("TC-02", "Gather 5 times: tree must deplete, wood total 6", (6, 0), tc02),
 ("TC-03", "Node has only 1 left, yield is 2: take just 1", (1, 0), tc03),
 ("TC-04", "Craft campfire with 3 wood, 0 stone (must be refused)", (False, 3, 0), tc04),
 ("TC-05", "Craft campfire with exact 3 wood + 2 stone", (True, 0, 0), tc05),
 ("TC-06", "Craft spear from 5 wood + 3 stone", (True, 3, 2), tc06),
 ("TC-07", "Bare-hand hit on wolf (40 HP): 5 dmg", 35, tc07),
 ("TC-08", "Spear hit on wolf (40 HP): 15 dmg", 25, tc08),
 ("TC-09", "Two spear attacks in the same frame: only 1 lands", 25, tc09),
 ("TC-10", "Spear attack, wait 0.6s, attack again: 2 hits", 10, tc10),
 ("TC-11", "Wolf bites player at 100 HP: 10 dmg", 90, tc11),
 ("TC-12", "Eat berries at 98 hunger: clamp to 100", 100.0, tc12),
 ("TC-13", "Add 40 wood to 30-slot bag: capped at 30", 30, tc13),
 ("TC-14", "Warmth 50 near fire for 1s: -1 cold +9 fire = 58", 58.0, tc14),
 ("TC-15", "Blizzard drain for 1s from 100 warmth: 97.8", 97.8, tc15),
]

def run(phase, bugs_on, writer):
    for key in S.BUGS: S.BUGS[key] = bugs_on
    print(f"\n===== {phase} =====")
    print(f"{'ID':6}{'Scenario':58}{'Expected':16}{'Actual':16}Status")
    passed = 0
    for tid, scenario, expected, fn in CASES:
        try: actual = fn()
        except Exception as ex: actual = f"ERROR {ex}"
        status = "PASS" if actual == expected else "FAIL"
        passed += status == "PASS"
        print(f"{tid:6}{scenario:58}{str(expected):16}{str(actual):16}{status}")
        writer.writerow([phase, tid, scenario, expected, actual, status])
    print(f"Result: {passed}/{len(CASES)} passed")

if __name__ == "__main__":
    with open("test_report.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Phase", "ID", "Scenario", "Expected", "Actual", "Status"])
        run("BEFORE FIX (bugs injected)", True, w)
        run("AFTER FIX (corrected code)", False, w)
    print("\nSaved test_report.csv")