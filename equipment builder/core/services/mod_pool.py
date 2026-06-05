import random
import json
from typing import List, Dict, Any
from pathlib import Path
from core.models.mod import ExplicitMod
from core.enums import StatType


class ModPool:
    """
    词缀池服务类。
    管理所有可能的词缀模板，并提供根据规则随机生成词缀的功能。
    词缀数据从外部 mods.json 文件加载。
    """

    def __init__(self, data_file_path: str = "core/mods.json"):
        """
        初始化时，从指定的JSON文件加载所有词缀模板。
        """
        self._mod_templates: Dict[str, List[Dict[str, Any]]] = self._load_mods_from_file(data_file_path)

    def _load_mods_from_file(self, file_path: str) -> Dict:
        """一个私有方法，专门用于读取和解析JSON文件。"""
        try:
            path = Path(file_path)
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"错误：找不到词缀数据文件 at '{file_path}'")
            return {"prefix": [], "suffix": []}
        except json.JSONDecodeError:
            print(f"错误：词缀数据文件 '{file_path}' 格式不正确。")
            return {"prefix": [], "suffix": []}

    def _roll_from_template(self, template: Dict, is_prefix: bool) -> ExplicitMod:
        """内部辅助函数，从单个模板生成词缀"""
        stat_enum_member = StatType[template['stat']]
        value = random.randint(template['min'], template['max'])
        return ExplicitMod(
            stat_type=stat_enum_member,
            value=value,
            is_prefix=is_prefix,
            template=template  # <-- 传入模板
        )

    def roll_prefix(self) -> ExplicitMod:
        """从前缀池中随机抽取并生成一个前缀词缀。"""
        template = random.choice(self._mod_templates['prefix'])
        return self._roll_from_template(template, is_prefix=True)

    def roll_suffix(self) -> ExplicitMod:
        """从后缀池中随机抽取并生成一个后缀词缀。"""
        template = random.choice(self._mod_templates['suffix'])
        return self._roll_from_template(template, is_prefix=False)

    def generate_random_mods(self, num_prefixes: int, num_suffixes: int) -> List[ExplicitMod]:
        """
        为一件装备生成一组指定数量的随机词缀。
        """
        mods = []

        # Clamp values to avoid asking for more mods than available in the pool
        num_prefixes = min(num_prefixes, len(self._mod_templates['prefix']))
        num_suffixes = min(num_suffixes, len(self._mod_templates['suffix']))

        # Get unique prefixes
        prefix_templates = random.sample(self._mod_templates['prefix'], num_prefixes)
        for template in prefix_templates:
            mods.append(self._roll_from_template(template, is_prefix=True))

        # Get unique suffixes
        suffix_templates = random.sample(self._mod_templates['suffix'], num_suffixes)
        for template in suffix_templates:
            mods.append(self._roll_from_template(template, is_prefix=False))

        return mods