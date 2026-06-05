from enum import Enum
from dataclasses import dataclass
from typing import Optional


class DamageType(Enum):
    """伤害类型枚举"""
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    CHAOS = "chaos"

@dataclass
class Skill:
    """技能数据类"""
    name: str
    base_damage: int
    damage_type: DamageType
    mana_cost: int = 0
    cast_time: float = 0.0
    crit_chance_bonus: float = 0.0
    added_damage_percentage: float = 0.0  # 额外增伤百分比
    more_damage_multiplier: float = 1.0  # 更多伤害乘数
    penetration_percentage: float = 0.0  # 抗性穿透百分比

    def __str__(self) -> str:
        return f"{self.name} ({self.damage_type.value})"

    class PresetSkills:
        @staticmethod
        def get_physical_attack():
            return Skill(
                name="猛击",
                base_damage=30,
                damage_type=DamageType.PHYSICAL,
                mana_cost=10
            )

        @staticmethod
        def get_fire_attack():
            return Skill(
                name="火球术",
                base_damage=40,
                damage_type=DamageType.FIRE,
                mana_cost=15,
                crit_chance_bonus=5.0
            )

        @staticmethod
        def get_lightning_attack():
            return Skill(
                name="闪电箭",
                base_damage=35,
                damage_type=DamageType.LIGHTNING,
                mana_cost=12,
                penetration_percentage=10.0
            )