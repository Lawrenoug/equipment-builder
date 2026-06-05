from abc import ABC, abstractmethod
from typing import List
from core.enums import EquipmentSlot, InfluenceType, StatType
from core.models.mod import ImplicitMod, ExplicitMod


# --- MODIFIED: ItemBaseType to be simpler ---
class ItemBaseType:
    def __init__(self, name: str, slot: EquipmentSlot, base_stats: dict, required_level: int, icon_path: str):
        self.name: str = name
        self.slot: EquipmentSlot = slot
        self.required_level: int = required_level
        self.icon_path: str = icon_path  # Just the filename, e.g. "iron_helmet.png"
        self.implicits: List[ImplicitMod] = []
        for stat_name, value in base_stats.items():
            try:
                stat_type = StatType[stat_name]
                self.implicits.append(ImplicitMod(stat_type, value))
            except KeyError:
                pass


class Item(ABC):
    def __init__(self, base_type: ItemBaseType, item_level: int):
        self.base_type = base_type
        self.item_level = item_level

    @abstractmethod
    def get_description(self) -> str: pass


# --- MODIFIED: Equipment class with REAL get_description ---
class Equipment(Item):
    def __init__(self, base_type: ItemBaseType, item_level: int, slot: EquipmentSlot,
                 implicits: List[ImplicitMod], explicits: List[ExplicitMod],
                 influence: InfluenceType = InfluenceType.NONE):
        super().__init__(base_type, item_level)
        self.slot = slot
        self.implicits = implicits
        self.explicits = explicits
        self.influence = influence

    def get_description(self) -> str:
        prefixes = [mod for mod in self.explicits if mod.is_prefix]
        suffixes = [mod for mod in self.explicits if not mod.is_prefix]

        desc = f"--- {self.base_type.name} ---\n"
        desc += f"物品等级: {self.item_level}\n"

        if self.implicits:
            desc += "--- 固有词缀 ---\n"
            for mod in self.implicits:
                desc += f"{mod.describe()}\n"

        if prefixes:
            desc += "--- 前缀 ---\n"
            for mod in prefixes:
                desc += f"{mod.describe()}\n"

        if suffixes:
            desc += "--- 后缀 ---\n"
            for mod in suffixes:
                desc += f"{mod.describe()}\n"

        return desc.strip()