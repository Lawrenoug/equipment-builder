from typing import TYPE_CHECKING, Optional
import random

from . import BattleLog, DamageCalculator

if TYPE_CHECKING:
    from .combat_unit import CombatUnit
    from .skill import Skill


class Battle:
    """战斗管理器 - 与现有UI系统集成"""
    def __init__(self, player: 'CombatUnit', enemy: 'CombatUnit', max_rounds: int = 50):
        self.player = player
        self.enemy = enemy
        self.log = BattleLog()
        self.damage_calculator = DamageCalculator()
        self.is_battle_over = False
        self.winner: Optional['CombatUnit'] = None
        self.max_rounds = max_rounds

    def fight(self) -> str:
        """
        执行完整战斗
        返回战斗日志
        """
        self.log.add_entry(f"战斗开始！{self.player.name} vs {self.enemy.name}")

        current_attacker, current_defender = self.player, self.enemy

        while not self.is_battle_over and self.log.round_count < self.max_rounds:
            self.log.start_round()

            # 攻击方行动
            self._execute_turn(current_attacker, current_defender)
            if self._check_battle_end():
                break

            # 交换攻防
            current_attacker, current_defender = current_defender, current_attacker

            # 防御方行动
            self._execute_turn(current_attacker, current_defender)
            if self._check_battle_end():
                break

            # 换回原始顺序
            current_attacker, current_defender = current_defender, current_attacker

        if not self.is_battle_over:
            self._finish_by_round_limit()

        return self.log.get_full_log()

    def _execute_turn(self, attacker: 'CombatUnit', defender: 'CombatUnit') -> None:
        """执行单个回合"""
        # 选择技能
        skill = self._select_skill(attacker)

        if skill and attacker.use_skill(skill, defender):
            self.log.log_mana_use(attacker, skill)

            damage_result = self.damage_calculator.calculate_damage(
                attacker.stats, defender.stats, skill
            )

            defender.take_damage(damage_result["final_damage"])
            self.log.log_attack(attacker, defender, skill, damage_result)

            if not defender.is_alive:
                self.log.log_death(defender)
        else:
            self.log.add_entry(f"{attacker.name} 魔力不足，无法行动")

    def _select_skill(self, unit: 'CombatUnit') -> Optional['Skill']:
        """选择技能"""
        from .skill import Skill, DamageType

        # 根据单位属性选择技能
        strength = getattr(unit.stats, 'strength', 0)
        intelligence = getattr(unit.stats, 'intelligence', 0)
        dexterity = getattr(unit.stats, 'dexterity', 0)

        # 力量型角色使用物理攻击
        if strength >= max(intelligence, dexterity):
            skill = Skill(
                name="猛击",
                base_damage=30 + strength // 5,
                damage_type=DamageType.PHYSICAL,
                mana_cost=10,
                crit_chance_bonus=5.0
            )
        # 智力型角色使用元素攻击
        elif intelligence >= max(strength, dexterity):
            element = random.choice([DamageType.FIRE, DamageType.COLD, DamageType.LIGHTNING])
            skill = Skill(
                name=f"{element.name}冲击",
                base_damage=25 + intelligence // 4,
                damage_type=element,
                mana_cost=15,
                crit_chance_bonus=8.0
            )
        # 敏捷型角色使用快速攻击
        else:
            skill = Skill(
                name="快速打击",
                base_damage=20 + dexterity // 6,
                damage_type=DamageType.PHYSICAL,
                mana_cost=8,
                crit_chance_bonus=12.0
            )

        if getattr(unit, "current_mana", 0) >= skill.mana_cost:
            return skill

        # 魔力耗尽后使用无消耗普通攻击，避免双方空转导致UI卡死。
        return Skill(
            name="普通攻击",
            base_damage=max(8, 12 + max(strength, dexterity, intelligence) // 8),
            damage_type=DamageType.PHYSICAL,
            mana_cost=0,
            crit_chance_bonus=0.0
        )

    def _check_battle_end(self) -> bool:
        """检查战斗是否结束"""
        if not self.player.is_alive:
            self.is_battle_over = True
            self.winner = self.enemy
            self.log.add_entry(f"🎉 战斗结束！胜利者: {self.enemy.name}")
            return True
        elif not self.enemy.is_alive:
            self.is_battle_over = True
            self.winner = self.player
            self.log.add_entry(f"🎉 战斗结束！胜利者: {self.player.name}")
            return True
        return False

    def _finish_by_round_limit(self) -> None:
        """达到回合上限时按剩余生命比例判定，防止长时间阻塞UI。"""
        self.is_battle_over = True
        player_hp_rate = self.player.get_health_percentage()
        enemy_hp_rate = self.enemy.get_health_percentage()

        if player_hp_rate > enemy_hp_rate:
            self.winner = self.player
        elif enemy_hp_rate > player_hp_rate:
            self.winner = self.enemy
        else:
            self.winner = None

        if self.winner:
            self.log.add_entry(f"达到 {self.max_rounds} 回合上限，按剩余生命比例判定胜利者: {self.winner.name}")
        else:
            self.log.add_entry(f"达到 {self.max_rounds} 回合上限，双方生命比例相同，判定为平局")

    def get_winner(self) -> Optional['CombatUnit']:
        """获取胜利者"""
        return self.winner

    def is_finished(self) -> bool:
        """检查战斗是否已完成"""
        return self.is_battle_over
