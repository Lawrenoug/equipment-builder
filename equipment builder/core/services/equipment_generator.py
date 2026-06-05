import random
import json
from pathlib import Path
from typing import List, Dict
from core.models.item import Equipment, ItemBaseType
from core.services.mod_pool import ModPool
from core.enums import EquipmentSlot


class EquipmentGenerator:
    """
    装备生成器 (工厂类)。
    负责从JSON数据加载所有装备基底和词缀池，
    并将它们组装成随机的、完整的装备。
    """

    def __init__(self, root_path: Path):
        # 1. 加载所有装备基底 "骨架"
        self.item_bases: List[ItemBaseType] = self._load_item_bases_from_json(
            root_path / "core" / "item_bases.json"
        )
        # 2. 加载词缀池 "灵魂库"
        self.mod_pool: ModPool = ModPool(
            data_file_path=root_path / "core" / "mods.json"
        )
        print("装备生成器已初始化完毕。")

    def _load_item_bases_from_json(self, file_path: Path) -> List[ItemBaseType]:
        """从 item_bases.json 加载并创建所有 ItemBaseType 对象。"""
        all_bases = []
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data: Dict[str, List[Dict]] = json.load(f)

                # data.items() 会是 ("HELMET", [...]), ("BOOTS", [...])
                for slot_str, bases_list in data.items():
                    try:
                        slot_enum = EquipmentSlot[slot_str]  # "HELMET" -> EquipmentSlot.HELMET
                        for base_data in bases_list:
                            base = ItemBaseType(
                                name=base_data['name'],
                                slot=slot_enum,
                                base_stats=base_data['base_stats'],
                                required_level=base_data['required_level'],
                                icon_path=base_data['icon_path']
                            )
                            all_bases.append(base)
                    except KeyError:
                        print(f"警告: 装备槽位 '{slot_str}' 不存在于 EquipmentSlot 枚举中，已跳过。")
            print(f"成功从 {file_path.name} 加载了 {len(all_bases)} 个装备基底。")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"!!! 错误: 加载 {file_path.name} 失败: {e}")
        return all_bases

    def generate_random_equipment(self, item_level: int = 50):
        """
        生成一件带有随机词缀的稀有(黄色)装备。
        """
        if not self.item_bases:
            print("错误: 没有任何装备基底可供选择，无法生成装备。")
            return None

        # 1. 随机挑选一个“骨架” (基底)
        random_base = random.choice(self.item_bases)

        # 2. 随机决定词缀数量 (例如，一件稀有装备有4-6个词缀)
        num_mods = random.randint(4, 6)
        num_prefixes = random.randint(max(1, num_mods - 3), min(3, num_mods - 1))  # 保证至少1前1后
        num_suffixes = num_mods - num_prefixes

        # 3. 从“灵魂库”里抽取指定数量的“灵魂” (词缀)
        random_mods = self.mod_pool.generate_random_mods(num_prefixes, num_suffixes)

        # 4. 把它们组装成一个“成品”
        new_equipment = Equipment(
            base_type=random_base,
            item_level=item_level,
            slot=random_base.slot,
            implicits=random_base.implicits,
            explicits=random_mods
        )

        return new_equipment