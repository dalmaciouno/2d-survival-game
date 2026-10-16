# items.py
import settings as S

class Inventory:
    """Stores item counts, enforces capacity, and handles crafting costs."""
    def __init__(self, capacity=S.CAPACITY):
        self.items = {}
        self.capacity = capacity

    def count(self, name):
        return self.items.get(name, 0)

    def total(self):
        return sum(self.items.values())

    def add(self, name, qty):
        room = self.capacity - self.total()
        qty = max(0, min(qty, room))          # never exceed capacity
        if qty:
            self.items[name] = self.count(name) + qty
        return qty                             # how many were really added

    def remove(self, name, qty=1):
        if self.count(name) < qty:
            return False
        self.items[name] -= qty
        if self.items[name] == 0:
            del self.items[name]
        return True

    def missing(self, cost):
        return {k: v - self.count(k) for k, v in cost.items() if self.count(k) < v}

    def can_afford(self, cost):
        if S.BUGS["craft_check"]:              # BUG-02: any() instead of all()
            return any(self.count(k) >= v for k, v in cost.items())
        return all(self.count(k) >= v for k, v in cost.items())   # FIX

    def craft(self, name):
        cost = S.RECIPES[name]["cost"]
        if not self.can_afford(cost):
            need = ", ".join(f"{v} {k}" for k, v in self.missing(cost).items())
            return False, f"Not enough materials - need {need} more."
        for k, v in cost.items():
            self.items[k] = max(0, self.count(k) - v)
        self.items = {k: v for k, v in self.items.items() if v > 0}
        return True, "ok"