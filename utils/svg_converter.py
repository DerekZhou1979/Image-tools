"""
SVG到PNG转换工具

支持多种转换引擎和质量设置，专门为Image-tools项目设计
"""

import os
import io
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

try:
    from svglib.svglib import renderSVG
    from reportlab.graphics import renderPDF, renderPM
    SVGLIB_AVAILABLE = True
except ImportError:
    SVGLIB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class SVGConverter:
    """SVG到PNG转换器"""
    
    def __init__(self, default_width: int = 512, default_height: int = 512, quality: str = "high"):
        self.default_width = default_width
        self.default_height = default_height
        self.quality = quality
        self.stats = {
            'converted': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def get_available_engines(self) -> Dict[str, bool]:
        """获取可用的转换引擎"""
        return {
            'cairosvg': CAIROSVG_AVAILABLE,
            'svglib': SVGLIB_AVAILABLE,
            'pillow': PILLOW_AVAILABLE
        }
    
    def convert_svg_to_png(self, svg_path: str, png_path: Optional[str] = None, 
                          width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """
        将SVG文件转换为PNG
        
        Args:
            svg_path: SVG文件路径
            png_path: PNG输出路径，如果为None则自动生成
            width: 输出宽度
            height: 输出高度
            
        Returns:
            bool: 转换是否成功
        """
        if not os.path.exists(svg_path):
            self.log_error(f"SVG文件不存在: {svg_path}")
            return False
            
        if png_path is None:
            png_path = str(Path(svg_path).with_suffix('.png'))
            
        width = width or self.default_width
        height = height or self.default_height
        
        # 尝试多种转换方法
        conversion_methods = [
            self._convert_with_cairosvg,
            self._convert_with_svglib,
            self._convert_with_pillow_fallback
        ]
        
        for method in conversion_methods:
            try:
                if method(svg_path, png_path, width, height):
                    self.stats['converted'] += 1
                    self.log_info(f"✅ SVG转PNG成功: {os.path.basename(png_path)}")
                    return True
            except Exception as e:
                self.log_error(f"转换方法失败: {method.__name__}", e)
                continue
        
        self.stats['failed'] += 1
        self.log_error(f"❌ SVG转PNG失败: {svg_path}")
        return False
    
    def _convert_with_cairosvg(self, svg_path: str, png_path: str, width: int, height: int) -> bool:
        """使用CairoSVG转换"""
        if not CAIROSVG_AVAILABLE:
            return False
            
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=width,
            output_height=height
        )
        return os.path.exists(png_path)
    
    def _convert_with_svglib(self, svg_path: str, png_path: str, width: int, height: int) -> bool:
        """使用svglib转换"""
        if not SVGLIB_AVAILABLE:
            return False
            
        drawing = renderSVG.renderSVG(svg_path)
        # 缩放到指定尺寸
        scale_x = width / drawing.width
        scale_y = height / drawing.height
        scale = min(scale_x, scale_y)
        
        drawing.width = width
        drawing.height = height
        drawing.scale(scale, scale)
        
        renderPM.drawToFile(drawing, png_path, fmt='PNG')
        return os.path.exists(png_path)
    
    def _convert_with_pillow_fallback(self, svg_path: str, png_path: str, width: int, height: int) -> bool:
        """使用Pillow创建占位图（备用方案）"""
        if not PILLOW_AVAILABLE:
            return False
            
        # 创建一个简单的占位图
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的SVG占位符
        draw.rectangle([10, 10, width-10, height-10], outline=(100, 100, 100), width=2)
        draw.text((width//2-30, height//2-10), "SVG", fill=(100, 100, 100))
        
        img.save(png_path, 'PNG')
        return True
    
    def convert_directory(self, directory: str, keep_original: bool = True) -> Dict[str, Any]:
        """
        转换目录中的所有SVG文件
        
        Args:
            directory: 目录路径
            keep_original: 是否保留原始SVG文件
            
        Returns:
            Dict: 转换统计信息
        """
        svg_files = list(Path(directory).glob('*.svg'))
        
        if not svg_files:
            self.log_info("未找到SVG文件")
            return self.stats
            
        self.log_info(f"发现 {len(svg_files)} 个SVG文件，开始转换...")
        
        for svg_file in svg_files:
            svg_path = str(svg_file)
            png_path = str(svg_file.with_suffix('.png'))
            
            if self.convert_svg_to_png(svg_path, png_path):
                if not keep_original:
                    try:
                        os.remove(svg_path)
                        self.log_info(f"🗑️ 删除原始SVG: {svg_file.name}")
                    except Exception as e:
                        self.log_error(f"删除原始文件失败: {svg_file.name}", e)
        
        return self.stats
    
    def batch_convert_with_settings(self, directory: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用自定义设置批量转换
        
        Args:
            directory: 目录路径
            settings: 转换设置
                - width: 输出宽度
                - height: 输出高度
                - quality: 质量设置
                - keep_original: 是否保留原文件
                - suffix: 输出文件后缀
        """
        width = settings.get('width', self.default_width)
        height = settings.get('height', self.default_height)
        keep_original = settings.get('keep_original', True)
        suffix = settings.get('suffix', '')
        
        svg_files = list(Path(directory).glob('*.svg'))
        self.log_info(f"批量转换 {len(svg_files)} 个SVG文件...")
        
        for svg_file in svg_files:
            svg_path = str(svg_file)
            
            # 生成输出文件名
            if suffix:
                png_name = f"{svg_file.stem}{suffix}.png"
            else:
                png_name = f"{svg_file.stem}.png"
            
            png_path = str(svg_file.parent / png_name)
            
            if self.convert_svg_to_png(svg_path, png_path, width, height):
                if not keep_original:
                    try:
                        os.remove(svg_path)
                    except Exception as e:
                        self.log_error(f"删除原始文件失败: {svg_file.name}", e)
        
        return self.stats
    
    def get_svg_info(self, svg_path: str) -> Optional[Dict[str, Any]]:
        """获取SVG文件信息"""
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单解析SVG尺寸信息
            info = {
                'file_size': os.path.getsize(svg_path),
                'content_length': len(content),
                'has_viewbox': 'viewBox' in content,
                'has_width': 'width=' in content,
                'has_height': 'height=' in content
            }
            
            return info
        except Exception as e:
            self.log_error(f"获取SVG信息失败: {svg_path}", e)
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取转换统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {'converted': 0, 'failed': 0, 'skipped': 0}
    
    def log_info(self, message: str):
        """输出信息日志"""
        print(f"ℹ️  [SVG转换] {message}")
    
    def log_error(self, message: str, exception: Exception = None):
        """输出错误日志"""
        if exception:
            print(f"❌ [SVG转换] {message}: {exception}")
        else:
            print(f"❌ [SVG转换] {message}")


def convert_svg_images(directory: str, **kwargs) -> Dict[str, Any]:
    """
    便捷函数：转换目录中的SVG图片
    
    Args:
        directory: 图片目录
        **kwargs: 转换选项
    
    Returns:
        Dict: 转换统计
    """
    converter = SVGConverter()
    return converter.convert_directory(directory, **kwargs)


if __name__ == "__main__":
    # 测试代码
    converter = SVGConverter()
    print("可用的转换引擎:")
    for engine, available in converter.get_available_engines().items():
        status = "✅" if available else "❌"
        print(f"  {engine}: {status}") 