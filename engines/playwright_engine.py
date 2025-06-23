"""
基于Playwright的高级图片爬取引擎

专门设计用于应对现代网站的反爬虫机制，包括：
- Cloudflare保护
- JavaScript动态加载
- 懒加载图片
- 会话验证和防盗链
"""

import asyncio
import os
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
    PLAYWRIGHT_IMPORTED = True
except ImportError:
    PLAYWRIGHT_IMPORTED = False

from .base_engine import BaseImageEngine, ImageInfo
from ..utils.browser_config import BrowserConfig


class PlaywrightImageEngine(BaseImageEngine):
    """基于Playwright的图片爬取引擎"""
    
    def __init__(self):
        super().__init__()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def initialize(self, config: Dict) -> bool:
        """初始化Playwright浏览器"""
        if not PLAYWRIGHT_IMPORTED:
            self.log_error("Playwright未安装，请运行: pip install playwright && python -m playwright install chromium")
            return False
        
        try:
            self.config = config
            engine_settings = config.get('engine_settings', {})
            
            # 启动Playwright
            self.playwright = await async_playwright().start()
            
            # 获取浏览器类型
            browser_type = engine_settings.get('browser_type', 'chromium')
            browser_launcher = getattr(self.playwright, browser_type)
            
            # 配置启动参数
            launch_options = {
                'headless': engine_settings.get('headless', True),
                'args': BrowserConfig.get_stealth_launch_args() if engine_settings.get('stealth_mode', True) else []
            }
            
            # 启动浏览器
            self.browser = await browser_launcher.launch(**launch_options)
            
            # 创建上下文
            context_options = BrowserConfig.get_stealth_context_options()
            
            # 添加代理配置
            proxy_settings = config.get('proxy_settings', {})
            if proxy_settings.get('enabled', False):
                proxy_config = BrowserConfig.get_proxy_config(proxy_settings)
                if proxy_config:
                    context_options['proxy'] = proxy_config
            
            self.context = await self.browser.new_context(**context_options)
            
            # 注入反检测脚本
            if engine_settings.get('stealth_mode', True):
                await self._inject_stealth_scripts()
            
            # 创建页面
            self.page = await self.context.new_page()
            
            # 设置额外的事件监听
            await self._setup_page_handlers()
            
            self.log_info("Playwright引擎初始化成功")
            return True
            
        except Exception as e:
            self.log_error("Playwright引擎初始化失败", e)
            await self.cleanup()
            return False
    
    async def _inject_stealth_scripts(self):
        """注入反检测脚本"""
        stealth_scripts = BrowserConfig.get_stealth_scripts()
        
        for script in stealth_scripts:
            try:
                await self.context.add_init_script(script)
            except Exception as e:
                self.log_error(f"注入反检测脚本失败: {script[:50]}...", e)
    
    async def _setup_page_handlers(self):
        """设置页面事件处理器"""
        # 处理对话框（如alert, confirm等）
        self.page.on('dialog', lambda dialog: asyncio.create_task(dialog.dismiss()))
        
        # 处理控制台消息（调试用）
        # self.page.on('console', lambda msg: print(f"Console: {msg.text}"))
        
        # 处理页面错误
        self.page.on('pageerror', lambda error: self.log_error(f"页面错误: {error}"))
    
    async def extract_image_urls(self, url: str) -> List[ImageInfo]:
        """智能提取图片URL"""
        try:
            self.log_info(f"正在访问页面: {url}")
            
            # 导航到页面
            response = await self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            if not response or not response.ok:
                self.log_error(f"页面加载失败: {response.status if response else 'No response'}")
                return []
            
            self.log_info("页面加载成功，开始检测和处理动态内容...")
            
            # 处理可能的Cookie同意弹窗
            await self._handle_cookie_consent()
            
            # 执行智能滚动以触发懒加载
            await self._smart_scroll()
            
            # 等待图片加载
            await self._wait_for_images_to_load()
            
            # 提取图片信息
            image_infos = await self._extract_all_images()
            
            self.stats['images_found'] = len(image_infos)
            self.log_info(f"成功提取到 {len(image_infos)} 张图片")
            
            return image_infos
            
        except Exception as e:
            self.log_error("提取图片URL失败", e)
            return []
    
    async def _handle_cookie_consent(self):
        """处理Cookie同意弹窗"""
        try:
            # 常见的Cookie同意按钮选择器
            consent_selectors = [
                'button:has-text("Accept")',
                'button:has-text("同意")',
                'button:has-text("确定")',
                'button:has-text("OK")',
                '.cookie-accept',
                '#cookie-accept',
                '[data-testid="cookie-accept"]'
            ]
            
            for selector in consent_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        self.log_info("已处理Cookie同意弹窗")
                        await self.page.wait_for_timeout(1000)
                        break
                except:
                    continue
                    
        except Exception as e:
            # Cookie弹窗处理失败不影响主流程
            pass
    
    async def _smart_scroll(self):
        """智能滚动以触发懒加载"""
        try:
            scroll_config = BrowserConfig.get_scroll_behavior_config(self.config)
            
            if not scroll_config.get('enabled', True):
                return
            
            self.log_info("开始智能滚动以触发懒加载...")
            
            max_attempts = scroll_config.get('max_scroll_attempts', 10)
            pause_time = scroll_config.get('scroll_pause_time', 2.0)
            
            last_height = 0
            attempts = 0
            
            while attempts < max_attempts:
                # 获取当前页面高度
                current_height = await self.page.evaluate('document.body.scrollHeight')
                
                # 如果高度没有变化，说明可能已经到底了
                if current_height == last_height:
                    attempts += 1
                else:
                    attempts = 0  # 重置计数器
                
                # 平滑滚动到底部
                await self.page.evaluate('''
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                ''')
                
                # 等待内容加载
                await self.page.wait_for_timeout(int(pause_time * 1000))
                
                last_height = current_height
                
                # 模拟随机暂停（更像人类行为）
                if scroll_config.get('random_pause', True):
                    import random
                    pause_range = scroll_config.get('pause_range', (0.5, 1.5))
                    await self.page.wait_for_timeout(random.uniform(pause_range[0], pause_range[1]) * 1000)
            
        except Exception as e:
            self.log_error("智能滚动失败", e)
    
    async def _wait_for_images_to_load(self):
        """等待图片加载"""
        try:
            # 这里需要实现等待图片加载的逻辑
            # 目前只是一个占位函数，实际实现需要根据实际情况来决定
            await self.page.wait_for_timeout(5000)  # 临时等待
        except Exception as e:
            self.log_error("等待图片加载失败", e)
    
    async def _extract_all_images(self) -> List[ImageInfo]:
        """提取所有图片信息"""
        try:
            # 这里需要实现提取所有图片信息的逻辑
            # 目前只是一个占位函数，实际实现需要根据实际情况来决定
            return []  # 临时返回空列表
        except Exception as e:
            self.log_error("提取所有图片信息失败", e)
            return []
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            self.log_info("Playwright引擎清理成功")
        except Exception as e:
            self.log_error("Playwright引擎清理失败", e)
    
    async def batch_download(self, image_infos: List[ImageInfo], output_dir: str, max_concurrent: int = 5) -> Dict:
        """批量下载图片"""
        try:
            # 这里需要实现批量下载图片的逻辑
            # 目前只是一个占位函数，实际实现需要根据实际情况来决定
            return {}  # 临时返回空字典
        except Exception as e:
            self.log_error("批量下载图片失败", e)
            return {}
    
    def get_stats(self) -> Dict:
        """获取引擎统计信息"""
        return self.stats

    def log_info(self, message: str):
        """记录信息"""
        print(f"[INFO] {message}")

    def log_error(self, message: str, exception: Exception = None):
        """记录错误"""
        print(f"[ERROR] {message}", exception) 