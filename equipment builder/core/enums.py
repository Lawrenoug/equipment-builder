from enum import Enum, auto


class StatType(Enum):
    """属性类型枚举，定义游戏中所有可计算的属性。"""
    # --- 基础生存属性 ---
    HEALTH = auto()  # 生命值
    MANA = auto()  # 魔力值

    # --- 基础防御属性 ---
    ARMOR = auto()  # 护甲
    EVASION = auto()  # 闪避
    ENERGY_SHIELD = auto()  # 能量护盾

    # --- 抗性 ---
    FIRE_RESISTANCE = auto()  # 火焰抗性
    COLD_RESISTANCE = auto()  # 冰霜抗性
    LIGHTNING_RESISTANCE = auto()  # 闪电抗性
    CHAOS_RESISTANCE = auto()  # 混沌抗性

    # --- 核心属性 ---
    STRENGTH = auto()  # 力量
    DEXTERITY = auto()  # 敏捷
    INTELLIGENCE = auto()  # 智慧

    # --- 攻击与施法属性 ---
    ATTACK_SPEED = auto()  # 攻击速度
    CAST_SPEED = auto()  # 施法速度
    CRITICAL_STRIKE_CHANCE = auto()  # 暴击率
    CRITICAL_STRIKE_MULTIPLIER = auto()  # 暴击伤害

    # --- 伤害点伤 (Flat Damage) ---
    FLAT_PHYSICAL_DAMAGE_TO_ATTACKS = auto()  # 附加物理点伤（攻击）
    FLAT_FIRE_DAMAGE_TO_ATTACKS = auto()  # 附加火焰点伤（攻击）
    # 可按需添加 FLAT_COLD_DAMAGE, FLAT_LIGHTNING_DAMAGE 等

    # --- 功能性属性 ---
    MOVEMENT_SPEED = auto()  # 移动速度

class EquipmentSlot(Enum):
    HELMET = auto()
    BODY_ARMOR = auto()
    GLOVES = auto()
    BOOTS = auto()
    WEAPON = auto()
    OFF_HAND = auto()
    AMULET = auto()
    RING_1 = auto()
    RING_2 = auto()
    BELT = auto()


class InfluenceType(Enum):
    NONE = auto()
    SHAPER = auto()
    ELDER = auto()
    CRUSADER = auto()
    REDEEMER = auto()
    HUNTER = auto()
    WARLORD = auto()


class DamageType(Enum):
    PHYSICAL = auto()
    FIRE = auto()
    COLD = auto()
    LIGHTNING = auto()
    CHAOS = auto()