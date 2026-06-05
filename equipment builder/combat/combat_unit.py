from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .skill import Skill
    from character.attribute_set import AttributeSet


class CombatUnit:
    """战斗单位基类 - 与现有属性系统集成"""

    def __init__(self, name: str, stats: 'AttributeSet'):
        self.name = name
        self.stats = stats

        # 基础战斗状态 - 从AttributeSet获取
        self.max_health = getattr(stats, 'health', 100)
        self.current_health = self.max_health
        self.max_mana = getattr(stats, 'mana', 50)
        self.current_mana = self.max_mana

        # 战斗状态标志
        self.is_alive = True
        self.active_effects: List[str] = []  #用于后续的buff/debuff系统

    def take_damage(self, amount: int) -> None:
        """承受伤害"""
        self.current_health = max(0, self.current_health - amount)
        if self.current_health <= 0:
            self.is_alive = False
            self.on_death()

    def heal(self, amount: int) -> None:
        """治疗"""
        if self.is_alive:
            self.current_health = min(self.max_health, self.current_health + amount)

    def use_skill(self, skill: 'Skill', target: 'CombatUnit') -> bool:
        """使用技能的基础验证"""
        if not self.is_alive:
            return False

        if self.current_mana < skill.mana_cost:
            return False

        self.current_mana -= skill.mana_cost
        return True

    def get_health_percentage(self) -> float:
        """获取生命值百分比"""
        return self.current_health / self.max_health if self.max_health > 0 else 0

    def on_death(self) -> None:
        """死亡回调"""
        print(f"{self.name} 被击败了！")

    def __str__(self) -> str:
        status = "存活" if self.is_alive else "死亡"
        return f"{self.name} [{status}] HP: {self.current_health}/{self.max_health}"