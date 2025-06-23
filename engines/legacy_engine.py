"""
传统爬取引擎 (基于requests + BeautifulSoup)

这是v3.0及以前版本使用的爬取方式，主要用于：
1. 向后兼容
2. 简单网站的快速爬取
3. 在Playwright不可用时的备用方案
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import os
import time
from .base_engine import BaseImageEngine, ImageInfo


class LegacyImageEngine(BaseImageEngine):
    """基于requests的传统图片爬取引擎"""
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def initialize(self, config: Dict) -> bool:
        """初始化传统引擎"""
        try:
            self.config = config
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            
            # 设置超时和重试参数
            download_settings = config.get('download_settings', {})
            self.timeout = download_settings.get('timeout', 30)
            self.max_retries = download_settings.get('max_retries', 3)
            self.delay = download_settings.get('delay_between_downloads', 0.5)
            
            self.log_info("传统引擎初始化成功")
            return True
            
        except Exception as e:
            self.log_error("传统引擎初始化失败", e)
            return False
    
    async def extract_image_urls(self, url: str) -> List[ImageInfo]:
        """从网页提取图片URL"""
        try:
            self.log_info(f"正在分析页面: {url}")
            
            # 获取网页内容
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找所有图片标签
            img_tags = soup.find_all('img')
            image_infos = []
            
            for i, img in enumerate(img_tags):
                # 提取图片URL
                img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                
                if not img_url:
                    continue
                
                # 转换为绝对URL
                absolute_url = urljoin(url, img_url)
                
                # 创建图片信息对象
                filename = self._generate_filename(absolute_url, i + 1)
                metadata = {
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'class': img.get('class', []),
                    'width': img.get('width'),
                    'height': img.get('height')
                }
                
                image_info = ImageInfo(absolute_url, filename, metadata)
                image_infos.append(image_info)
            
            self.stats['images_found'] = len(image_infos)
            self.log_info(f"找到 {len(image_infos)} 张图片")
            
            return image_infos
            
        except Exception as e:
            self.log_error("提取图片URL失败", e)
            return []
    
    async def download_image(self, image_info: ImageInfo, save_path: str) -> bool:
        """下载单张图片"""
        try:
            # 添加延迟以避免请求过快
            if self.delay > 0:
                await asyncio.sleep(self.delay)
            
            # 下载图片
            response = self.session.get(image_info.url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 保存文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 更新统计信息
            file_size = os.path.getsize(save_path)
            self.stats['total_size'] += file_size
            
            return True
            
        except Exception as e:
            self.log_error(f"下载图片失败: {image_info.url}", e)
            return False
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            self.session.close()
            self.log_info("传统引擎资源已清理")
    
    def _generate_filename(self, url: str, index: int) -> str:
        """生成文件名"""
        try:
            # 从URL中提取文件名
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            
            if original_filename and '.' in original_filename:
                return original_filename
            else:
                # 如果无法提取有效文件名，使用索引
                return f"image_{index:03d}.jpg"
                
        except:
            return f"image_{index:03d}.jpg" 