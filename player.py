# player.py
import pygame
import settings as S
from items import Inventory

def clamp(v, lo=0.0, hi=S.MAX_STAT):
    return max(lo, min(hi, v))

class Player:
    EAT_PRIORITY = ["cooked_meat", "berries", "raw_meat"]

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.facing = pygame.Vector2(1, 0)
        self.health = self.stamina = self.warmth = self.hunger = self.thirst = S.MAX_STAT
        self.inventory = Inventory()
        self.has_spear = False
        self.attack_timer = 0.0
        self.sprinting = False

    @property
    def alive(self):
        return self.health > 0

    def move(self, dt, direction, want_sprint):
        self.sprinting = False
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.facing = direction
            speed = S.WALK_SPEED
            if want_sprint and self.stamina > 5:
                speed, self.sprinting = S.SPRINT_SPEED, True
                self.stamina = clamp(self.stamina - S.SPRINT_DRAIN * dt)
            self.pos += direction * speed * dt
            self.pos.x = max(20, min(S.WORLD_W - 20, self.pos.x))
            self.pos.y = max(20, min(S.WORLD_H - 20, self.pos.y))
        if not self.sprinting:
            self.stamina = clamp(self.stamina + S.STAMINA_REGEN * dt)

    def update_survival(self, dt, weather=1.0, near_fire=False, sheltered=False, scale=1.0):
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.hunger = clamp(self.hunger - S.HUNGER_DRAIN * dt * scale)
        self.thirst = clamp(self.thirst - S.THIRST_DRAIN * dt * scale)
        cold = S.WARMTH_DRAIN * weather * scale
        if sheltered:
            cold *= S.SHELTER_KEEPS
        self.warmth = clamp(self.warmth - cold * dt)
        if near_fire:
            self.warmth = clamp(self.warmth + S.FIRE_WARMTH * dt)
        problems = sum(1 for v in (self.hunger, self.thirst, self.warmth) if v <= 0)
        if problems:
            self.health = clamp(self.health - S.STARVE_DAMAGE * problems * dt)
        elif min(self.hunger, self.thirst, self.warmth) > 40:
            self.health = clamp(self.health + S.REGEN * dt)

    def damage(self, amount):
        self.health = clamp(self.health - amount)     # never below 0

    # ---------------- combat ----------------
    def attack_damage(self):
        bonus = S.SPEAR_BONUS if (self.has_spear and not S.BUGS["weapon"]) else 0
        return S.BASE_DAMAGE + bonus                  # BUG-03: weapon bonus ignored

    def try_attack(self, animals):
        if self.attack_timer > 0 and not S.BUGS["cooldown"]:   # BUG-04: cooldown ignored
            return []
        if self.stamina < S.ATTACK_STAMINA:
            return []
        self.stamina = clamp(self.stamina - S.ATTACK_STAMINA)
        self.attack_timer = S.ATTACK_COOLDOWN
        hits = []
        for a in animals:
            if a.alive and self.pos.distance_to(a.pos) <= S.ATTACK_RANGE:
                a.take_damage(self.attack_damage())
                hits.append(a)
        return hits

    # ---------------- eating / drinking ----------------
    def consume(self, mode):
        order = self.EAT_PRIORITY if mode == "eat" else ["ice"]
        for item in order:
            if self.inventory.remove(item, 1):
                for stat, delta in S.ITEM_EFFECTS[item].items():
                    setattr(self, stat, clamp(getattr(self, stat) + delta))
                return item
        return None