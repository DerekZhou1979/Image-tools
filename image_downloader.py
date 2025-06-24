#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image-tools v4.0 通用图片下载器
"""
import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
import time
from typing import Dict, List, Optional, Union

# --- 动态路径设置 ---
# 确保在任何情况下都能从项目根目录正确导入模块
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 引擎导入 ---
try:
    from engines.base_engine import BaseImageEngine, ImageInfo
    from engines.legacy_engine import LegacyImageEngine
    ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"❌ 关键引擎模块导入失败: {e}。请检查项目结构。")
    sys.exit(1)

# --- Playwright引擎懒加载 ---
PLAYWRIGHT_AVAILABLE = False
try:
    from engines.playwright_engine import PlaywrightImageEngine
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass # 如果不可用，将在逻辑中处理

class ImageDownloader:
    """v4.0 主下载器类"""
    def __init__(self, config_file: str = 'image_download_config.json'):
        self.config_file = os.path.join(project_root, config_file)
        self.load_config()
        self.base_url = self.config.get('base_url', '')
        self.images_dir = Path(os.path.join(project_root, 'images'))
        self.engine: Optional[BaseImageEngine] = None
        self.engine_type = None
        self.stats = {'start_time': time.time()}
        self.images_dir.mkdir(exist_ok=True)

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 配置文件加载成功: {self.config_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ 配置文件错误: {e}. 程序将退出。")
            sys.exit(1)

    def _determine_engine_type(self, force_engine: Optional[str]) -> str:
        if force_engine and force_engine in ['playwright', 'legacy']:
            return force_engine
        
        default_engine = self.config.get('engine_settings', {}).get('default_engine', 'auto')
        
        if default_engine == 'auto':
            return 'playwright' if PLAYWRIGHT_AVAILABLE else 'legacy'
        return default_engine

    async def _create_engine(self, engine_type: str) -> BaseImageEngine:
        """创建并初始化引擎"""
        if engine_type == 'playwright':
            if not PLAYWRIGHT_AVAILABLE:
                raise ImportError("Playwright引擎不可用, 请安装: pip install playwright && python -m playwright install")
            engine = PlaywrightImageEngine()
        elif engine_type == 'legacy':
            engine = LegacyImageEngine()
        else:
            raise ValueError(f"未知的引擎类型: {engine_type}")
        
        await engine.initialize(self.config)
        return engine

    async def download_images_async(self, args: argparse.Namespace):
        print(f"\n🚀 启动 Image-tools v4.0 - 模式: {args.mode}")
        if self.base_url:
            print(f"🎯 目标网站: {self.base_url}")
        else:
            print("⚠️  警告: 未在配置文件中设置 'base_url'。")
            return

        self.engine_type = self._determine_engine_type(args.engine)
        print(f"🔧 使用引擎: {self.engine_type}")

        try:
            self.engine = await self._create_engine(self.engine_type)
            print(f"✅ {self.engine_type} 引擎初始化成功")

            image_infos = await self.engine.extract_image_urls(self.base_url)
            if not image_infos:
                print("🤷 未找到任何符合条件的图片。")
                return

            print(f"📷 找到 {len(image_infos)} 张图片，准备下载...")
            
            save_dir = str(self.images_dir)
            result = await self.engine.batch_download(image_infos, save_dir)
            self.stats.update(result)

        except Exception as e:
            print(f"\n❌ 下载过程中发生严重错误: {e}")
        finally:
            if self.engine:
                await self.engine.cleanup()
            self._print_stats()

    def _print_stats(self):
        elapsed = time.time() - self.stats['start_time']
        size_kb = self.stats.get('total_size', 0) / 1024
        print("\n" + "="*30)
        print("📊 下载统计")
        print("="*30)
        print(f"  - 成功下载: {self.stats.get('successful', 0)} 张图片")
        print(f"  - 下载失败: {self.stats.get('failed', 0)} 张图片")
        print(f"  - 总文件大小: {size_kb:.2f} KB")
        print(f"  - 总耗时: {elapsed:.2f} 秒")
        print("="*30)

def main():
    parser = argparse.ArgumentParser(description="Image-tools v4.0 - 智能图片下载器")
    parser.add_argument('mode', nargs='?', default='all', help="运行模式 (当前版本仅支持 'all')")
    parser.add_argument('--engine', choices=['playwright', 'legacy'], help="强制使用特定引擎 (playwright 或 legacy)")
    
    args = parser.parse_args()
    downloader = ImageDownloader()
    
    try:
        asyncio.run(downloader.download_images_async(args))
        print("\n🎉 下载任务完成!")
    except KeyboardInterrupt:
        print("\n⏹️  用户操作中断，程序退出。")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()