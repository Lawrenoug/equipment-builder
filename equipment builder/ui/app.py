import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk, ImageDraw
from typing import Dict, Optional, List
from pathlib import Path
from core.models.item import Equipment
from core.enums import EquipmentSlot

ASSETS_PATH = Path(__file__).resolve().parent / "assets"


class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, text: str):
        if self.tip_window or not text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tip_window, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


class InventorySlotUI(tk.Frame):
    def __init__(self, parent, game_controller, size=64):
        super().__init__(parent, width=size, height=size, relief="sunken", borderwidth=1, bg="#1E1E1E")
        self.pack_propagate(False)
        self.game = game_controller
        self.item: Optional[Equipment] = None
        self.label = tk.Label(self, bg="#1E1E1E")
        self.label.pack(expand=True, fill="both")
        self.tooltip = Tooltip(self)

        # 添加默认的空图片引用
        self.default_image = Image.new('RGBA', (56, 56), (30, 30, 30, 255))
        self.default_photo = ImageTk.PhotoImage(self.default_image)

        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_left_click)
        self.label.bind("<Button-3>", self.on_right_click)

    def set_item(self, item: Optional[Equipment]):
        self.item = item
        self.refresh()

    def refresh(self):
        is_selected = self.game.selected_item is self.item and self.item is not None
        bg_color = "yellow" if is_selected else "#1E1E1E"

        # 重置整个frame的背景
        self.config(bg=bg_color)

        if self.item:
            try:
                full_path = ASSETS_PATH / self.item.base_type.icon_path
                img = Image.open(full_path).resize((56, 56))
                photo = ImageTk.PhotoImage(img)
                self.label.config(image=photo, bg=bg_color, text="")
                self.label.image = photo  # 保持引用
            except FileNotFoundError:
                self.label.config(image=None, text="?", bg=bg_color)
                self.label.image = None
        else:
            # 使用默认的空图片，避免图片引用丢失
            self.label.config(
                image=self.default_photo,
                bg=bg_color,
                text=""
            )
            self.label.image = self.default_photo  # 保持默认图片引用

    def on_enter(self, event):
        if self.item:
            self.tooltip.show_tip(self.item.get_description())

    def on_leave(self, event):
        self.tooltip.hide_tip()

    def on_left_click(self, event):
        # 先刷新之前选中的槽
        if self.game.selected_item_slot_ui and self.game.selected_item_slot_ui != self:
            self.game.selected_item_slot_ui.refresh()

        self.game.selected_item = self.item
        self.game.selected_item_slot_ui = self
        self.refresh()

        if self.item:
            self.game.put_item_on_crafting_bench(self)

    # 其他方法保持不变...

    def on_right_click(self, event):
        if not self.item:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="放入工艺台", command=lambda: self.game.put_item_on_crafting_bench(self))
        menu.add_separator()
        menu.add_command(label="装备", command=lambda: self.game.equip_item(self))
        menu.add_separator()
        menu.add_command(label="删除", command=lambda: self.game.delete_item(self))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


class InventoryUI(tk.Toplevel):
    def __init__(self, parent, game_controller, rows=5, cols=10):
        super().__init__(parent)
        self.title("物品栏")
        self.geometry("680x380")
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.withdraw()
        self.configure(bg="#2E2E2E")

        self.slots: List[InventorySlotUI] = []
        for r in range(rows):
            for c in range(cols):
                slot = InventorySlotUI(self, game_controller)
                slot.grid(row=r, column=c, padx=2, pady=2)
                self.slots.append(slot)

    def show(self):
        if self.winfo_viewable():
            self.lift()
            self.focus_force()
            return
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide(self):
        self.withdraw()

    def add_item(self, item) -> bool:
        for slot in self.slots:
            if not slot.item:
                slot.set_item(item)
                return True
        print("物品栏已满！")
        return False


class EquipmentSlotUI(tk.Frame):
    def __init__(self, parent, game_controller, slot_display_name: str, icon_path, slot_type: EquipmentSlot,
                 size: int = 64):
        super().__init__(parent, width=size, height=size, relief="sunken", borderwidth=2)
        self.pack_propagate(False)
        self.game = game_controller
        self.slot_type = slot_type
        self.slot_display_name = slot_display_name
        self.size = size
        self.item: Optional[Equipment] = None

        try:
            self.default_image = Image.open(icon_path).resize((size, size))
            self.default_photo = ImageTk.PhotoImage(self.default_image)
        except (FileNotFoundError, AttributeError):
            self.default_image = Image.new('RGBA', (size, size), (50, 50, 50, 255))
            draw = ImageDraw.Draw(self.default_image)
            draw.text((10, 10), self.slot_display_name[:2], fill=(200, 200, 200))
            self.default_photo = ImageTk.PhotoImage(self.default_image)

        self.label = tk.Label(self, image=self.default_photo, bg="#3C3C3C")
        self.label.pack(expand=True, fill="both")
        self.tooltip = Tooltip(self)

        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-3>", self.on_right_click)

    def set_item(self, item: Optional[Equipment]):
        self.item = item
        self.refresh()

    def refresh(self):
        if self.item:
            try:
                full_path = ASSETS_PATH / self.item.base_type.icon_path
                img = Image.open(full_path).resize((self.size, self.size))
                photo = ImageTk.PhotoImage(img)
                self.label.config(image=photo)
                self.label.image = photo  # 保持引用
            except FileNotFoundError:
                self.label.config(image=self.default_photo)
                self.label.image = self.default_photo
        else:
            self.label.config(image=self.default_photo)
            self.label.image = self.default_photo  # 保持默认图片引用

    # 添加事件处理方法
    def on_enter(self, event):
        """鼠标进入槽位时显示工具提示"""
        if self.item:
            self.tooltip.show_tip(self.item.get_description())
        else:
            self.tooltip.show_tip(self.slot_display_name)

    def on_leave(self, event):
        """鼠标离开槽位时隐藏工具提示"""
        self.tooltip.hide_tip()

    def on_right_click(self, event):
        """右键点击显示上下文菜单"""
        if not self.item:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="卸下", command=lambda: self.game.unequip_item(self))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
class CurrencyStashUI(tk.Toplevel):
    def __init__(self, parent, game_controller):
        super().__init__(parent)
        self.game = game_controller
        self.title("工艺台")
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.withdraw()
        self.configure(bg="#2E2E2E")

        self.selected_item_frame = tk.LabelFrame(self, text="工艺槽物品", bg="#3C3C3C", fg="white", padx=10, pady=10)
        self.selected_item_frame.pack(pady=10, padx=10, fill="x")
        self.selected_item_label = tk.Label(self.selected_item_frame, text="请从物品栏中左键点击一件物品放入工艺台",
                                            bg="#3C3C3C", fg="yellow")
        self.selected_item_label.pack(anchor="w")
        self.selected_item_detail = tk.Label(
            self.selected_item_frame,
            text="工艺操作只会作用于这里显示的物品。",
            bg="#3C3C3C",
            fg="gray",
            justify=tk.LEFT,
            anchor="w"
        )
        self.selected_item_detail.pack(anchor="w", fill="x", pady=(6, 0))

        currency_frame = tk.LabelFrame(self, text="工艺选项", bg="#3C3C3C", fg="white", padx=10, pady=10)
        currency_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # 工艺按钮
        chaos_orb_btn = tk.Button(currency_frame, text="使用 混沌石", command=self.game.use_chaos_orb)
        chaos_orb_btn.pack(pady=5, fill="x")
        tk.Label(currency_frame, text="移除一个随机词缀, 并添加一个新的随机词缀。", bg="#3C3C3C", fg="gray").pack(
            anchor="w")

        exalted_craft_btn = tk.Button(currency_frame, text="崇高工艺", command=self.game.use_exalted_orb)
        exalted_craft_btn.pack(pady=(10, 5), fill="x")
        tk.Label(currency_frame, text="为物品添加一个随机词缀 (如果词缀未满)。", bg="#3C3C3C", fg="gray").pack(
            anchor="w")

        divine_craft_btn = tk.Button(currency_frame, text="神圣工艺", command=self.game.use_divine_orb)
        divine_craft_btn.pack(pady=(10, 5), fill="x")
        tk.Label(currency_frame, text="重新随机化物品上所有显式词缀的数值。", bg="#3C3C3C", fg="gray").pack(anchor="w")

        annulment_craft_btn = tk.Button(currency_frame, text="作废工艺", command=self.game.use_annulment_orb)
        annulment_craft_btn.pack(pady=(10, 5), fill="x")
        tk.Label(currency_frame, text="从物品上随机移除一个词缀。", bg="#3C3C3C", fg="gray").pack(anchor="w")

    def show(self):
        if self.winfo_viewable():
            self.lift()
            self.focus_force()
            return
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide(self):
        self.withdraw()

    def update_crafting_item_display(self):
        if self.game.crafting_item:
            desc = f"{self.game.crafting_item.base_type.name} (物品等级: {self.game.crafting_item.item_level})"
            self.selected_item_label.config(text=desc)
            self.selected_item_detail.config(text=self.game.crafting_item.get_description())
        else:
            self.selected_item_label.config(text="请从物品栏中左键点击一件物品放入工艺台")
            self.selected_item_detail.config(text="工艺操作只会作用于这里显示的物品。")

    def update_selected_item_display(self):
        self.update_crafting_item_display()


class UIMainWindow(tk.Tk):
    def __init__(self, game_controller):
        super().__init__()
        self.game = game_controller

        self.title("装备构筑系统")
        self.geometry("1200x700")
        self.configure(bg="#2E2E2E")

        self.inventory_ui = InventoryUI(self, game_controller)
        self.currency_stash_ui = CurrencyStashUI(self, game_controller)

        self.bind("<KeyPress-i>", self._handle_inventory_hotkey)
        self.bind("<KeyPress-c>", self._handle_crafting_hotkey)

        self.slot_definitions = {
            EquipmentSlot.HELMET: {"pos": (1, 1), "icon": ASSETS_PATH / "helmet.png"},
            EquipmentSlot.BODY_ARMOR: {"pos": (2, 1), "icon": ASSETS_PATH / "body_armor.png"},
            EquipmentSlot.GLOVES: {"pos": (3, 0), "icon": ASSETS_PATH / "gloves.png"},
            EquipmentSlot.BOOTS: {"pos": (3, 2), "icon": ASSETS_PATH / "boots.png"},
            EquipmentSlot.WEAPON: {"pos": (2, 0), "icon": ASSETS_PATH / "weapon.png"},
            EquipmentSlot.OFF_HAND: {"pos": (2, 2), "icon": ASSETS_PATH / "off_hand.png"},
            EquipmentSlot.AMULET: {"pos": (0, 1), "icon": ASSETS_PATH / "amulet.png"},
            EquipmentSlot.RING_1: {"pos": (1, 0), "icon": ASSETS_PATH / "ring.png"},
            EquipmentSlot.RING_2: {"pos": (1, 2), "icon": ASSETS_PATH / "ring.png"},
            EquipmentSlot.BELT: {"pos": (3, 1), "icon": ASSETS_PATH / "belt.png"},
        }
        self.equipment_slots_ui: Dict[EquipmentSlot, EquipmentSlotUI] = {}

        self._create_layout()
        self.update_character_stats()

    def _handle_inventory_hotkey(self, event=None):
        if self.inventory_ui.winfo_viewable():
            self.inventory_ui.show()
            return "break"
        if self.currency_stash_ui.winfo_viewable():
            self.currency_stash_ui.hide()
        self.inventory_ui.show()
        return "break"

    def _handle_crafting_hotkey(self, event=None):
        if self.currency_stash_ui.winfo_viewable():
            self.currency_stash_ui.show()
            return "break"
        if self.inventory_ui.winfo_viewable():
            self.inventory_ui.hide()
        self.currency_stash_ui.show()
        return "break"

    def _create_initial_items(self):
        self.game.generate_item_into_inventory()
        self.game.generate_item_into_inventory()

    def _create_layout(self):
        # 左侧面板
        left_frame = tk.Frame(self, bg="#2E2E2E", padx=10, pady=10)
        left_frame.pack(side="left", fill="y", expand=False)
        self._create_character_panel(left_frame)
        self._create_stats_panel(left_frame)
        self._create_control_panel(left_frame)

        # 中间面板
        center_frame = tk.Frame(self, bg="#2E2E2E", padx=10, pady=10)
        center_frame.pack(side="left", fill="both", expand=True)
        self._create_combat_panel(center_frame)

        # 右侧面板
        right_frame = tk.Frame(self, bg="#2E2E2E", padx=10, pady=10)
        right_frame.pack(side="right", fill="y", expand=False)
        self._create_log_panel(right_frame)

    def _create_control_panel(self, parent):
        control_frame = tk.LabelFrame(parent, text="游戏操作", bg="#3C3C3C", fg="white", padx=10, pady=10)
        control_frame.pack(side="bottom", fill="x", pady=(10, 0))

        generate_btn = tk.Button(control_frame, text="生成随机物品", command=self.game.generate_item_into_inventory)
        generate_btn.pack(fill="x")

        tk.Label(control_frame, text="按 'i' 打开物品栏\n按 'c' 打开工艺台", bg="#3C3C3C", fg="cyan").pack(pady=10)

    def _create_character_panel(self, parent):
        character_frame = tk.LabelFrame(parent, text="角色装备", bg="#3C3C3C", fg="white", padx=10, pady=10)
        character_frame.pack(side="top", fill="x", pady=(0, 10))
        for slot, props in self.slot_definitions.items():
            row, col = props["pos"]
            slot_ui = EquipmentSlotUI(character_frame, self.game, slot.name, props["icon"], slot)
            slot_ui.grid(row=row, column=col, padx=5, pady=5)
            self.equipment_slots_ui[slot] = slot_ui

    def _create_stats_panel(self, parent):
        stats_frame = tk.LabelFrame(parent, text="角色属性", bg="#3C3C3C", fg="white", padx=10, pady=10, width=280)
        stats_frame.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(stats_frame, bg="#3C3C3C", highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#3C3C3C")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.stat_labels = {}

    def update_character_stats(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.stat_labels = {}

        stats = self.game.character.get_display_stats()

        categories = {
            "基础属性": ["力量", "敏捷", "智慧"],
            "生存属性": ["生命值", "魔力值", "能量护盾"],
            "防御属性": ["护甲", "闪避"],
            "元素抗性": ["火焰抗性", "冰霜抗性", "闪电抗性", "混沌抗性"],
            "攻击属性": ["攻击速度", "施法速度", "暴击率", "暴击伤害"],
            "伤害加成": ["物理点伤", "火焰点伤"],
            "功能性": ["移动速度"]
        }

        row = 0
        for category, stat_names in categories.items():
            category_label = tk.Label(self.scrollable_frame, text=category, bg="#3C3C3C", fg="yellow",
                                      font=("Arial", 10, "bold"))
            category_label.grid(row=row, column=0, sticky="w", pady=(10, 5))
            row += 1

            for stat_name in stat_names:
                if stat_name in stats:
                    value = stats[stat_name]
                    stat_label = tk.Label(self.scrollable_frame, text=f"{stat_name}: {value}", bg="#3C3C3C", fg="white",
                                          font=("Arial", 9))
                    stat_label.grid(row=row, column=0, sticky="w", padx=10)
                    self.stat_labels[stat_name] = stat_label
                    row += 1

    def _create_combat_panel(self, parent):
        combat_frame = tk.LabelFrame(parent, text="战斗测试", bg="#3C3C3C", fg="white", padx=10, pady=10)
        combat_frame.pack(fill="both", expand=True)

        # 战斗控制按钮
        control_frame = tk.Frame(combat_frame, bg="#3C3C3C")
        control_frame.pack(pady=10, fill="x")

        start_battle_btn = tk.Button(control_frame, text="开始战斗测试",
                                     command=self._start_combat_test,
                                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        start_battle_btn.pack(side="left", padx=5)

        # 敌人选择
        enemy_frame = tk.Frame(control_frame, bg="#3C3C3C")
        enemy_frame.pack(side="left", padx=20)

        tk.Label(enemy_frame, text="敌人类型:", bg="#3C3C3C", fg="white").pack(side="left")
        self.enemy_type = tk.StringVar(value="普通训练假人")
        enemy_options = ["普通训练假人", "精英战士", "火焰法师", "敏捷盗贼"]
        enemy_menu = tk.OptionMenu(enemy_frame, self.enemy_type, *enemy_options)
        enemy_menu.config(bg="#555555", fg="white")
        enemy_menu.pack(side="left", padx=5)

        # 战斗状态显示
        status_frame = tk.Frame(combat_frame, bg="#3C3C3C")
        status_frame.pack(fill="x", pady=5)

        self.player_status = tk.Label(status_frame, text="玩家: 等待战斗开始",
                                      bg="#3C3C3C", fg="#90EE90", font=("Arial", 9))
        self.player_status.pack(side="left", padx=10)

        self.enemy_status = tk.Label(status_frame, text="敌人: 等待战斗开始",
                                     bg="#3C3C3C", fg="#FF6B6B", font=("Arial", 9))
        self.enemy_status.pack(side="right", padx=10)

        # 战斗日志显示
        log_frame = tk.Frame(combat_frame, bg="#3C3C3C")
        log_frame.pack(fill="both", expand=True)

        self.combat_log = scrolledtext.ScrolledText(log_frame, width=60, height=15,
                                                    bg="#1E1E1E", fg="white",
                                                    font=("Consolas", 9),
                                                    state="disabled")
        self.combat_log.pack(fill="both", expand=True, pady=5)

        # 清空日志按钮
        clear_btn = tk.Button(combat_frame, text="清空战斗日志",
                              command=self._clear_combat_log,
                              bg="#FF9800", fg="white")
        clear_btn.pack(pady=5)

    def _start_combat_test(self):
        """开始战斗测试"""
        try:
            from combat import CombatUnit, Battle
            from character.attribute_set import AttributeSet

            # 创建敌人属性
            enemy_stats = AttributeSet()

            # 根据选择的敌人类型设置不同属性
            enemy_type = self.enemy_type.get()
            if enemy_type == "普通训练假人":
                enemy_stats.health = 100
                enemy_stats.mana = 30
                enemy_stats.strength = 15
                enemy_stats.intelligence = 8
                enemy_stats.dexterity = 10
                enemy_stats.armor = 25
                enemy_stats.fire_resistance = 10
                enemy_stats.cold_resistance = 10
                enemy_stats.lightning_resistance = 10
            elif enemy_type == "精英战士":
                enemy_stats.health = 150
                enemy_stats.mana = 20
                enemy_stats.strength = 25
                enemy_stats.intelligence = 5
                enemy_stats.dexterity = 12
                enemy_stats.armor = 40
                enemy_stats.fire_resistance = 15
            elif enemy_type == "火焰法师":
                enemy_stats.health = 80
                enemy_stats.mana = 60
                enemy_stats.strength = 8
                enemy_stats.intelligence = 25
                enemy_stats.dexterity = 15
                enemy_stats.armor = 15
                enemy_stats.fire_resistance = 30
                enemy_stats.cold_resistance = 5
            elif enemy_type == "敏捷盗贼":
                enemy_stats.health = 90
                enemy_stats.mana = 25
                enemy_stats.strength = 12
                enemy_stats.intelligence = 10
                enemy_stats.dexterity = 25
                enemy_stats.armor = 20
                enemy_stats.evasion = 30

            enemy = CombatUnit(enemy_type, enemy_stats)

            # 使用当前角色作为玩家
            player_name = "你的角色"
            player = CombatUnit(player_name, self.game.character.attribute_set)

            # 更新状态显示
            self.player_status.config(text=f"玩家: {player.current_health}/{player.max_health} HP")
            self.enemy_status.config(text=f"敌人: {enemy.current_health}/{enemy.max_health} HP")

            # 开始战斗
            battle = Battle(player, enemy)
            battle_log = battle.fight()

            # 显示战斗日志
            self.combat_log.config(state="normal")
            self.combat_log.delete(1.0, tk.END)
            self.combat_log.insert(tk.END, battle_log)
            self.combat_log.config(state="disabled")

            # 更新最终状态
            if battle.winner:
                self.player_status.config(
                    text=f"玩家: {player.current_health}/{player.max_health} HP {'(胜利!)' if battle.winner == player else '(失败)'}")
                self.enemy_status.config(
                    text=f"敌人: {enemy.current_health}/{enemy.max_health} HP {'(胜利!)' if battle.winner == enemy else '(失败)'}")

            # 在游戏日志中也记录战斗结果
            winner_name = battle.winner.name if battle.winner else "无"
            self.log_message(f"战斗结束! 胜利者: {winner_name}")

        except Exception as e:
            error_msg = f"战斗测试错误: {str(e)}"
            self.combat_log.config(state="normal")
            self.combat_log.delete(1.0, tk.END)
            self.combat_log.insert(tk.END, error_msg)
            self.combat_log.config(state="disabled")
            self.log_message(error_msg)

    def _clear_combat_log(self):
        """清空战斗日志"""
        self.combat_log.config(state="normal")
        self.combat_log.delete(1.0, tk.END)
        self.combat_log.config(state="disabled")
        self.player_status.config(text="玩家: 等待战斗开始")
        self.enemy_status.config(text="敌人: 等待战斗开始")

    def _create_log_panel(self, parent):
        log_frame = tk.LabelFrame(parent, text="游戏日志", bg="#3C3C3C", fg="white", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, width=40, height=40, bg="#1E1E1E", fg="white",
                                                  state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log_message(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
