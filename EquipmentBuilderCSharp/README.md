# EquipmentBuilderCSharp

这是把 `F:\Pycharm\UML\equipment builder` 里的 Python 装备与词缀原型迁成 C# 后的独立 WinForms 版本。

## 当前包含

- 稀有装备随机生成
- 背包 50 格
- 装备栏纸娃娃
- 固有词缀与显式词缀显示
- `Chaos / Exalt / Divine / Annul` 工艺逻辑
- 装备后角色属性实时回算
- 更统一的暗色 ARPG 风格桌面界面

## 运行

```powershell
dotnet run --project F:\Pycharm\UML\EquipmentBuilderCSharp\EquipmentBuilderCSharp.csproj
```

## 目录

- `MainForm.cs`
  WinForms 界面与交互逻辑
- `EquipmentSystem.cs`
  装备、词缀、背包、工艺台、属性回算核心逻辑
- `Data/`
  清理后的装备底子和词缀数据
- `Assets/assets/`
  复用原 Python 原型中的装备图标资源
