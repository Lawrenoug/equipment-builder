#!/usr/bin/env python3
"""
通用 Python 代码提取器 - 提取所有 .py 文件内容
支持多项目结构
"""

import os
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class PythonCodeExtractor:
    def __init__(self, project_root=".", max_file_size=100000):  # 100KB 限制
        self.root = Path(project_root).absolute()
        self.output_lines = []
        self.max_file_size = max_file_size
        self.stats = {
            'py_files': [],
            'total_lines': 0,
            'total_size': 0,
            'module_info': {}
        }

    def extract_all_python_code(self):
        """提取所有 Python 文件代码"""
        print(f"🐍 正在提取 Python 代码: {self.root}")

        self._create_header()
        self._extract_python_files()
        self._analyze_project_structure()
        self._save_extracted_code()

        return self._get_output_file()

    def _create_header(self):
        """创建文件头"""
        self.output_lines.append("# 🐍 Python 项目完整代码库")
        self.output_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.output_lines.append(f"项目路径: {self.root}")
        self.output_lines.append(f"Python 版本: {self._get_python_version()}")
        self.output_lines.append("\n---\n")

    def _get_python_version(self):
        """获取 Python 版本"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _extract_python_files(self):
        """提取所有 Python 文件"""
        py_files = list(self.root.rglob("*.py"))

        if not py_files:
            self.output_lines.append("## 📄 Python 文件\n")
            self.output_lines.append("未找到 .py 文件\n")
            return

        self.output_lines.append("## 📄 Python 文件\n")
        self.output_lines.append(f"共找到 {len(py_files)} 个 Python 文件\n")

        for py_file in sorted(py_files):
            self._process_python_file(py_file)

    def _process_python_file(self, py_file: Path):
        """处理单个 Python 文件"""
        try:
            file_size = os.path.getsize(py_file)

            # 检查文件大小
            if file_size > self.max_file_size:
                print(f"⚠️  跳过大文件: {py_file} ({file_size / 1024:.1f}KB)")
                self.output_lines.append(f"### ⚠️ {py_file.relative_to(self.root)}")
                self.output_lines.append(f"文件过大 ({file_size / 1024:.1f}KB)，已跳过\n")
                return

            rel_path = py_file.relative_to(self.root)
            self.stats['py_files'].append(str(rel_path))

            # 读取文件内容
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 计算行数
            lines = content.split('\n')
            line_count = len(lines)

            # 提取模块信息
            module_info = self._analyze_module_content(content, py_file)
            self.stats['module_info'][str(rel_path)] = module_info

            # 添加到输出
            self.output_lines.append(f"### 📄 {rel_path}")
            self.output_lines.append(f"**大小**: {file_size:,} 字节 | **行数**: {line_count}")

            # 显示模块信息
            if module_info:
                self._append_module_info(module_info)

            self.output_lines.append("\n**完整代码:**")
            self.output_lines.append("```python")
            self.output_lines.append(content)
            self.output_lines.append("```\n")

            # 添加分隔线
            self.output_lines.append("---\n")

            # 更新统计
            self.stats['total_lines'] += line_count
            self.stats['total_size'] += file_size

        except Exception as e:
            rel_path = py_file.relative_to(self.root)
            self.output_lines.append(f"### ❌ {rel_path}")
            self.output_lines.append(f"读取失败: {str(e)}\n")

    def _analyze_module_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """分析模块内容"""
        module_info = {
            'imports': [],
            'functions': [],
            'classes': [],
            'variables': [],
            'docstring': ''
        }

        try:
            # 尝试使用 AST 解析
            tree = ast.parse(content)

            # 提取文档字符串
            if ast.get_docstring(tree):
                module_info['docstring'] = ast.get_docstring(tree)[:200] + "..."

            # 提取导入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        module_info['imports'].append(f"{module}.{alias.name}")

                # 提取函数定义
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': len(node.args.args),
                        'has_docstring': bool(ast.get_docstring(node))
                    }
                    module_info['functions'].append(func_info)

                # 提取类定义
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'bases': [ast.unparse(base) for base in node.bases],
                        'has_docstring': bool(ast.get_docstring(node)),
                        'methods': []
                    }

                    # 提取类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append(item.name)

                    module_info['classes'].append(class_info)

        except Exception as e:
            # 如果 AST 解析失败，使用正则表达式简单提取
            module_info['imports'] = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(\S+)', content, re.MULTILINE)
            module_info['functions'] = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
            module_info['classes'] = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)

        return module_info

    def _append_module_info(self, module_info: Dict[str, Any]):
        """附加模块信息到输出"""
        if module_info['imports']:
            imports_str = ', '.join(module_info['imports'][:10])
            self.output_lines.append(f"**导入**: {imports_str}")
            if len(module_info['imports']) > 10:
                self.output_lines.append(f"  ... 还有 {len(module_info['imports']) - 10} 个导入")

        if module_info['docstring']:
            self.output_lines.append(f"**文档**: {module_info['docstring']}")

        if module_info['classes']:
            class_info = []
            for cls in module_info['classes'][:5]:
                info = cls['name']
                if cls['bases']:
                    info += f"({', '.join(cls['bases'])})"
                if cls['methods']:
                    info += f" [方法: {', '.join(cls['methods'][:3])}]"
                class_info.append(info)

            self.output_lines.append(f"**类**: {', '.join(class_info)}")
            if len(module_info['classes']) > 5:
                self.output_lines.append(f"  还有 {len(module_info['classes']) - 5} 个类")

        if module_info['functions']:
            func_info = []
            for func in module_info['functions'][:5]:
                if isinstance(func, dict):
                    info = f"{func['name']}({func['args']}参数)"
                    if func['has_docstring']:
                        info += " 📝"
                    func_info.append(info)
                else:
                    func_info.append(func)

            self.output_lines.append(f"**函数**: {', '.join(func_info)}")
            if len(module_info['functions']) > 5:
                self.output_lines.append(f"  还有 {len(module_info['functions']) - 5} 个函数")

    def _analyze_project_structure(self):
        """分析项目结构"""
        self.output_lines.append("\n## 📁 项目结构分析\n")

        # 分析目录结构
        dir_structure = {}
        for py_file in self.stats['py_files']:
            file_path = Path(py_file)
            parent = file_path.parent

            if parent not in dir_structure:
                dir_structure[parent] = []

            dir_structure[parent].append(file_path.name)

        # 显示目录结构
        self.output_lines.append("### 目录结构\n")
        for dir_path in sorted(dir_structure.keys()):
            files = dir_structure[dir_path]
            self.output_lines.append(f"**{dir_path if dir_path != Path('..') else '根目录'}**")
            for file in sorted(files)[:5]:  # 每个目录最多显示5个文件
                self.output_lines.append(f"- `{file}`")

            if len(files) > 5:
                self.output_lines.append(f"  ... 还有 {len(files) - 5} 个文件")

            self.output_lines.append("")

    def _save_extracted_code(self):
        """保存提取的代码"""
        # 添加统计信息
        self.output_lines.append("\n---\n")
        self.output_lines.append("## 📊 统计信息\n")

        self.output_lines.append(f"- **Python 文件总数**: {len(self.stats['py_files'])}")
        self.output_lines.append(f"- **总代码行数**: {self.stats['total_lines']:,}")
        self.output_lines.append(f"- **总文件大小**: {self.stats['total_size'] / 1024:.1f} KB")

        # 显示文件列表
        if self.stats['py_files']:
            self.output_lines.append("\n### 文件列表")
            for i, file_path in enumerate(self.stats['py_files'][:20], 1):
                self.output_lines.append(f"{i:2d}. `{file_path}`")

            if len(self.stats['py_files']) > 20:
                self.output_lines.append(f"... 还有 {len(self.stats['py_files']) - 20} 个文件")

        # 保存到文件
        output_file = self.root / "PYTHON_CODE_EXTRACT.md"
        content = '\n'.join(self.output_lines)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ Python 代码提取完成!")
        print(f"📄 输出文件: {output_file}")
        print(f"📏 文件大小: {len(content.encode('utf-8')) / 1024:.1f} KB")
        print(f"📝 总文件数: {len(self.stats['py_files'])}")
        print(f"🔤 总代码行: {self.stats['total_lines']:,}")

    def _get_output_file(self):
        """获取输出文件路径"""
        return self.root / "PYTHON_CODE_EXTRACT.md"


def main():
    """主函数"""
    print("🚀 Python 项目代码提取器")
    print("=" * 60)
    print("📝 功能: 提取所有 .py 文件的完整代码内容")
    print("🎯 用途: 代码分析、文档生成、AI 辅助编程\n")

    import sys

    # 获取项目路径
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = ".."

    root = Path(project_path).absolute()
    print(f"目标目录: {root}")

    if not root.exists():
        print(f"❌ 错误: 目录不存在 - {root}")
        return

    # 设置文件大小限制
    max_size_input = input("设置最大文件大小限制 (KB, 默认 100): ").strip()
    if max_size_input:
        try:
            max_size_kb = int(max_size_input)
            max_size = max_size_kb * 1024
        except:
            max_size = 100 * 1024
            print(f"⚠️  输入无效，使用默认值: 100KB")
    else:
        max_size = 100 * 1024

    print(f"\n🔄 正在扫描 Python 项目...")

    try:
        extractor = PythonCodeExtractor(project_path, max_file_size=max_size)
        output_file = extractor.extract_all_python_code()

        print(f"\n🎯 输出文件: {output_file}")
        print("📤 可以直接上传给 AI 进行分析")

        # 询问是否查看示例
        if input("\n查看文件示例? (y/n): ").lower() == 'y':
            with open(output_file, 'r', encoding='utf-8') as f:
                for _ in range(30):
                    line = f.readline()
                    if not line:
                        break
                    print(line.rstrip())
                print("...")

    except KeyboardInterrupt:
        print("\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()