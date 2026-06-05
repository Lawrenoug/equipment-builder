from enum import Enum

class SocketColor(Enum):
    """插槽颜色枚举。"""
    RED = 'R'  # 红色 (力量)
    GREEN = 'G'  # 绿色 (敏捷)
    BLUE = 'B'  # 蓝色 (智慧)
    WHITE = 'W'  # 白色 (通用)

class Socket:
    """插槽类，管理技能石的镶嵌孔位和它们之间的连接关系。"""
    def __init__(self, color: SocketColor, group_id: int):
        self.color: SocketColor = color  # 插槽的颜色
        self.group_id: int = group_id  # 插槽的连接组ID, 相同ID的插槽视为互相连接

    def __repr__(self):
        return f"Socket(颜色={self.color.name}, 连接组={self.group_id})"