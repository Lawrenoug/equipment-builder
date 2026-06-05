from core.models.item import Equipment
from core.services.mod_pool import ModPool
import random


class CraftingBench:
    """工艺台：封装所有对装备进行词缀操作的方法。"""

    def __init__(self, mod_pool: ModPool):
        self.mod_pool = mod_pool
        self.MAX_PREFIXES = 3
        self.MAX_SUFFIXES = 3

    def _get_prefix_count(self, item: Equipment) -> int:
        return sum(1 for mod in item.explicits if mod.is_prefix)

    def _get_suffix_count(self, item: Equipment) -> int:
        return sum(1 for mod in item.explicits if not mod.is_prefix)

    def augment(self, item: Equipment) -> bool:
        """为物品增加一条词缀（崇高石/增幅石的基础逻辑）。"""
        prefix_count = self._get_prefix_count(item)
        suffix_count = self._get_suffix_count(item)

        can_add_prefix = prefix_count < self.MAX_PREFIXES
        can_add_suffix = suffix_count < self.MAX_SUFFIXES

        possible_actions = []
        if can_add_prefix: possible_actions.append('prefix')
        if can_add_suffix: possible_actions.append('suffix')

        if not possible_actions: return False

        if random.choice(possible_actions) == 'prefix':
            item.explicits.append(self.mod_pool.roll_prefix())
        else:
            item.explicits.append(self.mod_pool.roll_suffix())
        return True

    def reforge_rare(self, item: Equipment) -> bool:
        """
        混沌石 (Chaos Orb): 移除一个随机词缀, 并添加一个新的随机词缀。
        (参考 Path of Exile 2 的机制)
        """
        if not item.explicits:
            print("物品没有任何词缀，无法使用混沌石。")
            return False

        mod_to_remove = random.choice(item.explicits)
        item.explicits.remove(mod_to_remove)

        return self.augment(item)

    def exalt(self, item: Equipment) -> bool:
        """崇高工艺: 为稀有物品添加一条词缀。"""
        if len(item.explicits) >= (self.MAX_PREFIXES + self.MAX_SUFFIXES):
            print("物品词缀已满，无法使用崇高工艺。")
            return False
        return self.augment(item)

    def divine(self, item: Equipment) -> bool:
        """神圣工艺: 重随物品上所有显式词缀的数值。"""
        if not item.explicits:
            print("物品没有显式词缀，无法使用神圣工艺。")
            return False

        for mod in item.explicits:
            min_val = mod.template['min']
            max_val = mod.template['max']
            mod.value = random.randint(min_val, max_val)
        return True

    def annul(self, item: Equipment) -> bool:
        """作废工艺: 随机移除一条显式词缀。"""
        if not item.explicits:
            print("物品没有显式词缀，无法使用作废工艺。")
            return False

        mod_to_remove = random.choice(item.explicits)
        item.explicits.remove(mod_to_remove)
        return True