import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from game.game_manager import Game

def main():
    game_app = Game(root_path=project_root)
    game_app.run()

if __name__ == "__main__":
    main()