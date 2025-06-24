"""
Image-tools v4.0 工具模块

包含各种辅助工具和配置管理器：
- BrowserConfig: 浏览器反检测配置
- ProxyManager: 代理管理器  
"""

from .browser_config import BrowserConfig
from .svg_converter import SVGConverter, convert_svg_images

__version__ = "4.0.0"
__all__ = ["BrowserConfig", "SVGConverter", "convert_svg_images"]

# 便捷函数：直接从命令行运行SVG转换工具
def run_svg_converter():
    """运行SVG转换工具的便捷函数"""
    from .svg_converter_tool import main
    main()

# 其他工具的延迟导入
def get_proxy_manager():
    """获取代理管理器"""
    try:
        from .proxy_manager import ProxyManager
        return ProxyManager
    except ImportError:
        return None 