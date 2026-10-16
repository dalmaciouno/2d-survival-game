# entities.py
import random
import pygame
import settings as S

class ResourceNode:
    """A tree, rock, berry bush or ice patch with a limited amount."""
    def __init__(self, kind, x, y):
        d = S.NODE_TYPES[kind]
        self.kind, self.item = kind, d["item"]
        self.amount, self.yield_ = d["amount"], d["yield"]
        self.radius, self.color = d["radius"], d["color"]
        self.pos = pygame.Vector2(x, y)

    def gather(self, inventory):
        """Returns the quantity actually added to the inventory."""
        if self.amount <= 0:
            return 0
        if S.BUGS["gather"]:                   # BUG-01: never depletes / over-yields
            return inventory.add(self.item, self.yield_)
        qty = min(self.yield_, self.amount)    # FIX: cannot take more than remains
        added = inventory.add(self.item, qty)
        self.amount -= added                   # FIX: deplete only what was taken
        return added


class Animal:
    """Hare (passive, flees), wolf (hostile), pup (weak tutorial enemy)."""
    def __init__(self, kind, x, y):
        d = S.ANIMAL_TYPES[kind]
        self.kind = kind
        self.pos = pygame.Vector2(x, y)
        self.health = self.max_health = d["hp"]
        self.speed, self.damage, self.hostile = d["speed"], d["damage"], d["hostile"]
        self.loot, self.radius, self.color = d["loot"], d["radius"], d["color"]
        self.bite_timer = 0.0
        self.wander_dir = pygame.Vector2()
        self.wander_timer = 0.0

    @property
    def alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def update(self, dt, player):
        """Returns damage dealt to the player this frame (0 if none)."""
        self.bite_timer = max(0.0, self.bite_timer - dt)
        to_player = player.pos - self.pos
        dist = to_player.length()
        dealt = 0
        if self.hostile and dist < S.AGGRO_RANGE:
            if dist > S.BITE_RANGE:
                self.pos += to_player.normalize() * self.speed * dt
            elif self.bite_timer <= 0:
                player.damage(self.damage)
                self.bite_timer = S.BITE_COOLDOWN
                dealt = self.damage
        elif not self.hostile and 0 < dist < S.FLEE_RANGE:
            self.pos -= to_player.normalize() * self.speed * dt
        else:
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.wander_timer = random.uniform(1, 3)
                self.wander_dir = (pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
                                   if random.random() < 0.6 else pygame.Vector2())
            self.pos += self.wander_dir * self.speed * 0.3 * dt
        self.pos.x = max(10, min(S.WORLD_W - 10, self.pos.x))
        self.pos.y = max(10, min(S.WORLD_H - 10, self.pos.y))
        return dealt