from typing import Dict, Any


class AttributeSet:
    def __init__(self):
        # 基础属性
        self.strength = 0
        self.dexterity = 0
        self.intelligence = 0

        # 生存属性
        self.health = 0
        self.mana = 0
        self.energy_shield = 0

        # 防御属性
        self.armor = 0
        self.evasion = 0

        # 抗性
        self.fire_resistance = 0
        self.cold_resistance = 0
        self.lightning_resistance = 0
        self.chaos_resistance = 0

        # 攻击属性
        self.attack_speed = 0.0
        self.cast_speed = 0.0
        self.critical_strike_chance = 0.0
        self.critical_strike_multiplier = 0.0

        # 伤害加成
        self.flat_physical_damage_to_attacks = 0
        self.flat_fire_damage_to_attacks = 0

        # 功能性属性
        self.movement_speed = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "力量": self.strength,
            "敏捷": self.dexterity,
            "智慧": self.intelligence,
            "生命值": self.health,
            "魔力值": self.mana,
            "能量护盾": self.energy_shield,
            "护甲": self.armor,
            "闪避": self.evasion,
            "火焰抗性": f"{self.fire_resistance}%",
            "冰霜抗性": f"{self.cold_resistance}%",
            "闪电抗性": f"{self.lightning_resistance}%",
            "混沌抗性": f"{self.chaos_resistance}%",
            "攻击速度": f"{self.attack_speed:.1f}%",
            "施法速度": f"{self.cast_speed:.1f}%",
            "暴击率": f"{self.critical_strike_chance:.1f}%",
            "暴击伤害": f"{self.critical_strike_multiplier:.1f}%",
            "物理点伤": self.flat_physical_damage_to_attacks,
            "火焰点伤": self.flat_fire_damage_to_attacks,
            "移动速度": f"{self.movement_speed}%"
        }

    def reset(self):
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr_value = getattr(self, attr_name)
                if isinstance(attr_value, (int, float)):
                    setattr(self, attr_name, 0)