"""
浏览器反检测配置模块
提供各种反检测设置以绕过现代网站的机器人检测
"""

import random
from typing import Dict, List, Optional


class BrowserConfig:
    """浏览器反检测配置管理器"""
    
    # 真实的User-Agent列表
    USER_AGENTS = [
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        
        # Firefox
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
    ]
    
    # 真实的屏幕分辨率
    SCREEN_RESOLUTIONS = [
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 720},
        {"width": 2560, "height": 1440}
    ]
    
    # 语言设置
    LANGUAGES = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "zh-CN;q=0.9,zh;q=0.8,en;q=0.7"
    ]

    # === Playwright引擎期望的方法 ===
    
    @staticmethod
    def get_stealth_launch_args() -> List[str]:
        """获取Playwright浏览器启动的反检测参数"""
        return [
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-web-security",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--no-first-run",
            "--no-zygote",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding"
        ]
    
    @staticmethod
    def get_stealth_context_options() -> Dict:
        """获取Playwright浏览器上下文的反检测选项"""
        resolution = random.choice(BrowserConfig.SCREEN_RESOLUTIONS)
        user_agent = random.choice(BrowserConfig.USER_AGENTS)
        language = random.choice(BrowserConfig.LANGUAGES)
        
        return {
            "user_agent": user_agent,
            "viewport": resolution,
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": language,
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            }
        }
    
    @staticmethod
    def get_stealth_scripts() -> List[str]:
        """获取反检测JavaScript脚本"""
        return [
            # 隐藏webdriver标记
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            # 修改navigator.plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            # 修改navigator.languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
            """,
            # 隐藏Chrome自动化扩展
            """
            if (window.chrome && window.chrome.runtime && window.chrome.runtime.onConnect) {
                delete window.chrome.runtime.onConnect;
            }
            """
        ]
    
    @staticmethod
    def get_proxy_config(proxy_settings: Dict) -> Optional[Dict]:
        """获取代理配置"""
        if not proxy_settings.get('enabled', False):
            return None
            
        proxy_config = {}
        if proxy_settings.get('server'):
            proxy_config['server'] = proxy_settings['server']
        if proxy_settings.get('username') and proxy_settings.get('password'):
            proxy_config['username'] = proxy_settings['username']
            proxy_config['password'] = proxy_settings['password']
            
        return proxy_config if proxy_config else None
    
    @staticmethod
    def get_scroll_behavior_config(config: Dict) -> Dict:
        """获取滚动行为配置"""
        scroll_settings = config.get('scroll_settings', {})
        return {
            'enabled': scroll_settings.get('enabled', True),
            'max_scroll_attempts': scroll_settings.get('max_scroll_attempts', 10),
            'scroll_pause_time': scroll_settings.get('scroll_pause_time', 2.0),
            'random_pause': scroll_settings.get('random_pause', True),
            'pause_range': scroll_settings.get('pause_range', (0.5, 1.5))
        }

    # === 原有的方法保持不变 ===
    
    @classmethod
    def get_stealth_config(cls, engine: str = "playwright") -> Dict:
        """获取反检测配置"""
        if engine == "playwright":
            return cls._get_playwright_stealth_config()
        elif engine == "legacy":
            return cls._get_legacy_stealth_config()
        else:
            raise ValueError(f"不支持的引擎类型: {engine}")
    
    @classmethod
    def _get_playwright_stealth_config(cls) -> Dict:
        """获取Playwright的反检测配置"""
        resolution = random.choice(cls.SCREEN_RESOLUTIONS)
        user_agent = random.choice(cls.USER_AGENTS)
        language = random.choice(cls.LANGUAGES)
        
        return {
            "user_agent": user_agent,
            "viewport": resolution,
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": language,
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            },
            "java_script_enabled": True,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ],
            "stealth_options": {
                "webdriver": True,
                "chrome_app": True,
                "chrome_csi": True,
                "chrome_load_times": True,
                "chrome_runtime": True,
                "iframe_content_window": True,
                "media_codecs": True,
                "navigator_hardware_concurrency": True,
                "navigator_languages": True,
                "navigator_permissions": True,
                "navigator_plugins": True,
                "navigator_webdriver": True,
                "webgl_vendor": True,
                "window_outerdimensions": True
            }
        }
    
    @classmethod
    def _get_legacy_stealth_config(cls) -> Dict:
        """获取传统引擎的反检测配置"""
        user_agent = random.choice(cls.USER_AGENTS)
        language = random.choice(cls.LANGUAGES)
        
        return {
            "headers": {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": language,
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            },
            "timeout": 30,
            "allow_redirects": True,
            "verify": True
        }
    
    @classmethod
    def get_random_delays(cls) -> Dict[str, float]:
        """获取随机延迟配置"""
        return {
            "page_load": random.uniform(1.0, 3.0),
            "between_requests": random.uniform(0.5, 2.0),
            "scroll_delay": random.uniform(0.8, 1.5),
            "click_delay": random.uniform(0.2, 0.8),
            "typing_delay": random.uniform(0.1, 0.3)
        }
    
    @classmethod
    def get_humanlike_scroll_params(cls) -> Dict:
        """获取人类化滚动参数"""
        return {
            "scroll_step": random.randint(200, 400),
            "scroll_delay": random.uniform(0.8, 1.5),
            "pause_probability": 0.3,
            "pause_duration": random.uniform(1.0, 3.0),
            "back_scroll_probability": 0.1,
            "back_scroll_distance": random.randint(50, 150)
        } 