from typing import List
from datetime import datetime


class BattleLog:
    def __init__(self):
        self.entries: List[str] = []
        self.round_count = 0
        self.start_time = datetime.now()

    def add_entry(self, message: str) -> None:
        """添加日志条目"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.entries.append(f"[{timestamp}] {message}")

    def start_round(self) -> None:
        """开始新回合"""
        self.round_count += 1
        self.add_entry(f"=== 第 {self.round_count} 回合开始 ===")

    def log_attack(self, attacker, defender, skill, damage_result: dict) -> None:
        """记录攻击事件"""
        crit_text = "【暴击!】" if damage_result["is_critical"] else ""

        message = (f"{attacker.name} 对 {defender.name} 使用 {skill.name}{crit_text}, "
                   f"造成 {damage_result['final_damage']} 点{skill.damage_type.value}伤害")
        self.add_entry(message)

    def log_heal(self, unit, amount: int) -> None:
        """记录治疗事件"""
        self.add_entry(f"{unit.name} 恢复了 {amount} 点生命值")

    def log_death(self, unit) -> None:
        """记录死亡事件"""
        self.add_entry(f"💀 {unit.name} 被击败了！")

    def log_mana_use(self, unit, skill) -> None:
        """记录法力消耗"""
        self.add_entry(f"{unit.name} 消耗了 {skill.mana_cost} 点法力值")

    def get_full_log(self) -> str:
        """获取完整战斗日志"""
        return "\n".join(self.entries)

    def clear(self) -> None:
        """清空日志"""
        self.entries.clear()
        self.round_count = 0
        self.start_time = datetime.now()