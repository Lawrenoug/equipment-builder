import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .skill import Skill
    from character.attribute_set import AttributeSet


class DamageCalculator:
    """伤害计算器 - 适配现有属性系统"""

    @staticmethod
    def calculate_damage(
            attacker_stats: 'AttributeSet',
            defender_stats: 'AttributeSet',
            skill: 'Skill'
    ) -> dict:
        """
        计算最终伤害
        返回包含详细伤害信息的字典
        """
        # 1. 基础伤害
        base_damage = skill.base_damage

        # 2. 增伤计算
        increased_damage = DamageCalculator._calculate_increased_damage(attacker_stats, skill)
        damage_after_increased = base_damage * (1 + increased_damage)

        # 3. 更多伤害计算
        more_damage = skill.more_damage_multiplier
        damage_after_more = damage_after_increased * more_damage

        # 4. 暴击计算
        crit_result = DamageCalculator._calculate_critical_hit(attacker_stats, skill, damage_after_more)
        damage_before_resistance = crit_result['damage']
        is_critical = crit_result['is_critical']

        # 5. 抗性减免计算
        resistance_result = DamageCalculator._calculate_resistance_reduction(
            defender_stats, skill, damage_before_resistance
        )

        return {
            "base_damage": base_damage,
            "damage_after_increased": round(damage_after_increased, 1),
            "damage_after_more": round(damage_after_more, 1),
            "is_critical": is_critical,
            "damage_before_resistance": round(damage_before_resistance, 1),
            "defender_resistance": resistance_result['base_resistance'],
            "effective_resistance": resistance_result['effective_resistance'],
            "final_damage": DamageCalculator._normalize_final_damage(
                damage_before_resistance,
                resistance_result['final_damage']
            ),
            "damage_type": skill.damage_type
        }

    @staticmethod
    def _calculate_increased_damage(stats: 'AttributeSet', skill: 'Skill') -> float:
        """计算增伤部分 - 适配现有属性命名"""
        increased_damage = 0.0

        if skill.damage_type.value == 'physical':
            # 力量提供物理伤害加成
            increased_damage += getattr(stats, 'strength', 0) * 0.2 / 100.0
        elif skill.damage_type.value == 'fire':
            # 智慧提供火焰伤害加成
            increased_damage += getattr(stats, 'intelligence', 0) * 0.15 / 100.0
        # 技能自带增伤
        increased_damage += skill.added_damage_percentage / 100.0

        return increased_damage

    @staticmethod
    def _calculate_critical_hit(stats: 'AttributeSet', skill: 'Skill', base_damage: float) -> dict:
        """计算暴击 - 使用现有暴击属性"""
        crit_chance_value = getattr(stats, 'critical_strike_chance', 5.0)
        if crit_chance_value <= 0:
            crit_chance_value = 5.0
        base_crit_chance = crit_chance_value / 100.0
        total_crit_chance = base_crit_chance + (skill.crit_chance_bonus / 100.0)

        is_critical = random.random() < total_crit_chance

        if is_critical:
            crit_multiplier_value = getattr(stats, 'critical_strike_multiplier', 150.0)
            if crit_multiplier_value <= 0:
                crit_multiplier_value = 150.0
            crit_multiplier = crit_multiplier_value / 100.0
            final_damage = base_damage * crit_multiplier
        else:
            final_damage = base_damage

        return {
            'damage': final_damage,
            'is_critical': is_critical
        }

    @staticmethod
    def _calculate_resistance_reduction(defender_stats: 'AttributeSet', skill: 'Skill', damage: float) -> dict:
        """计算抗性减免 - 使用现有抗性属性"""
        # 抗性属性映射
        resistance_map = {
            'physical': 'armor',
            'fire': 'fire_resistance',
            'cold': 'cold_resistance',
            'lightning': 'lightning_resistance',
            'chaos': 'chaos_resistance'
        }

        resistance_attr = resistance_map.get(skill.damage_type.value, 'armor')
        base_resistance = getattr(defender_stats, resistance_attr, 0.0)

        #护甲对物理伤害的减免
        if skill.damage_type.value == 'physical':
            # 简化版护甲计算
            denominator = base_resistance + damage * 10
            armor_multiplier = 1.0 if denominator <= 0 else max(0.1, 1 - (base_resistance / denominator))
            effective_resistance = (1 - armor_multiplier) * 100
            final_damage = damage * armor_multiplier
        else:
            # 元素抗性计算
            effective_resistance = max(-100, base_resistance - skill.penetration_percentage)
            resistance_multiplier = max(0, 1 - (effective_resistance / 100.0))
            final_damage = damage * resistance_multiplier

        return {
            'base_resistance': base_resistance,
            'effective_resistance': effective_resistance,
            'final_damage': final_damage
        }

    @staticmethod
    def _normalize_final_damage(raw_damage: float, final_damage: float) -> int:
        """保证有效攻击至少造成1点伤害，避免战斗永远无法结束。"""
        if raw_damage <= 0:
            return 0
        return max(1, round(final_damage))
