from abc import ABC, abstractmethod
from core.enums import StatType
from typing import Dict, Any


class Mod(ABC):
    """词缀抽象基类，定义了为角色提供属性加成的通用接口。"""
    def __init__(self, stat_type: StatType, value: float, is_prefix: bool):
        self.stat_type: StatType = stat_type  # 该词缀影响的属性类型
        self.value: float = value  # 该词缀提供的数值
        self.is_prefix: bool = is_prefix  # 词缀类型, True为前缀, False为后缀

    @abstractmethod
    def describe(self) -> str:
        """返回词缀的文本描述, 例如 '+50 最大生命值'。"""
        pass

class ExplicitMod(Mod):
    """随机词缀类，表示随机生成的“前缀”或“后缀”。"""
    def __init__(self, stat_type: StatType, value: float, is_prefix: bool, template: Dict[str, Any]):
        super().__init__(stat_type, value, is_prefix)
        self.template = template  # 新增：保存生成此词缀的原始模板

    def describe(self) -> str:
        # 例如: "巨人的(T1): +82 到 HEALTH"
        return f"{self.template['name']}: +{self.value} 到 {self.stat_type.name}"

class ImplicitMod(Mod):
    """固有词缀类，表示装备基底自带的、通常无法被工艺改变的词缀。"""
    def __init__(self, stat_type: StatType, value: float):
        # 固有词缀无前后缀之分
        super().__init__(stat_type, value, is_prefix=True)

    def describe(self) -> str:
        return f"(固有) +{self.value} 到 {self.stat_type.name}"