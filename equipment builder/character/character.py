from typing import Dict
from core.enums import EquipmentSlot
from core.models.item import Equipment
from .attribute_set import AttributeSet
from .inventory import Inventory


class Character:
    def __init__(self):
        self.attribute_set = AttributeSet()
        self.inventory = Inventory()
        # 延迟导入，避免循环依赖
        from .stats_calculator import StatsCalculator
        self.stats_calculator = StatsCalculator(self)

        self.equipment = {slot: None for slot in EquipmentSlot}

        # 基础属性
        self.base_strength = 10
        self.base_dexterity = 10
        self.base_intelligence = 10
        self.base_health = 50
        self.base_mana = 30

    def equip_item(self, item: Equipment, slot: EquipmentSlot) -> bool:
        if item.slot != slot:
            return False

        current_item = self.equipment[slot]
        if current_item:
            self.unequip_item(slot)

        self.equipment[slot] = item
        self._recalculate_stats()
        return True

    def unequip_item(self, slot: EquipmentSlot) -> Equipment:
        item = self.equipment[slot]
        if item:
            self.equipment[slot] = None
            self._recalculate_stats()
        return item

    def get_equipped_item(self, slot: EquipmentSlot) -> Equipment:
        return self.equipment.get(slot)

    def _recalculate_stats(self):
        self.stats_calculator.calculate_all_stats()

    def get_display_stats(self) -> Dict[str, any]:
        return self.attribute_set.to_dict()

    def get_equipment_summary(self) -> Dict[str, str]:
        summary = {}
        for slot, item in self.equipment.items():
            summary[slot.name] = item.base_type.name if item else "空"
        return summary