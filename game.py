# game.py
import sys
import pygame
import settings as S
from player import Player
from world import World
from tutorial import Tutorial
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption("Frostbound - Arctic Survival")
        self.clock = pygame.time.Clock()
        self.ui = UI()
        self.state = "story"
        self.reset()

    def reset(self):
        self.world = World()
        self.player = Player(self.world.spawn.x, self.world.spawn.y)
        self.tutorial = Tutorial(self.world)
        self.messages, self.camera = [], pygame.Vector2()
        self.in_cave, self.prev_blizzard, self.cause = False, False, ""

    def say(self, text, color=(255, 255, 255)):
        self.messages.append([text, 4.0, color])
        self.messages = self.messages[-5:]

    # ---------------- input ----------------
    def handle(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if self.state == "story" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.state = "play"
        elif self.state in ("win", "lose") and e.key == pygame.K_RETURN:
            self.reset()
            self.state = "play"
        elif self.state == "play":
            k = e.key
            if k == pygame.K_e: self.gather()
            elif k == pygame.K_r: self.eat_drink("eat")
            elif k == pygame.K_t: self.eat_drink("drink")
            elif k == pygame.K_f: self.cook()
            elif k == pygame.K_RETURN: self.tutorial.counters["ack"] += 1
            elif k == pygame.K_k and self.tutorial.active:
                self.tutorial.finish(self.player)
                self.say("Tutorial skipped. Wolves now roam the ice!", (255, 200, 90))
            elif k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.craft(list(S.RECIPES)[k - pygame.K_1])

    # ---------------- actions ----------------
    def gather(self):
        node = self.world.nearest_node(self.player.pos)
        if not node:
            return self.say("Nothing to gather here. Move next to a tree, rock, bush or ice.", (255, 220, 120))
        got = node.gather(self.player.inventory)
        if got == 0:
            self.say("Your bag is full!", (255, 120, 120))
        else:
            self.say(f"+{got} {node.item}  ({node.amount} left in this source)", (160, 255, 170))

    def eat_drink(self, mode):
        item = self.player.consume(mode)
        if not item:
            return self.say("You have nothing to eat." if mode == "eat" else
                            "You have no ice to drink. Gather ice first.", (255, 220, 120))
        self.say(f"You used {item}.", (160, 255, 170))
        if self.tutorial.active:
            self.tutorial.counters["ate" if mode == "eat" else "drank"] += 1

    def cook(self):
        p, w = self.player, self.world
        if not w.near("campfire", p.pos, S.FIRE_RADIUS):
            return self.say("Stand near a campfire to cook.", (255, 220, 120))
        if not p.inventory.remove("raw_meat"):
            return self.say("You have no raw meat. Hunt a hare or wolf.", (255, 220, 120))
        p.inventory.add("cooked_meat", 1)
        self.say("Cooked meat ready! Press R to eat.", (160, 255, 170))
        if self.tutorial.active:
            self.tutorial.counters["cooked"] += 1

    def craft(self, name):
        p, w, r = self.player, self.world, S.RECIPES[name]
        if name == "beacon" and p.pos.distance_to(w.rescue_pos) > S.RESCUE_RADIUS:
            return self.say("The beacon must be built inside the red ring at the rescue point.", (255, 220, 120))
        if name == "spear" and p.has_spear:
            return self.say("You already own a spear.", (255, 220, 120))
        ok, msg = p.inventory.craft(name)
        if not ok:
            return self.say(msg, (255, 120, 120))
        if name in ("campfire", "shelter"):
            w.place(name, p.pos)
        elif name == "spear":
            p.has_spear = True
        elif name == "beacon":
            self.state = "win"
        self.say(f"Crafted {r['label']}!", (160, 255, 170))

    def attack(self):
        p = self.player
        for a in p.try_attack(self.world.animals):
            if a.alive:
                self.say(f"Hit {a.kind}! {a.health:.0f} HP left", (255, 200, 120))
            else:
                for item, qty in a.loot.items():
                    p.inventory.add(item, qty)
                self.say(f"{a.kind.capitalize()} defeated! Looted {a.loot}", (160, 255, 170))
                if self.tutorial.active:
                    self.tutorial.counters["kills"] += 1
        self.world.animals = [a for a in self.world.animals if a.alive]

    # ---------------- update / draw ----------------
    def update(self, dt):
        p, w, k = self.player, self.world, pygame.key.get_pressed()
        dx = int(k[pygame.K_d] or k[pygame.K_RIGHT]) - int(k[pygame.K_a] or k[pygame.K_LEFT])
        dy = int(k[pygame.K_s] or k[pygame.K_DOWN]) - int(k[pygame.K_w] or k[pygame.K_UP])
        p.move(dt, pygame.Vector2(dx, dy), k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT])
        if k[pygame.K_SPACE]:
            self.attack()
        cave = w.in_safe_zone(p.pos)
        if cave and not self.in_cave:
            self.say("Ice cave: shelter from the wind (cold drains slower).", (140, 210, 255))
        self.in_cave = cave
        scale = S.TUTORIAL_DRAIN_SCALE if self.tutorial.active else 1.0
        p.update_survival(dt, w.weather_factor(), w.near("campfire", p.pos, S.FIRE_RADIUS),
                          cave or w.near("shelter", p.pos, S.SHELTER_RADIUS), scale)
        for kind, dmg in w.update(dt, p):
            self.say(f"A {kind} bites you! -{dmg} health", (255, 120, 120))
        if w.blizzard != self.prev_blizzard:
            self.say("A BLIZZARD hits! Seek fire or an ice cave." if w.blizzard else
                     "The blizzard fades.", (255, 200, 90))
            self.prev_blizzard = w.blizzard
        was_active = self.tutorial.active
        self.tutorial.update(dt, p)
        if was_active and not self.tutorial.active:
            self.say("Tutorial complete! Wolves now roam. Reach the rescue flag!", (255, 220, 90))
        for m in self.messages:
            m[1] -= dt
        self.messages = [m for m in self.messages if m[1] > 0]
        self.camera.x = max(0, min(S.WORLD_W - S.WIDTH, p.pos.x - S.WIDTH / 2))
        self.camera.y = max(0, min(S.WORLD_H - S.HEIGHT, p.pos.y - S.HEIGHT / 2))
        if not p.alive:
            self.cause = ("hypothermia" if p.warmth <= 0 else "dehydration" if p.thirst <= 0
                          else "starvation" if p.hunger <= 0 else "a wildlife attack")
            self.state = "lose"

    def draw(self):
        if self.state == "story":
            self.screen.fill((15, 25, 45))
            self.ui.draw_overlay(self.screen, "FROSTBOUND - ARCTIC SURVIVAL",
                                 S.STORY_INTRO, "Press ENTER to begin the tutorial")
        else:
            self.ui.draw_world(self.screen, self)
            self.ui.draw_hud(self.screen, self)
            self.ui.draw_tutorial(self.screen, self)
            if self.state == "win":
                self.ui.draw_overlay(self.screen, "RESCUED!", [
                    "The Signal Beacon lights the ridge. A helicopter breaks through the clouds. "
                    "Mara's ice cores, and her survival, make it home.", "Press ENTER to play again."],
                    "ENTER = play again")
            elif self.state == "lose":
                self.ui.draw_overlay(self.screen, "YOU DID NOT SURVIVE", [
                    f"Mara was lost to {self.cause}. Manage warmth, food and water, and avoid wolves "
                    "without a spear."], "ENTER = try again")
        pygame.display.flip()

    def run(self):
        while True:
            dt = min(self.clock.tick(S.FPS) / 1000, 0.05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle(e)
            if self.state == "play":
                self.update(dt)
            self.draw()