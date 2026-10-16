# tutorial.py - 13 steps ordered basic -> advanced
from dataclasses import dataclass
from typing import Callable, Optional
import pygame
import settings as S
from entities import Animal

@dataclass
class Step:
    title: str
    text: str
    check: Callable                      # (player, world, counters) -> bool
    target: Optional[Callable] = None    # (player, world) -> world position or None
    on_start: Optional[Callable] = None  # (player, world) -> None

def _set(stat, value):
    def f(p, w): setattr(p, stat, value)
    return f

class Tutorial:
    def __init__(self, world):
        self.world, self.active, self.index, self.flash = world, True, 0, 0.0
        self.counters = {"sprint": 0.0, "warm": 0.0, "ate": 0, "drank": 0,
                         "kills": 0, "cooked": 0, "ack": 0}
        self.marker = world.spawn + pygame.Vector2(150, 0)
        self.steps = self._build()

    def _near(self, kind):
        def f(p, w):
            n = w.nearest_of(kind, p.pos)
            return n.pos if n else None
        return f

    def _build(self):
        inv = lambda p, item: p.inventory.count(item)
        return [
            Step("Know Your Stats",
                 "Top-left bars: HEALTH (red), STAMINA (green), WARMTH (cyan), HUNGER (orange), THIRST (blue). "
                 "If warmth, hunger or thirst reaches 0 you lose health. Press ENTER to continue.",
                 lambda p, w, c: c["ack"] >= 1),
            Step("Move", "Use W A S D or the arrow keys to walk into the glowing ring.",
                 lambda p, w, c: p.pos.distance_to(self.marker) < 40, lambda p, w: self.marker),
            Step("Sprint", "Hold SHIFT while moving to sprint for 2 seconds. Sprinting drains STAMINA (green); "
                           "it refills while you walk or stand still.",
                 lambda p, w, c: c["sprint"] >= 2.0),
            Step("Gather Wood", "Walk next to a tree (the arrow points to the nearest) and tap E to chop. Collect 5 wood.",
                 lambda p, w, c: inv(p, "wood") >= 5, self._near("tree")),
            Step("Gather Stone", "Tap E next to a grey rock. Collect 3 stone.",
                 lambda p, w, c: inv(p, "stone") >= 3, self._near("rock")),
            Step("Craft a Campfire", "Press 1 to craft a Campfire (3 wood + 2 stone). "
                                     "The crafting panel turns green when you can afford an item.",
                 lambda p, w, c: any(k == "campfire" for k, _ in w.structures)),
            Step("Stay Warm", "You are getting cold! Stand inside the orange fire glow for 3 seconds to restore WARMTH.",
                 lambda p, w, c: c["warm"] >= 3.0, None, _set("warmth", 55)),
            Step("Eat", "HUNGER is low. Tap E at the berry bush, then press R to eat. Food restores HUNGER.",
                 lambda p, w, c: c["ate"] >= 1, self._near("bush"), _set("hunger", 45)),
            Step("Drink", "THIRST is low. Tap E on the blue ice patch, then press T to drink. "
                          "Ice chills you slightly, so drink near the fire.",
                 lambda p, w, c: c["drank"] >= 1, self._near("ice"), _set("thirst", 40)),
            Step("Craft a Spear", "Press 2 to craft a Spear (2 wood + 1 stone). It raises your damage from 5 to 15.",
                 lambda p, w, c: p.has_spear),
            Step("Combat", "A wolf pup attacks! Get close and hold SPACE to strike (0.5 s cooldown, costs stamina). "
                           "Watch your HEALTH.",
                 lambda p, w, c: c["kills"] >= 1, None,
                 lambda p, w: w.animals.append(Animal("pup", p.pos.x + 200, p.pos.y - 50))),
            Step("Cook Food", "Raw meat is unsafe (-5 health). Stand near your campfire, press F to cook it, "
                              "then R to eat. Cooked meat restores far more hunger.",
                 lambda p, w, c: c["cooked"] >= 1),
            Step("Your Mission", "Reach the red RESCUE FLAG in the far north-east (distance shown top-right) and craft "
                                 "a Signal Beacon there (key 4: 8 wood + 4 stone). Key 3 builds a Shelter. "
                                 "Beware blizzards and wolves. Press ENTER to begin!",
                 lambda p, w, c: c["ack"] >= 1),
        ]

    def current(self):
        return self.steps[self.index] if self.active else None

    def target_pos(self, player):
        s = self.current()
        return s.target(player, self.world) if s and s.target else None

    def update(self, dt, player):
        if not self.active:
            return
        c = self.counters
        if player.sprinting:
            c["sprint"] += dt
        if self.world.near("campfire", player.pos, S.FIRE_RADIUS):
            c["warm"] += dt
        self.flash = max(0.0, self.flash - dt)
        if self.steps[self.index].check(player, self.world, c):
            self.flash = 1.5
            self.index += 1
            for k in c:                      # fresh counters for each step
                c[k] = 0
            if self.index >= len(self.steps):
                self.finish(player)
            elif self.steps[self.index].on_start:
                self.steps[self.index].on_start(player, self.world)

    def finish(self, player):
        self.active = False
        self.world.begin_survival(player)