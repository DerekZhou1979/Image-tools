#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image-tools v4.0 通用图片下载器
支持传统和浏览器自动化两种爬取引擎，智能应对现代网站的反爬虫机制
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import time
from typing import Dict, List, Optional, Union

# 核心引擎导入
try:
    from engines.base_engine import BaseImageEngine, ImageInfo
    from engines.legacy_engine import LegacyImageEngine
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    print("❌ 引擎模块导入失败，请检查项目结构")

# Playwright引擎导入（延迟导入）
PLAYWRIGHT_AVAILABLE = False
try:
    from engines import get_playwright_engine
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

# 工具模块导入
try:
    from utils.browser_config import BrowserConfig
    from utils.image_analyzer import ImageAnalyzer
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

# Gemini Vision API 相关导入
try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ImageDownloader:
    """Image-tools v4.0 主下载器类"""
    
    def __init__(self, config_file='image_download_config.json'):
        """初始化下载器"""
        self.config_file = config_file
        self.load_config()
        self.base_url = self.config.get('base_url', 'https://example.com/')
        self.images_dir = Path('./images')
        
        # 引擎相关
        self.engine: Optional[BaseImageEngine] = None
        self.engine_type = None
        
        # 统计信息
        self.stats = {
            'images_found': 0,
            'images_downloaded': 0,
            'images_failed': 0,
            'total_size': 0,
            'start_time': time.time()
        }
        
        # 创建images目录
        self.images_dir.mkdir(exist_ok=True)
        
        # Gemini相关初始化
            self.gemini_model = None
            self.use_gemini_vision = False
    
        # 兼容性标志
        self.force_matching_mode = False
        self.force_download_all = False
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 配置文件加载成功: {self.config_file}")
        except FileNotFoundError:
            print(f"❌ 配置文件未找到: {self.config_file}")
            print("💡 使用默认配置创建新的配置文件...")
            self._create_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "description": "通用图片下载配置文件 v4.0",
            "base_url": "https://example.com/",
            "site_name": "示例网站",
            "download_settings": {
                "delay_between_downloads": 0.5,
                "max_retries": 3,
                "timeout": 30,
                "max_concurrent_downloads": 5
            },
            "engine_settings": {
                "default_engine": "auto",
                "fallback_engine": "legacy",
                "browser_type": "chromium",
                "headless": True,
                "stealth_mode": True
            },
            "image_categories": [
                {
                    "category": "hero_section",
                    "filename": "hero_main_banner.jpg",
                    "keywords": ["hero", "banner", "main"],
                    "selectors": [".hero-banner", "#main-banner"]
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        self.config = default_config
        print(f"✅ 默认配置文件已创建: {self.config_file}")
    
    def _determine_engine_type(self, force_engine: str = None) -> str:
        """确定使用的引擎类型"""
        if force_engine:
            return force_engine
        
        # 从配置文件读取
        default_engine = self.config.get('engine_settings', {}).get('default_engine', 'auto')
        
        if default_engine == 'auto':
            # 自动选择：优先Playwright，不可用时降级到Legacy
            if PLAYWRIGHT_AVAILABLE:
                return 'playwright'
        else:
                print("⚠️  Playwright不可用，使用传统引擎")
                return 'legacy'
        
        return default_engine
    
    async def _create_engine(self, engine_type: str) -> BaseImageEngine:
        """创建并初始化引擎"""
        if engine_type == 'playwright':
            if not PLAYWRIGHT_AVAILABLE:
                print("❌ Playwright引擎不可用，请安装: pip install playwright")
                print("   然后运行: python -m playwright install chromium")
                raise ImportError("Playwright引擎不可用")
            
            PlaywrightEngine = get_playwright_engine()
            engine = PlaywrightEngine()
            
        elif engine_type == 'legacy':
            engine = LegacyImageEngine()
            
                    else:
            raise ValueError(f"未知的引擎类型: {engine_type}")
        
        # 初始化引擎
        success = await engine.initialize(self.config)
        if not success:
            raise RuntimeError(f"引擎 {engine_type} 初始化失败")
        
        return engine
    
    async def download_images_async(self, mode: str = 'all') -> Dict:
        """异步下载图片主方法"""
        print(f"\n🚀 启动 Image-tools v4.0 - 模式: {mode}")
        print(f"🎯 目标网站: {self.base_url}")
        
        # 确定引擎类型
        force_engine = None
        if mode == 'legacy':
            force_engine = 'legacy'
        
        self.engine_type = self._determine_engine_type(force_engine)
        print(f"🔧 使用引擎: {self.engine_type}")
        
        try:
            # 创建并初始化引擎
            self.engine = await self._create_engine(self.engine_type)
            print(f"✅ {self.engine_type} 引擎初始化成功")
            
            # 提取图片URL
            print("🔍 开始分析网页内容...")
            image_infos = await self.engine.extract_image_urls(self.base_url)
            
            if not image_infos:
                print("❌ 未找到任何图片")
                return self.stats
            
            self.stats['images_found'] = len(image_infos)
            print(f"📷 找到 {len(image_infos)} 张图片")
            
            # 根据模式处理图片
            selected_images = self._filter_images_by_mode(image_infos, mode)
            
            if not selected_images:
                print("❌ 根据当前模式未选择任何图片")
                return self.stats
            
            print(f"📥 准备下载 {len(selected_images)} 张图片...")
            
            # 执行下载
            download_result = await self.engine.batch_download(
                selected_images, 
                str(self.images_dir),
                max_concurrent=self.config.get('download_settings', {}).get('max_concurrent_downloads', 5)
            )
            
            # 更新统计信息
            self.stats.update(download_result)
            
            # 根据模式执行后处理
            if mode in ['gemini', 'rename']:
                await self._post_process_images(mode)
            
            return self.stats
            
                except Exception as e:
            print(f"❌ 下载过程中发生错误: {e}")
            # 尝试降级到备用引擎
            fallback_engine = self.config.get('engine_settings', {}).get('fallback_engine')
            if fallback_engine and fallback_engine != self.engine_type:
                print(f"🔄 尝试使用备用引擎: {fallback_engine}")
                return await self.download_images_async(mode + '_fallback')
            
            return self.stats
            
        finally:
            # 清理资源
            if self.engine:
                await self.engine.cleanup()
            
            # 显示统计信息
            self._print_stats()
    
    def _filter_images_by_mode(self, image_infos: List[ImageInfo], mode: str) -> List[ImageInfo]:
        """根据模式过滤图片"""
        if mode in ['all', 'legacy']:
            return image_infos
        
        elif mode == 'match':
            return self._filter_by_keywords(image_infos)
        
        elif mode == 'manual':
            return self._manual_select_images(image_infos)
        
            else:
            # 其他模式默认返回所有图片
            return image_infos
    
    def _filter_by_keywords(self, image_infos: List[ImageInfo]) -> List[ImageInfo]:
        """根据关键词过滤图片"""
        categories = self.config.get('image_categories', [])
        selected = []
        
        for image_info in image_infos:
            for category in categories:
                keywords = category.get('keywords', [])
                # 检查URL或metadata中是否包含关键词
                if any(keyword.lower() in image_info.url.lower() for keyword in keywords):
                    # 使用配置中的文件名
                    image_info.filename = category.get('filename', image_info.filename)
                    selected.append(image_info)
                    break
        
        return selected
    
    def _manual_select_images(self, image_infos: List[ImageInfo]) -> List[ImageInfo]:
        """手动选择图片"""
        print("\n📋 找到以下图片，请选择要下载的图片:")
        
        for i, image_info in enumerate(image_infos, 1):
            print(f"{i:3d}. {image_info.url}")
            if image_info.metadata.get('alt'):
                print(f"     Alt: {image_info.metadata['alt']}")
        
        try:
            selection = input("\n请输入要下载的图片编号（用逗号分隔，或输入 'all' 下载全部）: ").strip()
            
            if selection.lower() == 'all':
                return image_infos
            
            indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip().isdigit()]
            selected = [image_infos[i] for i in indices if 0 <= i < len(image_infos)]
            
            print(f"✅ 已选择 {len(selected)} 张图片")
            return selected
            
        except (ValueError, KeyboardInterrupt):
            print("❌ 选择无效或已取消")
            return []
    
    async def _post_process_images(self, mode: str):
        """图片后处理（重命名等）"""
        if mode == 'gemini':
            await self._smart_rename_with_gemini()
        elif mode == 'rename':
            await self._smart_rename_basic()
    
    async def _smart_rename_with_gemini(self):
        """使用Gemini AI进行智能重命名"""
        if not GEMINI_AVAILABLE:
            print("❌ Gemini API不可用")
            return
        
        # 初始化Gemini API
        self.init_gemini_api()
        
        if not self.use_gemini_vision:
            print("❌ Gemini Vision功能不可用")
            return
        
        print("🧠 开始使用Gemini AI进行智能重命名...")
        
        # 遍历images目录中的图片
        image_files = list(self.images_dir.glob('*.jpg')) + list(self.images_dir.glob('*.png'))
        
        for image_path in image_files:
            try:
                # 使用Gemini分析图片
                analysis = await self._analyze_image_with_gemini(image_path)
                
                if analysis:
                    new_filename = self._generate_ai_filename(analysis)
                    new_path = self.images_dir / new_filename
                    
                    # 避免重复文件名
                        counter = 1
                        while new_path.exists():
                        name, ext = new_filename.rsplit('.', 1)
                        new_filename = f"{name}_{counter}.{ext}"
                        new_path = self.images_dir / new_filename
                            counter += 1
                    
                    # 重命名文件
                    image_path.rename(new_path)
                    print(f"🎯 重命名: {image_path.name} -> {new_filename}")
                    
                except Exception as e:
                print(f"❌ 重命名失败 {image_path.name}: {e}")
    
    async def _smart_rename_basic(self):
        """基础智能重命名"""
        print("🔧 开始基础智能重命名...")
        
        # 实现基础重命名逻辑
        image_files = list(self.images_dir.glob('*.jpg')) + list(self.images_dir.glob('*.png'))
        
        for image_path in image_files:
            try:
                # 基于文件大小和简单特征进行重命名
                new_filename = self._generate_basic_filename(image_path)
                if new_filename != image_path.name:
                    new_path = self.images_dir / new_filename
                    
                    counter = 1
                    while new_path.exists():
                        name, ext = new_filename.rsplit('.', 1)
                        new_filename = f"{name}_{counter}.{ext}"
                        new_path = self.images_dir / new_filename
                        counter += 1
                    
                    image_path.rename(new_path)
                    print(f"🔧 重命名: {image_path.name} -> {new_filename}")
                    
            except Exception as e:
                print(f"❌ 重命名失败 {image_path.name}: {e}")
    
    def _generate_basic_filename(self, image_path: Path) -> str:
        """生成基础文件名"""
        # 基于文件大小判断图片类型
        file_size = image_path.stat().st_size
        
        if file_size > 1024 * 1024:  # > 1MB
            prefix = "large_image"
        elif file_size > 100 * 1024:  # > 100KB
            prefix = "medium_image"
        else:
            prefix = "small_image"
        
        return f"{prefix}_{int(time.time())}.jpg"
    
    async def _analyze_image_with_gemini(self, image_path: Path) -> Dict:
        """使用Gemini分析图片"""
        try:
            # 这里会实现Gemini图片分析的具体逻辑
            # 暂时返回模拟数据
            return {
                'type': 'product',
                'content': '产品图片',
                'confidence': 8
            }
        except Exception as e:
            print(f"❌ Gemini分析失败: {e}")
            return {}
    
    def _generate_ai_filename(self, analysis: Dict) -> str:
        """根据AI分析结果生成文件名"""
        image_type = analysis.get('type', 'unknown')
        content = analysis.get('content', 'image')
        
        # 简化文件名生成逻辑
        timestamp = int(time.time())
        return f"ai_{image_type}_{timestamp}.jpg"
    
    def init_gemini_api(self):
        """初始化Gemini API（保持兼容性）"""
        if not GEMINI_AVAILABLE:
            return
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ 未找到 GEMINI_API_KEY 环境变量")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            self.use_gemini_vision = True
            print("✅ Gemini Vision API 已配置成功")
        except Exception as e:
            print(f"❌ Gemini API 配置失败: {e}")
            self.use_gemini_vision = False
    
    def _print_stats(self):
        """打印统计信息"""
        elapsed_time = time.time() - self.stats['start_time']
        
        print(f"\n📊 下载统计:")
        print(f"✅ 成功下载: {self.stats.get('successful', 0)} 张图片")
        print(f"❌ 下载失败: {self.stats.get('failed', 0)} 张图片")
        print(f"📁 总文件大小: {self._format_file_size(self.stats.get('total_size', 0))}")
        print(f"⏱️  总耗时: {elapsed_time:.1f} 秒")
        
        if self.engine:
            engine_stats = self.engine.get_stats()
            print(f"🔧 引擎: {self.engine_type}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    # ============ 同步接口（向后兼容） ============
    
    def download_images(self, mode: str = 'all') -> Dict:
        """同步下载接口，保持向后兼容"""
        return asyncio.run(self.download_images_async(mode))
    
    def search_and_download_images(self):
        """兼容v3.0的方法名"""
        return self.download_images('all')
    
    def download_with_matching(self):
        """兼容v3.0的方法名"""
        return self.download_images('match')
    
    def manual_download_mode(self):
        """兼容v3.0的方法名"""
        return self.download_images('manual')
    
    def smart_rename_images(self):
        """兼容v3.0的方法名"""
        return asyncio.run(self._smart_rename_basic())
    
    def smart_rename_with_gemini(self):
        """兼容v3.0的方法名"""
        return asyncio.run(self._smart_rename_with_gemini())


def main():
    """主函数 - 兼容原有的命令行接口"""
    downloader = ImageDownloader()
    
    # 解析命令行参数（保持兼容性）
    if len(sys.argv) > 1:
        mode = sys.argv[1].replace('--', '')
        
        # 兼容性映射
        mode_mapping = {
            'match': 'match',
            'manual': 'manual',
            'rename': 'rename',
            'gemini': 'gemini',
            'legacy': 'legacy'
        }
        
        actual_mode = mode_mapping.get(mode, 'all')
    else:
        actual_mode = 'all'
    
    # 执行下载
    try:
        result = downloader.download_images(actual_mode)
        print(f"\n🎉 下载完成!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  用户取消下载")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 