#!/usr/bin/env python3
"""
独立的SVG转PNG转换工具

使用方法:
python utils/svg_converter_tool.py [目录路径] [选项]
或者从项目根目录: python -m utils.svg_converter_tool [目录路径] [选项]
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到路径，以便导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from utils.svg_converter import SVGConverter
except ImportError:
    print("❌ 无法导入SVG转换模块，请检查依赖安装")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='SVG到PNG转换工具')
    parser.add_argument('directory', nargs='?', default='images', 
                        help='包含SVG文件的目录路径 (默认: images)')
    parser.add_argument('--width', type=int, default=512, 
                        help='PNG输出宽度 (默认: 512)')
    parser.add_argument('--height', type=int, default=512, 
                        help='PNG输出高度 (默认: 512)')
    parser.add_argument('--quality', choices=['low', 'medium', 'high'], default='high',
                        help='转换质量 (默认: high)')
    parser.add_argument('--keep-original', action='store_true', default=True,
                        help='保留原始SVG文件 (默认开启)')
    parser.add_argument('--remove-original', action='store_true',
                        help='删除原始SVG文件')
    parser.add_argument('--suffix', default='',
                        help='输出文件名后缀')
    parser.add_argument('--check-engines', action='store_true',
                        help='检查可用的转换引擎')
    
    args = parser.parse_args()
    
    # 检查转换引擎
    if args.check_engines:
        converter = SVGConverter()
        engines = converter.get_available_engines()
        print("\n🔧 可用的转换引擎:")
        for engine, available in engines.items():
            status = "✅ 可用" if available else "❌ 不可用"
            print(f"  {engine}: {status}")
        
        if not any(engines.values()):
            print("\n⚠️  警告: 没有可用的转换引擎！")
            print("请安装以下依赖包之一:")
            print("  pip install cairosvg")
            print("  pip install svglib reportlab")
        print()
        return
    
    # 处理相对路径 - 相对于项目根目录
    if not os.path.isabs(args.directory):
        directory = Path(project_root) / args.directory
    else:
        directory = Path(args.directory)
    
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    if not directory.is_dir():
        print(f"❌ 路径不是目录: {directory}")
        return
    
    # 创建转换器
    converter = SVGConverter(
        default_width=args.width,
        default_height=args.height,
        quality=args.quality
    )
    
    print(f"🔄 开始转换SVG文件...")
    print(f"📂 目录: {directory.absolute()}")
    print(f"📏 尺寸: {args.width}x{args.height}")
    print(f"🎨 质量: {args.quality}")
    
    # 执行转换
    keep_original = args.keep_original and not args.remove_original
    
    if args.suffix:
        # 使用自定义设置
        settings = {
            'width': args.width,
            'height': args.height,
            'quality': args.quality,
            'keep_original': keep_original,
            'suffix': args.suffix
        }
        stats = converter.batch_convert_with_settings(str(directory), settings)
    else:
        # 使用标准转换
        stats = converter.convert_directory(str(directory), keep_original)
    
    # 显示结果
    print("\n" + "="*50)
    print("📊 转换结果统计")
    print("="*50)
    print(f"  ✅ 转换成功: {stats['converted']} 个文件")
    print(f"  ❌ 转换失败: {stats['failed']} 个文件")
    print(f"  ⏭️  跳过文件: {stats['skipped']} 个文件")
    print("="*50)
    
    if stats['converted'] > 0:
        print("🎉 转换完成！")
        print(f"📁 请查看目录中的PNG文件: {directory.absolute()}")
    elif stats['failed'] > 0:
        print("⚠️  部分文件转换失败，请检查日志")
    else:
        print("ℹ️  未找到需要转换的SVG文件")


if __name__ == "__main__":
    main() 