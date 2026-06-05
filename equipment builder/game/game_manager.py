from pathlib import Path
from core.services.equipment_generator import EquipmentGenerator
from game.bench import CraftingBench
from ui.app import UIMainWindow
from character.character import Character


class Game:
    def __init__(self, root_path: Path):
        self.selected_item = None
        self.selected_item_slot_ui = None
        self.crafting_item = None
        self.crafting_item_slot_ui = None

        self.generator = EquipmentGenerator(root_path)
        self.crafting_bench = CraftingBench(self.generator.mod_pool)
        self.character = Character()

        self.ui = UIMainWindow(game_controller=self)
        self.ui._create_initial_items()

    def run(self):
        self.ui.mainloop()

    def generate_item_into_inventory(self):
        new_item = self.generator.generate_random_equipment()

        if new_item:
            was_added = self.ui.inventory_ui.add_item(new_item)
            if was_added:
                if not self.ui.inventory_ui.winfo_viewable():
                    self.ui.inventory_ui.show()
            else:
                if hasattr(self.ui, 'log_message'):
                    self.ui.log_message("物品栏已满！")

    def put_item_on_crafting_bench(self, inventory_slot_ui):
        item = inventory_slot_ui.item
        if not item:
            self.ui.log_message("请选择一件背包中的物品放入工艺台。")
            return

        self.crafting_item = item
        self.crafting_item_slot_ui = inventory_slot_ui
        if hasattr(self.ui, 'currency_stash_ui'):
            if not self.ui.currency_stash_ui.winfo_viewable():
                self.ui.currency_stash_ui.show()
            self.ui.currency_stash_ui.update_crafting_item_display()

    def _refresh_crafting_target(self):
        if self.crafting_item_slot_ui:
            self.crafting_item_slot_ui.refresh()
        if hasattr(self.ui, 'currency_stash_ui'):
            self.ui.currency_stash_ui.update_crafting_item_display()

    def _get_crafting_item(self):
        if self.crafting_item:
            return self.crafting_item
        return None

    def use_chaos_orb(self):
        item = self._get_crafting_item()
        if item:
            if self.crafting_bench.reforge_rare(item):
                self.ui.log_message(f"混沌石: {item.base_type.name} 被重铸 (移除1, 添加1)。")
                self._refresh_crafting_target()
            else:
                self.ui.log_message("无法使用混沌石。")
        else:
            self.ui.log_message("请先从物品栏中点击一件物品放入工艺台。")

    def use_exalted_orb(self):
        item = self._get_crafting_item()
        if item:
            if self.crafting_bench.exalt(item):
                self.ui.log_message(f"崇高工艺: 为 {item.base_type.name} 添加了新词缀。")
                self._refresh_crafting_target()
            else:
                self.ui.log_message("无法使用崇高工艺 (可能词缀已满)。")
        else:
            self.ui.log_message("请先从物品栏中点击一件物品放入工艺台。")

    def use_divine_orb(self):
        item = self._get_crafting_item()
        if item:
            if self.crafting_bench.divine(item):
                self.ui.log_message(f"神圣工艺: {item.base_type.name} 的词缀数值已重置。")
                self._refresh_crafting_target()
            else:
                self.ui.log_message("无法使用神圣工艺。")
        else:
            self.ui.log_message("请先从物品栏中点击一件物品放入工艺台。")

    def use_annulment_orb(self):
        item = self._get_crafting_item()
        if item:
            if self.crafting_bench.annul(item):
                self.ui.log_message(f"作废工艺: 从 {item.base_type.name} 移除了一个词缀。")
                self._refresh_crafting_target()
            else:
                self.ui.log_message("无法使用作废工艺。")
        else:
            self.ui.log_message("请先从物品栏中点击一件物品放入工艺台。")

    def equip_item(self, inventory_slot_ui):
        item_to_equip = inventory_slot_ui.item
        if not item_to_equip:
            return

        target_slot_ui = self.ui.equipment_slots_ui.get(item_to_equip.slot)
        if not target_slot_ui:
            self.ui.log_message(f"错误: 找不到 {item_to_equip.slot.name} 对应的装备槽。")
            return

        # 获取当前装备槽中的物品
        currently_equipped_item = target_slot_ui.item

        # 先尝试装备新物品
        if self.character.equip_item(item_to_equip, item_to_equip.slot):
            # 装备成功，更新UI

            # 1. 将新物品放到装备槽
            target_slot_ui.set_item(item_to_equip)

            # 2. 将原来的装备（如果有）放回物品栏
            if currently_equipped_item:
                # 寻找空的物品栏槽位
                empty_slot_found = False
                for inv_slot in self.ui.inventory_ui.slots:
                    if not inv_slot.item:
                        inv_slot.set_item(currently_equipped_item)
                        empty_slot_found = True
                        break

                if not empty_slot_found:
                    # 如果没有空槽，无法卸下旧装备，回滚装备操作
                    self.character.unequip_item(item_to_equip.slot)
                    self.character.equip_item(currently_equipped_item, currently_equipped_item.slot)
                    target_slot_ui.set_item(currently_equipped_item)
                    self.ui.log_message("物品栏已满，无法卸下当前装备！")
                    return
            else:
                # 如果原来没有装备，清空物品栏当前槽位
                inventory_slot_ui.set_item(None)

            # 3. 重要修复：无论是否有旧装备，都要清空物品栏中原本的新装备槽位
            # 只有当新装备来自物品栏（而不是装备交换）时才需要清空
            if inventory_slot_ui != target_slot_ui:
                inventory_slot_ui.set_item(None)

            # 更新角色属性显示
            self.ui.update_character_stats()
            self.ui.log_message(f"装备了: {item_to_equip.base_type.name}")

            # 如果选中的物品被装备了，更新选中状态
            if self.crafting_item is item_to_equip:
                self.crafting_item = None
                self.crafting_item_slot_ui = None
                if hasattr(self.ui, 'currency_stash_ui'):
                    self.ui.currency_stash_ui.update_crafting_item_display()

            if self.selected_item is item_to_equip:
                self.selected_item = None
                self.selected_item_slot_ui = None
                if hasattr(self.ui, 'currency_stash_ui'):
                    self.ui.currency_stash_ui.update_crafting_item_display()
        else:
            self.ui.log_message(f"无法装备: {item_to_equip.base_type.name}")

    def unequip_item(self, equipment_slot_ui):
        item_to_unequip = equipment_slot_ui.item
        if not item_to_unequip:
            return

        unequipped_item = self.character.unequip_item(item_to_unequip.slot)
        if unequipped_item:
            found_empty_slot = False
            for inv_slot in self.ui.inventory_ui.slots:
                if not inv_slot.item:
                    inv_slot.set_item(unequipped_item)
                    equipment_slot_ui.set_item(None)
                    self.ui.update_character_stats()
                    self.ui.log_message(f"卸下了: {unequipped_item.base_type.name}")
                    found_empty_slot = True
                    break

            if not found_empty_slot:
                self.ui.log_message("物品栏已满，无法卸下装备！")
                self.character.equip_item(unequipped_item, unequipped_item.slot)

    def delete_item(self, inventory_slot_ui):
        item_to_delete = inventory_slot_ui.item
        if not item_to_delete:
            return

        if self.selected_item is item_to_delete:
            self.selected_item = None
            self.selected_item_slot_ui = None
        if self.crafting_item is item_to_delete:
            self.crafting_item = None
            self.crafting_item_slot_ui = None
            self.ui.currency_stash_ui.update_crafting_item_display()

        item_name = item_to_delete.base_type.name
        inventory_slot_ui.set_item(None)  # 这会调用 refresh()
        self.ui.log_message(f"已删除: {item_name}")

        # 确保UI立即更新
        self.ui.update_idletasks()

    def start_combat_test(self, enemy_type="普通训练假人"):
        """开始战斗测试"""
        try:
            from combat import CombatUnit, Battle
            from character.attribute_set import AttributeSet

            # 创建敌人
            enemy_stats = AttributeSet()
            # ... 使用与上面相同的敌人属性设置逻辑

            enemy = CombatUnit(enemy_type, enemy_stats)
            player = CombatUnit("玩家角色", self.character.attribute_set)

            battle = Battle(player, enemy)
            return battle.fight()

        except Exception as e:
            return f"战斗测试错误: {str(e)}"
