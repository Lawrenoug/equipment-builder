from core.enums import StatType
from .attribute_set import AttributeSet


class StatsCalculator:
    def __init__(self, character):
        self.character = character

    def calculate_all_stats(self):
        self.character.attribute_set.reset()
        self._add_base_stats()
        self._calculate_equipment_stats()
        self._calculate_derived_stats()

    def _add_base_stats(self):
        attr = self.character.attribute_set
        attr.strength = self.character.base_strength
        attr.dexterity = self.character.base_dexterity
        attr.intelligence = self.character.base_intelligence
        attr.health = self.character.base_health
        attr.mana = self.character.base_mana
        attr.fire_resistance = 0
        attr.cold_resistance = 0
        attr.lightning_resistance = 0
        attr.chaos_resistance = 0
        attr.movement_speed = 100

    def _calculate_equipment_stats(self):
        for slot, item in self.character.equipment.items():
            if item:
                self._add_mods_stats(item.implicits)
                self._add_mods_stats(item.explicits)

    def _add_mods_stats(self, mods):
        attr = self.character.attribute_set

        for mod in mods:
            stat_type = mod.stat_type
            value = mod.value

            if stat_type == StatType.STRENGTH:
                attr.strength += int(value)
            elif stat_type == StatType.DEXTERITY:
                attr.dexterity += int(value)
            elif stat_type == StatType.INTELLIGENCE:
                attr.intelligence += int(value)
            elif stat_type == StatType.HEALTH:
                attr.health += int(value)
            elif stat_type == StatType.MANA:
                attr.mana += int(value)
            elif stat_type == StatType.ENERGY_SHIELD:
                attr.energy_shield += int(value)
            elif stat_type == StatType.ARMOR:
                attr.armor += int(value)
            elif stat_type == StatType.EVASION:
                attr.evasion += int(value)
            elif stat_type == StatType.FIRE_RESISTANCE:
                attr.fire_resistance += int(value)
            elif stat_type == StatType.COLD_RESISTANCE:
                attr.cold_resistance += int(value)
            elif stat_type == StatType.LIGHTNING_RESISTANCE:
                attr.lightning_resistance += int(value)
            elif stat_type == StatType.CHAOS_RESISTANCE:
                attr.chaos_resistance += int(value)
            elif stat_type == StatType.ATTACK_SPEED:
                attr.attack_speed += value
            elif stat_type == StatType.CAST_SPEED:
                attr.cast_speed += value
            elif stat_type == StatType.CRITICAL_STRIKE_CHANCE:
                attr.critical_strike_chance += value
            elif stat_type == StatType.CRITICAL_STRIKE_MULTIPLIER:
                attr.critical_strike_multiplier += value
            elif stat_type == StatType.FLAT_PHYSICAL_DAMAGE_TO_ATTACKS:
                attr.flat_physical_damage_to_attacks += int(value)
            elif stat_type == StatType.FLAT_FIRE_DAMAGE_TO_ATTACKS:
                attr.flat_fire_damage_to_attacks += int(value)
            elif stat_type == StatType.MOVEMENT_SPEED:
                attr.movement_speed += int(value)

    def _calculate_derived_stats(self):
        attr = self.character.attribute_set

        # 力量提供生命加成
        strength_health_bonus = (attr.strength // 10) * 5
        attr.health += strength_health_bonus

        # 智慧提供魔力加成
        intelligence_mana_bonus = (attr.intelligence // 10) * 5
        attr.mana += intelligence_mana_bonus

        # 抗性上限
        max_resistance = 75
        attr.fire_resistance = min(attr.fire_resistance, max_resistance)
        attr.cold_resistance = min(attr.cold_resistance, max_resistance)
        attr.lightning_resistance = min(attr.lightning_resistance, max_resistance)

        # 暴击率范围
        attr.critical_strike_chance = max(5.0, min(attr.critical_strike_chance, 95.0))
        attr.critical_strike_multiplier = max(100.0, attr.critical_strike_multiplier)