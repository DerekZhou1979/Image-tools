"""
Image-tools v4.0 爬取引擎模块

支持多种爬取引擎：
- PlaywrightEngine: 基于浏览器自动化的高级爬取引擎
- LegacyEngine: 基于requests的传统爬取引擎
"""

from .base_engine import BaseImageEngine, ImageInfo
from .legacy_engine import LegacyImageEngine

__version__ = "4.0.0"
__all__ = ["BaseImageEngine", "LegacyImageEngine", "ImageInfo"]

# Playwright引擎延迟导入，避免在未安装时出错
def get_playwright_engine():
    """获取Playwright引擎实例"""
    try:
        from .playwright_engine import PlaywrightImageEngine
        return PlaywrightImageEngine
    except ImportError as e:
        raise ImportError(
            "Playwright引擎不可用。请安装Playwright:\n"
            "pip install playwright\n"
            "python -m playwright install chromium"
        ) from e

# 引擎工厂函数
def create_engine(engine_type: str):
    """创建指定类型的引擎"""
    if engine_type.lower() == 'playwright':
        return get_playwright_engine()()
    elif engine_type.lower() == 'legacy':
        return LegacyImageEngine()
    else:
        raise ValueError(f"未知的引擎类型: {engine_type}")

# 检查引擎可用性
def check_engine_availability():
    """检查各引擎的可用性"""
    availability = {
        'legacy': True,  # Legacy引擎总是可用的
        'playwright': False
    }
    
    try:
        from .playwright_engine import PlaywrightImageEngine
        availability['playwright'] = True
    except ImportError:
        pass
    
    return availability 