using System.Text;
using System.Text.Json;

namespace EquipmentBuilderCSharp;

public enum StatType
{
    Health,
    Mana,
    Armor,
    Evasion,
    EnergyShield,
    FireResistance,
    ColdResistance,
    LightningResistance,
    ChaosResistance,
    Strength,
    Dexterity,
    Intelligence,
    AttackSpeed,
    CastSpeed,
    CriticalStrikeChance,
    CriticalStrikeMultiplier,
    FlatPhysicalDamageToAttacks,
    FlatFireDamageToAttacks,
    MovementSpeed
}

public enum EquipmentFamily
{
    Helmet,
    BodyArmor,
    Gloves,
    Boots,
    Weapon,
    OffHand,
    Amulet,
    Ring,
    Belt
}

public enum EquipmentSlotId
{
    Helmet,
    BodyArmor,
    Gloves,
    Boots,
    Weapon,
    OffHand,
    Amulet,
    RingLeft,
    RingRight,
    Belt
}

public sealed class ModifierTemplate
{
    public required string Name { get; init; }
    public required StatType Stat { get; init; }
    public required int Min { get; init; }
    public required int Max { get; init; }
}

public sealed class ModifierInstance
{
    public required StatType StatType { get; init; }
    public required double Value { get; set; }
    public required bool IsPrefix { get; init; }
    public bool IsImplicit { get; init; }
    public ModifierTemplate? Template { get; init; }

    public string Describe()
    {
        if (IsImplicit)
        {
            return $"固有: {StatMetadata.FormatValue(StatType, Value)}";
        }

        var prefix = Template?.Name ?? (IsPrefix ? "前缀" : "后缀");
        return $"{prefix}: {StatMetadata.FormatValue(StatType, Value)}";
    }
}

public sealed class ItemBaseDefinition
{
    public required string Name { get; init; }
    public required EquipmentFamily Family { get; init; }
    public required Dictionary<StatType, double> BaseStats { get; init; }
    public required int RequiredLevel { get; init; }
    public required string IconPath { get; init; }

    public List<ModifierInstance> BuildImplicitModifiers()
    {
        return BaseStats
            .Select(pair => new ModifierInstance
            {
                StatType = pair.Key,
                Value = pair.Value,
                IsPrefix = true,
                IsImplicit = true
            })
            .ToList();
    }
}

public sealed class EquipmentItem
{
    public EquipmentItem(ItemBaseDefinition baseType, int itemLevel, List<ModifierInstance> implicits, List<ModifierInstance> explicits)
    {
        BaseType = baseType;
        ItemLevel = itemLevel;
        Implicits = implicits;
        Explicits = explicits;
    }

    public ItemBaseDefinition BaseType { get; }
    public int ItemLevel { get; }
    public List<ModifierInstance> Implicits { get; }
    public List<ModifierInstance> Explicits { get; }

    public IEnumerable<EquipmentSlotId> CompatibleSlots()
    {
        return BaseType.Family switch
        {
            EquipmentFamily.Helmet => new[] { EquipmentSlotId.Helmet },
            EquipmentFamily.BodyArmor => new[] { EquipmentSlotId.BodyArmor },
            EquipmentFamily.Gloves => new[] { EquipmentSlotId.Gloves },
            EquipmentFamily.Boots => new[] { EquipmentSlotId.Boots },
            EquipmentFamily.Weapon => new[] { EquipmentSlotId.Weapon },
            EquipmentFamily.OffHand => new[] { EquipmentSlotId.OffHand },
            EquipmentFamily.Amulet => new[] { EquipmentSlotId.Amulet },
            EquipmentFamily.Belt => new[] { EquipmentSlotId.Belt },
            EquipmentFamily.Ring => new[] { EquipmentSlotId.RingLeft, EquipmentSlotId.RingRight },
            _ => Array.Empty<EquipmentSlotId>()
        };
    }

    public string GetDescription()
    {
        var builder = new StringBuilder();
        builder.AppendLine(BaseType.Name);
        builder.AppendLine($"物品等级: {ItemLevel}");
        builder.AppendLine($"装备位: {StatMetadata.GetFamilyLabel(BaseType.Family)}");

        if (Implicits.Count > 0)
        {
            builder.AppendLine();
            builder.AppendLine("固有属性");
            foreach (var implicitMod in Implicits)
            {
                builder.AppendLine($"- {implicitMod.Describe()}");
            }
        }

        var prefixes = Explicits.Where(mod => mod.IsPrefix).ToList();
        var suffixes = Explicits.Where(mod => !mod.IsPrefix).ToList();

        if (prefixes.Count > 0)
        {
            builder.AppendLine();
            builder.AppendLine("前缀");
            foreach (var mod in prefixes)
            {
                builder.AppendLine($"- {mod.Describe()}");
            }
        }

        if (suffixes.Count > 0)
        {
            builder.AppendLine();
            builder.AppendLine("后缀");
            foreach (var mod in suffixes)
            {
                builder.AppendLine($"- {mod.Describe()}");
            }
        }

        builder.AppendLine();
        builder.AppendLine($"词缀数量: {Explicits.Count}/6");
        return builder.ToString().TrimEnd();
    }
}

public sealed class InventoryGrid
{
    public InventoryGrid(int capacity)
    {
        Slots = new EquipmentItem?[capacity];
    }

    public EquipmentItem?[] Slots { get; }
    public int Capacity => Slots.Length;
    public int Count => Slots.Count(item => item is not null);

    public bool AddItem(EquipmentItem item)
    {
        var index = FindFirstEmpty();
        if (index < 0)
        {
            return false;
        }

        Slots[index] = item;
        return true;
    }

    public int FindFirstEmpty()
    {
        for (var i = 0; i < Slots.Length; i++)
        {
            if (Slots[i] is null)
            {
                return i;
            }
        }

        return -1;
    }
}

public sealed class CharacterProfile
{
    public CharacterProfile()
    {
        Equipment = Enum.GetValues<EquipmentSlotId>().ToDictionary(slot => slot, _ => (EquipmentItem?)null);
        Attributes = new AttributeSet();
        Recalculate();
    }

    public Dictionary<EquipmentSlotId, EquipmentItem?> Equipment { get; }
    public AttributeSet Attributes { get; }

    public int BaseStrength { get; set; } = 10;
    public int BaseDexterity { get; set; } = 10;
    public int BaseIntelligence { get; set; } = 10;
    public int BaseHealth { get; set; } = 50;
    public int BaseMana { get; set; } = 30;

    public void Recalculate()
    {
        Attributes.Reset();
        Attributes.Strength = BaseStrength;
        Attributes.Dexterity = BaseDexterity;
        Attributes.Intelligence = BaseIntelligence;
        Attributes.Health = BaseHealth;
        Attributes.Mana = BaseMana;
        Attributes.MovementSpeed = 100;

        foreach (var item in Equipment.Values.Where(item => item is not null)!)
        {
            ApplyModifiers(item!.Implicits);
            ApplyModifiers(item.ExlicitsOrEmpty());
        }

        Attributes.Health += (Attributes.Strength / 10) * 5;
        Attributes.Mana += (Attributes.Intelligence / 10) * 5;
        Attributes.FireResistance = Math.Min(75, Attributes.FireResistance);
        Attributes.ColdResistance = Math.Min(75, Attributes.ColdResistance);
        Attributes.LightningResistance = Math.Min(75, Attributes.LightningResistance);
        Attributes.CriticalStrikeChance = Math.Clamp(Attributes.CriticalStrikeChance, 5.0, 95.0);
        Attributes.CriticalStrikeMultiplier = Math.Max(100.0, Attributes.CriticalStrikeMultiplier);
    }

    private void ApplyModifiers(IEnumerable<ModifierInstance> modifiers)
    {
        foreach (var modifier in modifiers)
        {
            var value = modifier.Value;
            switch (modifier.StatType)
            {
                case StatType.Strength:
                    Attributes.Strength += (int)value;
                    break;
                case StatType.Dexterity:
                    Attributes.Dexterity += (int)value;
                    break;
                case StatType.Intelligence:
                    Attributes.Intelligence += (int)value;
                    break;
                case StatType.Health:
                    Attributes.Health += (int)value;
                    break;
                case StatType.Mana:
                    Attributes.Mana += (int)value;
                    break;
                case StatType.Armor:
                    Attributes.Armor += (int)value;
                    break;
                case StatType.Evasion:
                    Attributes.Evasion += (int)value;
                    break;
                case StatType.EnergyShield:
                    Attributes.EnergyShield += (int)value;
                    break;
                case StatType.FireResistance:
                    Attributes.FireResistance += (int)value;
                    break;
                case StatType.ColdResistance:
                    Attributes.ColdResistance += (int)value;
                    break;
                case StatType.LightningResistance:
                    Attributes.LightningResistance += (int)value;
                    break;
                case StatType.ChaosResistance:
                    Attributes.ChaosResistance += (int)value;
                    break;
                case StatType.AttackSpeed:
                    Attributes.AttackSpeed += value;
                    break;
                case StatType.CastSpeed:
                    Attributes.CastSpeed += value;
                    break;
                case StatType.CriticalStrikeChance:
                    Attributes.CriticalStrikeChance += value;
                    break;
                case StatType.CriticalStrikeMultiplier:
                    Attributes.CriticalStrikeMultiplier += value;
                    break;
                case StatType.FlatPhysicalDamageToAttacks:
                    Attributes.FlatPhysicalDamageToAttacks += (int)value;
                    break;
                case StatType.FlatFireDamageToAttacks:
                    Attributes.FlatFireDamageToAttacks += (int)value;
                    break;
                case StatType.MovementSpeed:
                    Attributes.MovementSpeed += (int)value;
                    break;
            }
        }
    }
}

public static class EquipmentItemExtensions
{
    public static IEnumerable<ModifierInstance> ExlicitsOrEmpty(this EquipmentItem item) => item.Explicits;
}

public sealed class AttributeSet
{
    public int Strength { get; set; }
    public int Dexterity { get; set; }
    public int Intelligence { get; set; }
    public int Health { get; set; }
    public int Mana { get; set; }
    public int EnergyShield { get; set; }
    public int Armor { get; set; }
    public int Evasion { get; set; }
    public int FireResistance { get; set; }
    public int ColdResistance { get; set; }
    public int LightningResistance { get; set; }
    public int ChaosResistance { get; set; }
    public double AttackSpeed { get; set; }
    public double CastSpeed { get; set; }
    public double CriticalStrikeChance { get; set; }
    public double CriticalStrikeMultiplier { get; set; }
    public int FlatPhysicalDamageToAttacks { get; set; }
    public int FlatFireDamageToAttacks { get; set; }
    public int MovementSpeed { get; set; }

    public void Reset()
    {
        Strength = 0;
        Dexterity = 0;
        Intelligence = 0;
        Health = 0;
        Mana = 0;
        EnergyShield = 0;
        Armor = 0;
        Evasion = 0;
        FireResistance = 0;
        ColdResistance = 0;
        LightningResistance = 0;
        ChaosResistance = 0;
        AttackSpeed = 0;
        CastSpeed = 0;
        CriticalStrikeChance = 0;
        CriticalStrikeMultiplier = 0;
        FlatPhysicalDamageToAttacks = 0;
        FlatFireDamageToAttacks = 0;
        MovementSpeed = 0;
    }
}

public sealed class ModPool
{
    private readonly Random _random = new();
    private readonly List<ModifierTemplate> _prefixTemplates;
    private readonly List<ModifierTemplate> _suffixTemplates;

    public ModPool(List<ModifierTemplate> prefixTemplates, List<ModifierTemplate> suffixTemplates)
    {
        _prefixTemplates = prefixTemplates;
        _suffixTemplates = suffixTemplates;
    }

    public ModifierInstance RollPrefix()
    {
        return RollFromTemplate(_prefixTemplates[_random.Next(_prefixTemplates.Count)], true);
    }

    public ModifierInstance RollSuffix()
    {
        return RollFromTemplate(_suffixTemplates[_random.Next(_suffixTemplates.Count)], false);
    }

    public List<ModifierInstance> GenerateRandomMods(int prefixCount, int suffixCount)
    {
        var result = new List<ModifierInstance>();
        foreach (var template in _prefixTemplates.OrderBy(_ => _random.Next()).Take(Math.Min(prefixCount, _prefixTemplates.Count)))
        {
            result.Add(RollFromTemplate(template, true));
        }

        foreach (var template in _suffixTemplates.OrderBy(_ => _random.Next()).Take(Math.Min(suffixCount, _suffixTemplates.Count)))
        {
            result.Add(RollFromTemplate(template, false));
        }

        return result;
    }

    public void RerollValues(EquipmentItem item)
    {
        foreach (var modifier in item.Explicits.Where(modifier => modifier.Template is not null))
        {
            modifier.Value = _random.Next(modifier.Template!.Min, modifier.Template.Max + 1);
        }
    }

    private ModifierInstance RollFromTemplate(ModifierTemplate template, bool isPrefix)
    {
        return new ModifierInstance
        {
            StatType = template.Stat,
            Value = _random.Next(template.Min, template.Max + 1),
            IsPrefix = isPrefix,
            IsImplicit = false,
            Template = template
        };
    }
}

public sealed class EquipmentGenerator
{
    private readonly Random _random = new();
    private readonly List<ItemBaseDefinition> _itemBases;
    private readonly ModPool _modPool;

    public EquipmentGenerator(List<ItemBaseDefinition> itemBases, ModPool modPool)
    {
        _itemBases = itemBases;
        _modPool = modPool;
    }

    public EquipmentItem GenerateRandomEquipment(int itemLevel = 50)
    {
        var candidates = _itemBases.Where(item => item.RequiredLevel <= itemLevel).ToList();
        if (candidates.Count == 0)
        {
            candidates = _itemBases;
        }

        var baseType = candidates[_random.Next(candidates.Count)];
        var modifierCount = _random.Next(4, 7);
        var prefixCount = _random.Next(Math.Max(1, modifierCount - 3), Math.Min(3, modifierCount - 1) + 1);
        var suffixCount = modifierCount - prefixCount;

        return new EquipmentItem(
            baseType,
            itemLevel,
            baseType.BuildImplicitModifiers(),
            _modPool.GenerateRandomMods(prefixCount, suffixCount));
    }
}

public sealed class CraftingBench
{
    private const int MaxPrefixes = 3;
    private const int MaxSuffixes = 3;
    private readonly Random _random = new();
    private readonly ModPool _modPool;

    public CraftingBench(ModPool modPool)
    {
        _modPool = modPool;
    }

    public bool ReforgeRare(EquipmentItem item)
    {
        if (item.Explicits.Count == 0)
        {
            return false;
        }

        item.Explicits.RemoveAt(_random.Next(item.Explicits.Count));
        return Augment(item);
    }

    public bool Exalt(EquipmentItem item)
    {
        return item.Explicits.Count < MaxPrefixes + MaxSuffixes && Augment(item);
    }

    public bool Divine(EquipmentItem item)
    {
        if (item.Explicits.Count == 0)
        {
            return false;
        }

        _modPool.RerollValues(item);
        return true;
    }

    public bool Annul(EquipmentItem item)
    {
        if (item.Explicits.Count == 0)
        {
            return false;
        }

        item.Explicits.RemoveAt(_random.Next(item.Explicits.Count));
        return true;
    }

    private bool Augment(EquipmentItem item)
    {
        var prefixCount = item.Explicits.Count(modifier => modifier.IsPrefix);
        var suffixCount = item.Explicits.Count - prefixCount;
        var canAddPrefix = prefixCount < MaxPrefixes;
        var canAddSuffix = suffixCount < MaxSuffixes;

        if (!canAddPrefix && !canAddSuffix)
        {
            return false;
        }

        if (canAddPrefix && canAddSuffix)
        {
            item.Explicits.Add(_random.NextDouble() >= 0.5 ? _modPool.RollPrefix() : _modPool.RollSuffix());
            return true;
        }

        item.Explicits.Add(canAddPrefix ? _modPool.RollPrefix() : _modPool.RollSuffix());
        return true;
    }
}

public sealed class EquipmentSystemState
{
    public EquipmentSystemState(string dataDirectory)
    {
        DataDirectory = dataDirectory;
        var data = SeedDataLoader.Load(dataDirectory);
        Inventory = new InventoryGrid(50);
        Character = new CharacterProfile();
        ModPool = new ModPool(data.PrefixTemplates, data.SuffixTemplates);
        Generator = new EquipmentGenerator(data.ItemBases, ModPool);
        CraftingBench = new CraftingBench(ModPool);
    }

    public string DataDirectory { get; }
    public InventoryGrid Inventory { get; }
    public CharacterProfile Character { get; }
    public ModPool ModPool { get; }
    public EquipmentGenerator Generator { get; }
    public CraftingBench CraftingBench { get; }
}

public static class SeedDataLoader
{
    public static SeedData Load(string dataDirectory)
    {
        var itemBases = LoadItemBases(Path.Combine(dataDirectory, "item_bases.json"));
        var modifiers = LoadModifiers(Path.Combine(dataDirectory, "mods.json"));
        return new SeedData(itemBases, modifiers.PrefixTemplates, modifiers.SuffixTemplates);
    }

    private static List<ItemBaseDefinition> LoadItemBases(string path)
    {
        var document = JsonDocument.Parse(File.ReadAllText(path));
        var items = new List<ItemBaseDefinition>();

        foreach (var section in document.RootElement.EnumerateObject())
        {
            var family = ParseFamily(section.Name);
            foreach (var element in section.Value.EnumerateArray())
            {
                var stats = new Dictionary<StatType, double>();
                foreach (var stat in element.GetProperty("base_stats").EnumerateObject())
                {
                    stats.Add(ParseStatType(stat.Name), stat.Value.GetDouble());
                }

                items.Add(new ItemBaseDefinition
                {
                    Name = element.GetProperty("name").GetString() ?? "未知装备",
                    Family = family,
                    BaseStats = stats,
                    RequiredLevel = element.GetProperty("required_level").GetInt32(),
                    IconPath = element.GetProperty("icon_path").GetString() ?? string.Empty
                });
            }
        }

        return items;
    }

    private static ModifierSeed LoadModifiers(string path)
    {
        var document = JsonDocument.Parse(File.ReadAllText(path));
        return new ModifierSeed(
            LoadTemplateList(document.RootElement.GetProperty("prefix")),
            LoadTemplateList(document.RootElement.GetProperty("suffix")));
    }

    private static List<ModifierTemplate> LoadTemplateList(JsonElement array)
    {
        return array.EnumerateArray()
            .Select(element => new ModifierTemplate
            {
                Name = element.GetProperty("name").GetString() ?? "词缀",
                Stat = ParseStatType(element.GetProperty("stat").GetString() ?? string.Empty),
                Min = element.GetProperty("min").GetInt32(),
                Max = element.GetProperty("max").GetInt32()
            })
            .ToList();
    }

    private static EquipmentFamily ParseFamily(string value)
    {
        return value switch
        {
            "HELMET" => EquipmentFamily.Helmet,
            "BODY_ARMOR" => EquipmentFamily.BodyArmor,
            "GLOVES" => EquipmentFamily.Gloves,
            "BOOTS" => EquipmentFamily.Boots,
            "WEAPON" => EquipmentFamily.Weapon,
            "OFF_HAND" => EquipmentFamily.OffHand,
            "AMULET" => EquipmentFamily.Amulet,
            "RING" => EquipmentFamily.Ring,
            "BELT" => EquipmentFamily.Belt,
            _ => throw new InvalidOperationException($"未知装备分类: {value}")
        };
    }

    private static StatType ParseStatType(string value)
    {
        return value switch
        {
            "HEALTH" => StatType.Health,
            "MANA" => StatType.Mana,
            "ARMOR" => StatType.Armor,
            "EVASION" => StatType.Evasion,
            "ENERGY_SHIELD" => StatType.EnergyShield,
            "FIRE_RESISTANCE" => StatType.FireResistance,
            "COLD_RESISTANCE" => StatType.ColdResistance,
            "LIGHTNING_RESISTANCE" => StatType.LightningResistance,
            "CHAOS_RESISTANCE" => StatType.ChaosResistance,
            "STRENGTH" => StatType.Strength,
            "DEXTERITY" => StatType.Dexterity,
            "INTELLIGENCE" => StatType.Intelligence,
            "ATTACK_SPEED" => StatType.AttackSpeed,
            "CAST_SPEED" => StatType.CastSpeed,
            "CRITICAL_STRIKE_CHANCE" => StatType.CriticalStrikeChance,
            "CRITICAL_STRIKE_MULTIPLIER" => StatType.CriticalStrikeMultiplier,
            "FLAT_PHYSICAL_DAMAGE_TO_ATTACKS" => StatType.FlatPhysicalDamageToAttacks,
            "FLAT_FIRE_DAMAGE_TO_ATTACKS" => StatType.FlatFireDamageToAttacks,
            "MOVEMENT_SPEED" => StatType.MovementSpeed,
            _ => throw new InvalidOperationException($"未知属性类型: {value}")
        };
    }
}

public sealed record SeedData(List<ItemBaseDefinition> ItemBases, List<ModifierTemplate> PrefixTemplates, List<ModifierTemplate> SuffixTemplates);
public sealed record ModifierSeed(List<ModifierTemplate> PrefixTemplates, List<ModifierTemplate> SuffixTemplates);

public static class StatMetadata
{
    public static readonly (string Label, Func<AttributeSet, string> ValueFactory)[] DisplayRows =
    {
        ("力量", stats => stats.Strength.ToString()),
        ("敏捷", stats => stats.Dexterity.ToString()),
        ("智力", stats => stats.Intelligence.ToString()),
        ("生命", stats => stats.Health.ToString()),
        ("魔力", stats => stats.Mana.ToString()),
        ("能量护盾", stats => stats.EnergyShield.ToString()),
        ("护甲", stats => stats.Armor.ToString()),
        ("闪避", stats => stats.Evasion.ToString()),
        ("火焰抗性", stats => $"{stats.FireResistance}%"),
        ("冰霜抗性", stats => $"{stats.ColdResistance}%"),
        ("闪电抗性", stats => $"{stats.LightningResistance}%"),
        ("混沌抗性", stats => $"{stats.ChaosResistance}%"),
        ("攻击速度", stats => $"{stats.AttackSpeed:0.0}%"),
        ("施法速度", stats => $"{stats.CastSpeed:0.0}%"),
        ("暴击率", stats => $"{stats.CriticalStrikeChance:0.0}%"),
        ("暴击伤害", stats => $"{stats.CriticalStrikeMultiplier:0.0}%"),
        ("附加物理伤害", stats => stats.FlatPhysicalDamageToAttacks.ToString()),
        ("附加火焰伤害", stats => stats.FlatFireDamageToAttacks.ToString()),
        ("移动速度", stats => $"{stats.MovementSpeed}%")
    };

    public static string FormatValue(StatType statType, double value)
    {
        return statType switch
        {
            StatType.Health => $"+{value:0} 生命",
            StatType.Mana => $"+{value:0} 魔力",
            StatType.Armor => $"+{value:0} 护甲",
            StatType.Evasion => $"+{value:0} 闪避",
            StatType.EnergyShield => $"+{value:0} 能量护盾",
            StatType.FireResistance => $"+{value:0}% 火焰抗性",
            StatType.ColdResistance => $"+{value:0}% 冰霜抗性",
            StatType.LightningResistance => $"+{value:0}% 闪电抗性",
            StatType.ChaosResistance => $"+{value:0}% 混沌抗性",
            StatType.Strength => $"+{value:0} 力量",
            StatType.Dexterity => $"+{value:0} 敏捷",
            StatType.Intelligence => $"+{value:0} 智力",
            StatType.AttackSpeed => $"+{value:0.0}% 攻击速度",
            StatType.CastSpeed => $"+{value:0.0}% 施法速度",
            StatType.CriticalStrikeChance => $"+{value:0.0}% 暴击率",
            StatType.CriticalStrikeMultiplier => $"+{value:0.0}% 暴击伤害",
            StatType.FlatPhysicalDamageToAttacks => $"+{value:0} 物理点伤",
            StatType.FlatFireDamageToAttacks => $"+{value:0} 火焰点伤",
            StatType.MovementSpeed => $"+{value:0}% 移动速度",
            _ => $"+{value:0}"
        };
    }

    public static string GetFamilyLabel(EquipmentFamily family)
    {
        return family switch
        {
            EquipmentFamily.Helmet => "头盔",
            EquipmentFamily.BodyArmor => "胸甲",
            EquipmentFamily.Gloves => "手套",
            EquipmentFamily.Boots => "靴子",
            EquipmentFamily.Weapon => "武器",
            EquipmentFamily.OffHand => "副手",
            EquipmentFamily.Amulet => "项链",
            EquipmentFamily.Ring => "戒指",
            EquipmentFamily.Belt => "腰带",
            _ => family.ToString()
        };
    }

    public static string GetSlotLabel(EquipmentSlotId slot)
    {
        return slot switch
        {
            EquipmentSlotId.Helmet => "头盔",
            EquipmentSlotId.BodyArmor => "胸甲",
            EquipmentSlotId.Gloves => "手套",
            EquipmentSlotId.Boots => "靴子",
            EquipmentSlotId.Weapon => "武器",
            EquipmentSlotId.OffHand => "副手",
            EquipmentSlotId.Amulet => "项链",
            EquipmentSlotId.RingLeft => "左戒",
            EquipmentSlotId.RingRight => "右戒",
            EquipmentSlotId.Belt => "腰带",
            _ => slot.ToString()
        };
    }
}
