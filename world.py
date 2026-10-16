# world.py
import random
import pygame
import settings as S
from entities import ResourceNode, Animal

class World:
    def __init__(self, seed=7):
        self.rng = random.Random(seed)
        self.spawn = pygame.Vector2(400, S.WORLD_H - 400)
        self.rescue_pos = pygame.Vector2(S.WORLD_W - 300, 300)
        self.safe_zones = [pygame.Vector2(p) for p in
                           [(1500, 2400), (2600, 1700), (3500, 1000), (2000, 600)]]
        self.nodes, self.animals, self.structures = [], [], []
        self.blizzard, self.weather_timer, self.survival_started = False, 45.0, False
        self._tutorial_camp()
        self._scatter()

    def _tutorial_camp(self):
        layout = [("tree", 240, -100), ("tree", 290, 20), ("tree", 240, 130),
                  ("rock", -150, -90), ("rock", -190, 40),
                  ("bush", 60, -160), ("ice", -60, 150)]
        for kind, dx, dy in layout:
            self.nodes.append(ResourceNode(kind, self.spawn.x + dx, self.spawn.y + dy))

    def _random_far_pos(self, origin, min_dist):
        while True:
            pos = pygame.Vector2(self.rng.randint(60, S.WORLD_W - 60),
                                 self.rng.randint(60, S.WORLD_H - 60))
            if pos.distance_to(origin) > min_dist and pos.distance_to(self.rescue_pos) > 150:
                return pos

    def _scatter(self):
        for kind, n in {"tree": 90, "rock": 60, "bush": 35, "ice": 30}.items():
            for _ in range(n):
                p = self._random_far_pos(self.spawn, 420)
                self.nodes.append(ResourceNode(kind, p.x, p.y))
        for _ in range(20):
            p = self._random_far_pos(self.spawn, 420)
            self.animals.append(Animal("hare", p.x, p.y))

    def begin_survival(self, player):
        """Called when the tutorial ends: wolves + blizzards switch on."""
        self.survival_started, self.weather_timer = True, 30.0
        for _ in range(10):
            p = self._random_far_pos(player.pos, 600)
            self.animals.append(Animal("wolf", p.x, p.y))

    def update(self, dt, player):
        if self.survival_started:
            self.weather_timer -= dt
            if self.weather_timer <= 0:
                self.blizzard = not self.blizzard
                self.weather_timer = 20.0 if self.blizzard else 45.0
        events = []
        for a in self.animals:
            dealt = a.update(dt, player)
            if dealt:
                events.append((a.kind, dealt))
        self.nodes = [n for n in self.nodes if n.amount > 0]   # depleted nodes vanish
        return events

    def weather_factor(self):
        return S.BLIZZARD_FACTOR if self.blizzard else 1.0

    def place(self, kind, pos):
        self.structures.append((kind, pygame.Vector2(pos)))

    def near(self, kind, pos, radius):
        return any(k == kind and pos.distance_to(p) <= radius for k, p in self.structures)

    def in_safe_zone(self, pos):
        return any(pos.distance_to(z) <= S.SAFE_RADIUS for z in self.safe_zones)

    def nearest_node(self, pos, reach=S.GATHER_REACH):
        best, best_d = None, reach
        for n in self.nodes:
            d = pos.distance_to(n.pos) - n.radius
            if d < best_d:
                best, best_d = n, d
        return best

    def nearest_of(self, kind, pos):
        cands = [n for n in self.nodes if n.kind == kind]
        return min(cands, key=lambda n: pos.distance_to(n.pos)) if cands else None