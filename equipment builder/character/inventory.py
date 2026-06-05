from typing import List, Optional
from core.models.item import Equipment


class Inventory:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.items: List[Equipment] = []

    def add_item(self, item: Equipment) -> bool:
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item: Equipment) -> bool:
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def remove_item_at(self, index: int) -> Optional[Equipment]:
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def get_item_count(self) -> int:
        return len(self.items)

    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def get_items(self) -> List[Equipment]:
        return self.items.copy()