using System.Drawing.Drawing2D;

namespace EquipmentBuilderCSharp;

public sealed class MainForm : Form
{
    private readonly EquipmentSystemState _system;
    private readonly string _assetDirectory;
    private readonly ToolTip _toolTip = new();
    private readonly Dictionary<string, Image> _imageCache = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<int, ItemSlotPanel> _inventoryPanels = new();
    private readonly Dictionary<EquipmentSlotId, ItemSlotPanel> _equipmentPanels = new();
    private readonly List<(Label NameLabel, Label ValueLabel)> _statRows = new();
    private readonly RichTextBox _detailBox = new();
    private readonly RichTextBox _logBox = new();
    private readonly Label _selectedTitle = new();
    private readonly Label _inventorySummary = new();
    private readonly Label _craftingTargetLabel = new();
    private readonly PictureBox _previewIcon = new();
    private readonly Label _hintLabel = new();

    private EquipmentItem? _selectedItem;
    private int? _selectedInventoryIndex;
    private EquipmentSlotId? _selectedEquipmentSlot;
    private EquipmentItem? _craftingItem;
    private int? _craftingInventoryIndex;

    public MainForm()
    {
        var baseDirectory = AppContext.BaseDirectory;
        _assetDirectory = Path.Combine(baseDirectory, "Assets", "assets");
        _system = new EquipmentSystemState(Path.Combine(baseDirectory, "Data"));

        SuspendLayout();
        Text = "Echo Forge - 装备与词缀工艺台";
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(1380, 860);
        BackColor = Color.FromArgb(12, 18, 30);
        Font = new Font("Microsoft YaHei UI", 9F);

        BuildLayout();
        SeedInitialItems();
        RefreshAll();
        ResumeLayout();
    }

    protected override void OnPaintBackground(PaintEventArgs e)
    {
        using var brush = new LinearGradientBrush(ClientRectangle, Color.FromArgb(8, 13, 24), Color.FromArgb(18, 27, 42), 90f);
        e.Graphics.FillRectangle(brush, ClientRectangle);
    }

    private void BuildLayout()
    {
        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 3,
            RowCount = 2,
            Padding = new Padding(18),
            BackColor = Color.Transparent
        };
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 320));
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 320));
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 110));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

        root.Controls.Add(BuildHeaderPanel(), 0, 0);
        root.SetColumnSpan(root.GetControlFromPosition(0, 0)!, 3);
        root.Controls.Add(BuildCharacterPanel(), 0, 1);
        root.Controls.Add(BuildCenterPanel(), 1, 1);
        root.Controls.Add(BuildStatsPanel(), 2, 1);

        Controls.Add(root);
    }

    private Control BuildHeaderPanel()
    {
        var panel = CreateCard();
        panel.Padding = new Padding(18, 16, 18, 14);

        var title = new Label
        {
            Text = "Echo Forge",
            ForeColor = Color.White,
            Font = new Font("Segoe UI Semibold", 22F, FontStyle.Bold),
            Dock = DockStyle.Top,
            Height = 40
        };

        var subtitle = new Label
        {
            Text = "将 Python 装备词缀原型迁移为 C# 的独立工艺台。生成、装备、敲词缀、属性回算都在这一套里完成。",
            ForeColor = Color.FromArgb(175, 192, 214),
            Font = new Font("Microsoft YaHei UI", 9.5F),
            Dock = DockStyle.Top,
            Height = 38
        };

        var badges = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            FlowDirection = FlowDirection.LeftToRight,
            Height = 28,
            BackColor = Color.Transparent
        };
        badges.Controls.Add(CreateBadge("C# / WinForms"));
        badges.Controls.Add(CreateBadge("稀有装备生成"));
        badges.Controls.Add(CreateBadge("Chaos / Exalt / Divine / Annul"));
        badges.Controls.Add(CreateBadge("轻量 ARPG 成长验证"));

        panel.Controls.Add(badges);
        panel.Controls.Add(subtitle);
        panel.Controls.Add(title);
        return panel;
    }

    private Control BuildCharacterPanel()
    {
        var wrapper = CreateCard();
        wrapper.Padding = new Padding(14);

        var title = CreateSectionTitle("角色纸娃娃");
        wrapper.Controls.Add(title);

        var grid = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 3,
            RowCount = 4,
            BackColor = Color.Transparent,
            Padding = new Padding(6, 10, 6, 6)
        };

        for (var i = 0; i < 3; i++)
        {
            grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.33F));
        }

        for (var i = 0; i < 4; i++)
        {
            grid.RowStyles.Add(new RowStyle(SizeType.Percent, 25));
        }

        AddEquipmentSlot(grid, EquipmentSlotId.Amulet, 1, 0);
        AddEquipmentSlot(grid, EquipmentSlotId.RingLeft, 0, 1);
        AddEquipmentSlot(grid, EquipmentSlotId.Helmet, 1, 1);
        AddEquipmentSlot(grid, EquipmentSlotId.RingRight, 2, 1);
        AddEquipmentSlot(grid, EquipmentSlotId.Weapon, 0, 2);
        AddEquipmentSlot(grid, EquipmentSlotId.BodyArmor, 1, 2);
        AddEquipmentSlot(grid, EquipmentSlotId.OffHand, 2, 2);
        AddEquipmentSlot(grid, EquipmentSlotId.Gloves, 0, 3);
        AddEquipmentSlot(grid, EquipmentSlotId.Belt, 1, 3);
        AddEquipmentSlot(grid, EquipmentSlotId.Boots, 2, 3);

        wrapper.Controls.Add(grid);
        return wrapper;
    }

    private Control BuildCenterPanel()
    {
        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 3,
            BackColor = Color.Transparent
        };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 112));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 240));

        root.Controls.Add(BuildActionPanel(), 0, 0);
        root.Controls.Add(BuildInventoryPanel(), 0, 1);
        root.Controls.Add(BuildDetailsPanel(), 0, 2);
        return root;
    }

    private Control BuildActionPanel()
    {
        var panel = CreateCard();
        panel.Padding = new Padding(14);

        var title = CreateSectionTitle("工艺操作");
        panel.Controls.Add(title);

        var actions = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill,
            FlowDirection = FlowDirection.LeftToRight,
            WrapContents = true,
            BackColor = Color.Transparent,
            Padding = new Padding(0, 10, 0, 0)
        };

        actions.Controls.Add(CreateActionButton("生成稀有装备", Color.FromArgb(53, 104, 180), (_, _) => GenerateItem()));
        actions.Controls.Add(CreateActionButton("放入工艺台", Color.FromArgb(113, 83, 42), (_, _) => PutSelectedInventoryItemOnCraftingBench()));
        actions.Controls.Add(CreateActionButton("装备到身上", Color.FromArgb(64, 136, 106), (_, _) => EquipSelectedItem()));
        actions.Controls.Add(CreateActionButton("卸下装备", Color.FromArgb(78, 91, 122), (_, _) => UnequipSelectedItem()));
        actions.Controls.Add(CreateActionButton("混沌重铸", Color.FromArgb(183, 113, 36), (_, _) => ApplyCraft("混沌重铸", _system.CraftingBench.ReforgeRare)));
        actions.Controls.Add(CreateActionButton("崇高点金", Color.FromArgb(132, 92, 189), (_, _) => ApplyCraft("崇高点金", _system.CraftingBench.Exalt)));
        actions.Controls.Add(CreateActionButton("神圣洗值", Color.FromArgb(33, 132, 128), (_, _) => ApplyCraft("神圣洗值", _system.CraftingBench.Divine)));
        actions.Controls.Add(CreateActionButton("剥离词缀", Color.FromArgb(176, 75, 82), (_, _) => ApplyCraft("剥离词缀", _system.CraftingBench.Annul)));
        actions.Controls.Add(CreateActionButton("销毁物品", Color.FromArgb(92, 52, 58), (_, _) => DeleteSelectedInventoryItem()));
        _craftingTargetLabel.Width = 260;
        _craftingTargetLabel.Height = 34;
        _craftingTargetLabel.Margin = new Padding(0, 0, 10, 10);
        _craftingTargetLabel.TextAlign = ContentAlignment.MiddleLeft;
        _craftingTargetLabel.ForeColor = Color.FromArgb(232, 199, 128);
        _craftingTargetLabel.Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Bold);
        _craftingTargetLabel.Text = "工艺槽: 未放入物品";
        actions.Controls.Add(_craftingTargetLabel);

        panel.Controls.Add(actions);
        return panel;
    }

    private Control BuildInventoryPanel()
    {
        var panel = CreateCard();
        panel.Padding = new Padding(14);

        var header = new Panel
        {
            Dock = DockStyle.Top,
            Height = 38,
            BackColor = Color.Transparent
        };

        var title = CreateSectionTitle("背包");
        title.Dock = DockStyle.Left;
        _inventorySummary.Dock = DockStyle.Right;
        _inventorySummary.Width = 200;
        _inventorySummary.TextAlign = ContentAlignment.MiddleRight;
        _inventorySummary.ForeColor = Color.FromArgb(150, 170, 198);
        _inventorySummary.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);

        header.Controls.Add(_inventorySummary);
        header.Controls.Add(title);
        panel.Controls.Add(header);

        var grid = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 10,
            RowCount = 5,
            Padding = new Padding(0, 10, 0, 0),
            BackColor = Color.Transparent
        };

        for (var i = 0; i < 10; i++)
        {
            grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 10));
        }

        for (var i = 0; i < 5; i++)
        {
            grid.RowStyles.Add(new RowStyle(SizeType.Percent, 20));
        }

        for (var index = 0; index < 50; index++)
        {
            var panelSlot = new ItemSlotPanel(string.Empty, false, index, null);
            panelSlot.Clicked += (_, _) => SelectInventorySlot(index);
            panelSlot.DoubleClicked += (_, _) => EquipSelectedItem();
            panelSlot.Margin = new Padding(4);
            _inventoryPanels[index] = panelSlot;
            grid.Controls.Add(panelSlot, index % 10, index / 10);
        }

        panel.Controls.Add(grid);
        return panel;
    }

    private Control BuildDetailsPanel()
    {
        var panel = CreateCard();
        panel.Padding = new Padding(14);

        var layout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 1,
            BackColor = Color.Transparent
        };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 200));
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));

        var previewPanel = new Panel
        {
            Dock = DockStyle.Fill,
            BackColor = Color.Transparent
        };

        _selectedTitle.Text = "当前未选中物品";
        _selectedTitle.ForeColor = Color.White;
        _selectedTitle.Font = new Font("Segoe UI Semibold", 12F, FontStyle.Bold);
        _selectedTitle.Dock = DockStyle.Top;
        _selectedTitle.Height = 30;

        _previewIcon.SizeMode = PictureBoxSizeMode.Zoom;
        _previewIcon.Dock = DockStyle.Top;
        _previewIcon.Height = 132;
        _previewIcon.Margin = new Padding(0, 10, 0, 0);

        _hintLabel.Text = "左键选中背包物品后点击“放入工艺台”，工艺操作只作用于工艺槽中的装备。双击背包物品可快速装备。";
        _hintLabel.ForeColor = Color.FromArgb(148, 168, 194);
        _hintLabel.Dock = DockStyle.Fill;

        previewPanel.Controls.Add(_hintLabel);
        previewPanel.Controls.Add(_previewIcon);
        previewPanel.Controls.Add(_selectedTitle);

        _detailBox.Dock = DockStyle.Fill;
        _detailBox.ReadOnly = true;
        _detailBox.BorderStyle = BorderStyle.None;
        _detailBox.BackColor = Color.FromArgb(14, 20, 32);
        _detailBox.ForeColor = Color.FromArgb(225, 232, 240);
        _detailBox.Font = new Font("Consolas", 10F);
        _detailBox.ScrollBars = RichTextBoxScrollBars.Vertical;

        layout.Controls.Add(previewPanel, 0, 0);
        layout.Controls.Add(_detailBox, 1, 0);
        panel.Controls.Add(layout);
        return panel;
    }

    private Control BuildStatsPanel()
    {
        var panel = CreateCard();
        panel.Padding = new Padding(14);

        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 2,
            BackColor = Color.Transparent
        };
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 52));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 48));

        var statsCard = CreateInsetPanel();
        var statsTitle = CreateSectionTitle("角色属性");
        statsCard.Controls.Add(statsTitle);

        var statsRows = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = StatMetadata.DisplayRows.Length,
            Padding = new Padding(0, 10, 0, 0),
            BackColor = Color.Transparent
        };
        statsRows.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 58));
        statsRows.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 42));

        for (var i = 0; i < StatMetadata.DisplayRows.Length; i++)
        {
            statsRows.RowStyles.Add(new RowStyle(SizeType.Absolute, 24));

            var nameLabel = new Label
            {
                Text = StatMetadata.DisplayRows[i].Label,
                ForeColor = Color.FromArgb(177, 195, 218),
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleLeft
            };
            var valueLabel = new Label
            {
                ForeColor = Color.White,
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleRight,
                Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold)
            };

            _statRows.Add((nameLabel, valueLabel));
            statsRows.Controls.Add(nameLabel, 0, i);
            statsRows.Controls.Add(valueLabel, 1, i);
        }

        statsCard.Controls.Add(statsRows);
        root.Controls.Add(statsCard, 0, 0);

        var logCard = CreateInsetPanel();
        var logTitle = CreateSectionTitle("系统日志");
        logCard.Controls.Add(logTitle);

        _logBox.Dock = DockStyle.Fill;
        _logBox.ReadOnly = true;
        _logBox.BorderStyle = BorderStyle.None;
        _logBox.BackColor = Color.FromArgb(14, 20, 32);
        _logBox.ForeColor = Color.FromArgb(217, 224, 234);
        _logBox.Font = new Font("Consolas", 9F);
        _logBox.ScrollBars = RichTextBoxScrollBars.Vertical;
        _logBox.Margin = new Padding(0, 10, 0, 0);
        logCard.Controls.Add(_logBox);

        root.Controls.Add(logCard, 0, 1);
        panel.Controls.Add(root);
        return panel;
    }

    private void AddEquipmentSlot(TableLayoutPanel grid, EquipmentSlotId slot, int column, int row)
    {
        var slotPanel = new ItemSlotPanel(StatMetadata.GetSlotLabel(slot), true, null, slot)
        {
            Margin = new Padding(6)
        };
        slotPanel.Clicked += (_, _) => SelectEquipmentSlot(slot);
        slotPanel.DoubleClicked += (_, _) => UnequipSelectedItem();
        _equipmentPanels[slot] = slotPanel;
        grid.Controls.Add(slotPanel, column, row);
    }

    private void SeedInitialItems()
    {
        for (var i = 0; i < 4; i++)
        {
            _system.Inventory.AddItem(_system.Generator.GenerateRandomEquipment());
        }

        Log("已生成初始测试装备。");
    }

    private void GenerateItem()
    {
        var item = _system.Generator.GenerateRandomEquipment();
        if (_system.Inventory.AddItem(item))
        {
            Log($"生成装备: {item.BaseType.Name}");
            RefreshAll();
            return;
        }

        Log("背包已满，无法继续生成新装备。");
    }

    private void EquipSelectedItem()
    {
        if (_selectedInventoryIndex is null || _selectedItem is null)
        {
            Log("请先从背包中选择一个装备。");
            return;
        }

        var slotToUse = ResolveEquipSlot(_selectedItem);
        if (slotToUse is null)
        {
            Log($"没有找到 {StatMetadata.GetFamilyLabel(_selectedItem.BaseType.Family)} 的可用装备位。");
            return;
        }

        var inventoryIndex = _selectedInventoryIndex.Value;
        var previous = _system.Character.Equipment[slotToUse.Value];
        _system.Character.Equipment[slotToUse.Value] = _selectedItem;
        _system.Inventory.Slots[inventoryIndex] = previous;
        _system.Character.Recalculate();

        if (_craftingInventoryIndex == inventoryIndex)
        {
            ClearCraftingTarget();
        }

        SelectEquipmentSlot(slotToUse.Value);
        Log($"装备 {_selectedItem.BaseType.Name} 到 {StatMetadata.GetSlotLabel(slotToUse.Value)}。");
        RefreshAll();
    }

    private void UnequipSelectedItem()
    {
        if (_selectedEquipmentSlot is null)
        {
            Log("请先从装备栏中选择一个物品。");
            return;
        }

        var equipped = _system.Character.Equipment[_selectedEquipmentSlot.Value];
        if (equipped is null)
        {
            Log("当前装备位是空的。");
            return;
        }

        if (_system.Inventory.AddItem(equipped))
        {
            _system.Character.Equipment[_selectedEquipmentSlot.Value] = null;
            _system.Character.Recalculate();
            Log($"卸下 {equipped.BaseType.Name}。");
            ClearSelection();
            RefreshAll();
            return;
        }

        Log("背包已满，无法卸下当前装备。");
    }

    private void DeleteSelectedInventoryItem()
    {
        if (_selectedInventoryIndex is null || _selectedItem is null)
        {
            Log("只能销毁背包中的物品，请先选中一个背包格。");
            return;
        }

        var itemName = _selectedItem.BaseType.Name;
        _system.Inventory.Slots[_selectedInventoryIndex.Value] = null;
        if (_craftingInventoryIndex == _selectedInventoryIndex.Value)
        {
            ClearCraftingTarget();
        }
        ClearSelection();
        RefreshAll();
        Log($"已销毁 {itemName}。");
    }

    private void PutSelectedInventoryItemOnCraftingBench()
    {
        if (_selectedInventoryIndex is null || _selectedItem is null)
        {
            Log("请先从背包中选择一个要放入工艺台的装备。");
            return;
        }

        _craftingItem = _selectedItem;
        _craftingInventoryIndex = _selectedInventoryIndex;
        RefreshSelectionState();
        Log($"已将 {_craftingItem.BaseType.Name} 放入工艺台。");
    }

    private void ApplyCraft(string actionName, Func<EquipmentItem, bool> action)
    {
        if (_craftingItem is null)
        {
            Log($"请先将背包物品放入工艺台，再进行 {actionName}。");
            return;
        }

        if (action(_craftingItem))
        {
            _system.Character.Recalculate();
            RefreshAll();
            Log($"{actionName}: {_craftingItem.BaseType.Name}");
            return;
        }

        Log($"{actionName} 失败，当前物品不满足操作条件。");
    }

    private EquipmentSlotId? ResolveEquipSlot(EquipmentItem item)
    {
        var slots = item.CompatibleSlots().ToList();
        if (slots.Count == 0)
        {
            return null;
        }

        if (item.BaseType.Family == EquipmentFamily.Ring)
        {
            return slots.FirstOrDefault(slot => _system.Character.Equipment[slot] is null, slots[0]);
        }

        return slots[0];
    }

    private void SelectInventorySlot(int index)
    {
        var item = _system.Inventory.Slots[index];
        _selectedItem = item;
        _selectedInventoryIndex = item is null ? null : index;
        _selectedEquipmentSlot = null;
        if (item is not null)
        {
            _craftingItem = item;
            _craftingInventoryIndex = index;
        }
        RefreshSelectionState();
    }

    private void SelectEquipmentSlot(EquipmentSlotId slot)
    {
        var item = _system.Character.Equipment[slot];
        _selectedItem = item;
        _selectedInventoryIndex = null;
        _selectedEquipmentSlot = item is null ? null : slot;
        RefreshSelectionState();
    }

    private void ClearSelection()
    {
        _selectedItem = null;
        _selectedInventoryIndex = null;
        _selectedEquipmentSlot = null;
    }

    private void ClearCraftingTarget()
    {
        _craftingItem = null;
        _craftingInventoryIndex = null;
    }

    private void RefreshAll()
    {
        RefreshInventory();
        RefreshEquipment();
        RefreshStats();
        RefreshSelectionState();
        _inventorySummary.Text = $"容量 {_system.Inventory.Count}/{_system.Inventory.Capacity}";
    }

    private void RefreshInventory()
    {
        foreach (var (index, panel) in _inventoryPanels)
        {
            var item = _system.Inventory.Slots[index];
            panel.SetItem(item, false, item is not null && _selectedInventoryIndex == index, LoadItemImage(item?.BaseType.IconPath));
            _toolTip.SetToolTip(panel, item?.GetDescription() ?? "空背包格");
        }
    }

    private void RefreshEquipment()
    {
        foreach (var (slot, panel) in _equipmentPanels)
        {
            var item = _system.Character.Equipment[slot];
            var isLockedPreview = slot == EquipmentSlotId.OffHand && item is null;
            var emptyText = isLockedPreview ? "预留" : StatMetadata.GetSlotLabel(slot);
            panel.SetItem(item, true, item is not null && _selectedEquipmentSlot == slot, LoadItemImage(item?.BaseType.IconPath), emptyText);
            _toolTip.SetToolTip(panel, item?.GetDescription() ?? $"{StatMetadata.GetSlotLabel(slot)} 装备位");
        }
    }

    private void RefreshStats()
    {
        for (var i = 0; i < StatMetadata.DisplayRows.Length; i++)
        {
            var row = StatMetadata.DisplayRows[i];
            _statRows[i].ValueLabel.Text = row.ValueFactory(_system.Character.Attributes);
        }
    }

    private void RefreshSelectionState()
    {
        foreach (var (index, panel) in _inventoryPanels)
        {
            panel.Selected = _selectedInventoryIndex == index && _selectedInventoryIndex is not null;
        }

        foreach (var (slot, panel) in _equipmentPanels)
        {
            panel.Selected = _selectedEquipmentSlot == slot && _selectedEquipmentSlot is not null;
        }

        if (_selectedItem is null)
        {
            _selectedTitle.Text = "当前未选中物品";
            _detailBox.Text = "从背包或装备栏中选中一件装备后，这里会显示完整的词缀说明和当前状态。";
            _previewIcon.Image = null;
            RefreshCraftingTargetLabel();
            return;
        }

        _selectedTitle.Text = _selectedItem.BaseType.Name;
        _detailBox.Text = _selectedItem.GetDescription();
        _previewIcon.Image = LoadItemImage(_selectedItem.BaseType.IconPath);
        RefreshCraftingTargetLabel();
    }

    private void RefreshCraftingTargetLabel()
    {
        _craftingTargetLabel.Text = _craftingItem is null
            ? "工艺槽: 未放入物品"
            : $"工艺槽: {_craftingItem.BaseType.Name}";
    }

    private Image? LoadItemImage(string? iconPath)
    {
        if (string.IsNullOrWhiteSpace(iconPath))
        {
            return null;
        }

        if (_imageCache.TryGetValue(iconPath, out var cached))
        {
            return cached;
        }

        var fullPath = Path.Combine(_assetDirectory, iconPath);
        if (!File.Exists(fullPath))
        {
            return null;
        }

        using var source = Image.FromFile(fullPath);
        var canvas = new Bitmap(92, 92);
        using (var graphics = Graphics.FromImage(canvas))
        {
            graphics.Clear(Color.Transparent);
            graphics.InterpolationMode = InterpolationMode.HighQualityBicubic;
            graphics.DrawImage(source, new Rectangle(0, 0, 92, 92));
        }

        _imageCache[iconPath] = canvas;
        return canvas;
    }

    private void Log(string message)
    {
        _logBox.AppendText($"[{DateTime.Now:HH:mm:ss}] {message}{Environment.NewLine}");
        _logBox.ScrollToCaret();
    }

    private static Panel CreateCard()
    {
        return new Panel
        {
            Dock = DockStyle.Fill,
            Margin = new Padding(8),
            BackColor = Color.FromArgb(19, 28, 43)
        };
    }

    private static Panel CreateInsetPanel()
    {
        return new Panel
        {
            Dock = DockStyle.Fill,
            BackColor = Color.FromArgb(14, 20, 32),
            Padding = new Padding(12),
            Margin = new Padding(0, 0, 0, 10)
        };
    }

    private static Label CreateSectionTitle(string text)
    {
        return new Label
        {
            Text = text,
            Dock = DockStyle.Top,
            Height = 28,
            ForeColor = Color.White,
            Font = new Font("Segoe UI Semibold", 11F, FontStyle.Bold)
        };
    }

    private static Label CreateBadge(string text)
    {
        return new Label
        {
            AutoSize = true,
            Text = $"  {text}  ",
            Margin = new Padding(0, 0, 8, 0),
            Padding = new Padding(0, 4, 0, 4),
            BackColor = Color.FromArgb(28, 45, 68),
            ForeColor = Color.FromArgb(196, 214, 235),
            Font = new Font("Segoe UI", 8.5F, FontStyle.Bold)
        };
    }

    private static Button CreateActionButton(string text, Color color, EventHandler onClick)
    {
        var button = new Button
        {
            Text = text,
            Width = 126,
            Height = 34,
            Margin = new Padding(0, 0, 10, 10),
            BackColor = color,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold),
            Cursor = Cursors.Hand
        };
        button.FlatAppearance.BorderSize = 0;
        button.Click += onClick;
        return button;
    }

    private sealed class ItemSlotPanel : Panel
    {
        private readonly Label _title = new();
        private readonly PictureBox _icon = new();
        private readonly bool _equipmentStyle;
        private bool _selected;

        public ItemSlotPanel(string emptyText, bool equipmentStyle, int? inventoryIndex, EquipmentSlotId? equipmentSlot)
        {
            EmptyText = emptyText;
            _equipmentStyle = equipmentStyle;
            InventoryIndex = inventoryIndex;
            EquipmentSlot = equipmentSlot;

            Width = equipmentStyle ? 84 : 74;
            Height = equipmentStyle ? 92 : 76;
            BackColor = Color.FromArgb(10, 15, 25);
            BorderStyle = BorderStyle.FixedSingle;

            _icon.Dock = DockStyle.Fill;
            _icon.SizeMode = PictureBoxSizeMode.Zoom;
            _icon.BackColor = Color.Transparent;
            _icon.Click += (_, _) => Clicked?.Invoke(this, EventArgs.Empty);
            _icon.DoubleClick += (_, _) => DoubleClicked?.Invoke(this, EventArgs.Empty);

            _title.Dock = DockStyle.Bottom;
            _title.Height = equipmentStyle ? 24 : 18;
            _title.TextAlign = ContentAlignment.MiddleCenter;
            _title.ForeColor = Color.FromArgb(183, 198, 219);
            _title.Font = new Font("Microsoft YaHei UI", equipmentStyle ? 8F : 7.2F, FontStyle.Bold);
            _title.Click += (_, _) => Clicked?.Invoke(this, EventArgs.Empty);
            _title.DoubleClick += (_, _) => DoubleClicked?.Invoke(this, EventArgs.Empty);

            Controls.Add(_icon);
            Controls.Add(_title);
            SetItem(null, equipmentStyle, false, null, emptyText);
        }

        public string EmptyText { get; }
        public int? InventoryIndex { get; }
        public EquipmentSlotId? EquipmentSlot { get; }
        public event EventHandler? Clicked;
        public event EventHandler? DoubleClicked;

        public bool Selected
        {
            get => _selected;
            set
            {
                _selected = value;
                ApplyStyle();
            }
        }

        public void SetItem(EquipmentItem? item, bool equipmentStyle, bool selected, Image? image, string? emptyText = null)
        {
            var labelText = item?.BaseType.Name ?? emptyText ?? EmptyText;
            _title.Text = equipmentStyle && labelText.Length > 6 ? labelText[..6] : labelText;
            _icon.Image = image;
            Selected = selected;
            _icon.BackColor = item is null ? Color.FromArgb(14, 20, 32) : Color.Transparent;
        }

        private void ApplyStyle()
        {
            if (Selected)
            {
                BackColor = Color.FromArgb(46, 77, 124);
                _title.ForeColor = Color.White;
                return;
            }

            BackColor = _equipmentStyle ? Color.FromArgb(18, 26, 40) : Color.FromArgb(10, 15, 25);
            _title.ForeColor = Color.FromArgb(183, 198, 219);
        }
    }
}
