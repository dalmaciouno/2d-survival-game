# ui.py
import math, random
import pygame
import settings as S

def wrap(font, text, width):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if font.size(t)[0] <= width:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines

class UI:
    BAR = {"HEALTH": (220, 60, 60), "STAMINA": (80, 200, 100), "WARMTH": (70, 200, 230),
           "HUNGER": (235, 150, 50), "THIRST": (70, 110, 235)}

    def __init__(self):
        mk = lambda s, b=False: pygame.font.SysFont("arial", s, bold=b)
        self.font, self.small, self.mid, self.big = mk(16), mk(13), mk(20, True), mk(34, True)
        self.fog = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        self.fog.fill((235, 240, 255, 90))

    def text(self, screen, txt, pos, font=None, color=(20, 30, 40)):
        screen.blit((font or self.font).render(txt, True, color), pos)

    def glow(self, screen, c, r, color):
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (r, r), r)
        screen.blit(s, (int(c[0] - r), int(c[1] - r)))

    def vis(self, c, m=60):
        return -m <= c.x <= S.WIDTH + m and -m <= c.y <= S.HEIGHT + m

    # ---------------- world ----------------
    def draw_world(self, screen, game):
        cam, w, p = game.camera, game.world, game.player
        screen.fill((226, 238, 247))
        for gx in range(0, S.WORLD_W, 200):
            x = gx - cam.x
            if 0 <= x <= S.WIDTH:
                pygame.draw.line(screen, (212, 226, 240), (x, 0), (x, S.HEIGHT))
        for gy in range(0, S.WORLD_H, 200):
            y = gy - cam.y
            if 0 <= y <= S.HEIGHT:
                pygame.draw.line(screen, (212, 226, 240), (0, y), (S.WIDTH, y))
        for z in w.safe_zones:
            c = z - cam
            if self.vis(c, 160):
                self.glow(screen, c, S.SAFE_RADIUS, (120, 160, 210, 90))
                self.text(screen, "Ice Cave (safe zone)", (c.x - 62, c.y - 8), self.small, (30, 60, 110))
        for kind, pos in w.structures:
            c = pos - cam
            if not self.vis(c, 150):
                continue
            if kind == "campfire":
                self.glow(screen, c, S.FIRE_RADIUS, (255, 170, 60, 70))
                pygame.draw.circle(screen, (240, 110, 30), c, 11)
                pygame.draw.circle(screen, (255, 220, 90), c, 5)
            else:
                pygame.draw.polygon(screen, (120, 85, 50),
                                    [(c.x - 28, c.y + 18), (c.x + 28, c.y + 18), (c.x, c.y - 24)])
        rc = w.rescue_pos - cam
        if self.vis(rc, 200):
            pygame.draw.circle(screen, (220, 50, 50), rc, S.RESCUE_RADIUS, 3)
            pygame.draw.line(screen, (60, 40, 30), (rc.x, rc.y + 30), (rc.x, rc.y - 40), 4)
            pygame.draw.polygon(screen, (220, 40, 40),
                                [(rc.x, rc.y - 40), (rc.x + 32, rc.y - 28), (rc.x, rc.y - 16)])
            self.text(screen, "RESCUE POINT", (rc.x - 45, rc.y + 36), self.small, (160, 20, 20))
        for n in w.nodes:
            c = n.pos - cam
            if not self.vis(c):
                continue
            if n.kind == "tree":
                pygame.draw.rect(screen, (110, 75, 45), (c.x - 4, c.y + 8, 8, 16))
            if n.kind == "ice":
                pygame.draw.ellipse(screen, n.color, (c.x - n.radius, c.y - n.radius * 0.6,
                                                      n.radius * 2, n.radius * 1.2))
            else:
                pygame.draw.circle(screen, n.color, c, n.radius)
            if n.kind == "bush":
                for dx, dy in ((-6, -4), (5, 3), (-2, 7)):
                    pygame.draw.circle(screen, (210, 40, 60), (c.x + dx, c.y + dy), 3)
            if p.pos.distance_to(n.pos) < 130:
                self.text(screen, f"{n.item} x{n.amount}", (c.x - 25, c.y - n.radius - 18), self.small)
        for a in w.animals:
            c = a.pos - cam
            if not self.vis(c):
                continue
            pygame.draw.circle(screen, a.color, c, a.radius)
            pygame.draw.circle(screen, (40, 40, 50), c, a.radius, 2)
            pygame.draw.rect(screen, (60, 60, 60), (c.x - 14, c.y - a.radius - 9, 28, 4))
            pygame.draw.rect(screen, (220, 60, 60),
                             (c.x - 14, c.y - a.radius - 9, 28 * a.health / a.max_health, 4))
        pc = p.pos - cam
        pygame.draw.circle(screen, (40, 90, 200), pc, 14)
        pygame.draw.line(screen, (255, 255, 255), pc, pc + p.facing * 20, 3)
        if p.has_spear:
            pygame.draw.line(screen, (120, 80, 40), pc, pc + p.facing * 34, 3)
        if w.blizzard:
            screen.blit(self.fog, (0, 0))
            for _ in range(70):
                x, y = random.randint(0, S.WIDTH), random.randint(0, S.HEIGHT)
                pygame.draw.line(screen, (255, 255, 255), (x, y), (x - 16, y + 6))

    # ---------------- HUD ----------------
    def draw_hud(self, screen, game):
        p, w = game.player, game.world
        stats = [("HEALTH", p.health), ("STAMINA", p.stamina), ("WARMTH", p.warmth),
                 ("HUNGER", p.hunger), ("THIRST", p.thirst)]
        for i, (label, val) in enumerate(stats):
            y = 12 + i * 22
            self.text(screen, label, (10, y - 1), self.small)
            pygame.draw.rect(screen, (60, 70, 80), (78, y, 130, 14), border_radius=4)
            pygame.draw.rect(screen, self.BAR[label], (78, y, 130 * val / 100, 14), border_radius=4)
            if val < 25:
                self.text(screen, "!", (214, y - 3), self.mid, (220, 30, 30))
        dist = int(p.pos.distance_to(w.rescue_pos) / 10)
        self.text(screen, f"Rescue point: {dist} m", (S.WIDTH - 190, 12), self.font, (160, 20, 20))
        if w.blizzard:
            self.text(screen, "BLIZZARD! Cold x2 - find fire or cave", (S.WIDTH - 290, 36), self.font, (180, 30, 30))
        # crafting + inventory panel
        box = pygame.Rect(10, S.HEIGHT - 168, 330, 138)
        pygame.draw.rect(screen, (30, 45, 70), box, border_radius=8)
        self.text(screen, "CRAFTING (press key)", (box.x + 10, box.y + 6), self.small, (255, 210, 80))
        for i, (key, r) in enumerate(S.RECIPES.items()):
            ok = p.inventory.can_afford(r["cost"])
            cost = ", ".join(f"{v} {k}" for k, v in r["cost"].items())
            self.text(screen, f"[{i + 1}] {r['label']}: {cost}", (box.x + 10, box.y + 26 + i * 19),
                      self.font, (120, 230, 140) if ok else (230, 130, 130))
        inv = " | ".join(f"{k} {v}" for k, v in p.inventory.items.items()) or "empty"
        self.text(screen, f"Bag {p.inventory.total()}/{p.inventory.capacity}: {inv}",
                  (box.x + 10, box.y + 112), self.small, (220, 230, 255))
        # message log
        for i, (txt, _, col) in enumerate(game.messages):
            self.text(screen, txt, (355, S.HEIGHT - 160 + i * 22), self.font, col)
        self.text(screen, "WASD move | SHIFT sprint | E gather | SPACE attack | R eat | T drink | F cook | 1-4 craft | K skip tutorial",
                  (10, S.HEIGHT - 22), self.small, (60, 70, 90))

    # ---------------- tutorial overlay ----------------
    def draw_tutorial(self, screen, game):
        t = game.tutorial
        step = t.current()
        if not step:
            return
        box = pygame.Rect(240, 8, 520, 134)
        pygame.draw.rect(screen, (20, 35, 60), box, border_radius=10)
        pygame.draw.rect(screen, (255, 210, 80), box, 2, border_radius=10)
        self.text(screen, f"TUTORIAL {t.index + 1}/{len(t.steps)}: {step.title}",
                  (box.x + 14, box.y + 8), self.mid, (255, 210, 80))
        y = box.y + 38
        for line in wrap(self.font, step.text, box.w - 28):
            self.text(screen, line, (box.x + 14, y), self.font, (240, 245, 255))
            y += 20
        pygame.draw.rect(screen, (70, 80, 100), (box.x + 14, box.bottom - 12, box.w - 28, 6))
        pygame.draw.rect(screen, (255, 210, 80),
                         (box.x + 14, box.bottom - 12, (box.w - 28) * t.index / len(t.steps), 6))
        if t.flash > 0:
            self.text(screen, "Step complete!", (box.right - 130, box.y + 8), self.mid, (120, 240, 150))
        tp = t.target_pos(game.player)
        if tp is not None:
            sp, pc = tp - game.camera, game.player.pos - game.camera
            if self.vis(sp, 0):
                r = int(28 + 6 * abs(math.sin(pygame.time.get_ticks() / 250)))
                pygame.draw.circle(screen, (255, 210, 60), sp, r, 3)
            else:
                d = tp - game.player.pos
                if d.length() > 0:
                    d = d.normalize()
                    pygame.draw.polygon(screen, (255, 210, 60),
                                        [pc + d * 75, pc + d * 45 + d.rotate(90) * 10, pc + d * 45 + d.rotate(-90) * 10])

    # ---------------- full-screen messages ----------------
    def draw_overlay(self, screen, title, paragraphs, footer):
        shade = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        shade.fill((10, 20, 40, 225))
        screen.blit(shade, (0, 0))
        self.text(screen, title, (S.WIDTH // 2 - self.big.size(title)[0] // 2, 50), self.big, (255, 255, 255))
        y = 120
        for para in paragraphs:
            for line in wrap(self.font, para, 720):
                self.text(screen, line, (120, y), self.font, (225, 238, 255))
                y += 22
            y += 12
        self.text(screen, footer, (S.WIDTH // 2 - self.mid.size(footer)[0] // 2, S.HEIGHT - 60),
                  self.mid, (255, 210, 80))