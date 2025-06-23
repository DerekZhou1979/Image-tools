# 🖼️ Image-tools 通用图片下载器

![Version](https://img.shields.io/badge/Version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6+-green.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个智能的通用图片下载器，集成了Google Gemini 2.5 Flash AI视觉识别技术，能够自动从任意网站下载图片、分析图片内容并智能重命名。

## ✨ 主要特性

### 🤖 AI智能重命名
- **Gemini 2.5 Flash AI**：最新的Google视觉识别技术
- **自适应思维**：根据图片复杂度智能调节分析深度
- **语义化命名**：基于图片内容生成有意义的文件名
- **内容自动识别**：产品图、横幅图、新闻图、图标等自动分类

### 📥 多模式下载
- **全量下载**：下载所有找到的图片
- **智能匹配**：根据配置文件智能匹配特定图片
- **手动选择**：显示所有图片供用户选择
- **AI重命名**：使用Gemini Vision AI进行智能重命名
- **基础重命名**：使用规则匹配进行智能重命名

### 🛡️ 稳定可靠
- **错误处理**：完善的错误处理和重试机制
- **地理位置检测**：多API备用，自动切换最优服务
- **网络优化**：递增超时、智能重试
- **进度监控**：实时显示下载进度和统计信息

## 🚀 快速开始

### 📦 安装依赖

```bash
# 自动安装（推荐）
./start_download.sh

# 手动安装
pip install -r requirements.txt
```

### ⚙️ 配置目标网站

编辑 `image_download_config.json` 文件：

```json
{
  "description": "通用图片下载配置文件",
  "base_url": "https://your-target-website.com/",
  "site_name": "目标网站名称",
  "download_settings": {
    "delay_between_downloads": 0.5,
    "max_retries": 3,
    "timeout": 30
  }
}
```

### 🔑 配置API密钥（仅AI模式需要）

**方式1 - 脚本内配置（推荐）：**
```bash
# 编辑 start_download.sh 文件，找到这一行：
GEMINI_API_KEY=""

# 将您的API密钥填入引号中：
GEMINI_API_KEY="your_api_key_here"
```

**方式2 - 环境变量配置：**
```bash
# 临时设置
export GEMINI_API_KEY='your_api_key_here'

# 永久设置
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**获取API密钥：** https://makersuite.google.com/app/apikey

### 🎯 运行程序

```bash
# 全量下载模式（默认）
./start_download.sh

# 智能匹配模式
./start_download.sh match

# 手动选择模式
./start_download.sh manual

# 基础智能重命名模式
./start_download.sh rename

# Gemini AI智能重命名模式 🧠
./start_download.sh gemini
```

## 📁 项目结构

```
Image-tools/
├── image_downloader.py              # 主程序文件 (1275行)
├── start_download.sh                # Linux/Mac启动脚本
├── start_download.bat               # Windows启动脚本  
├── image_download_config.json       # 配置文件
├── requirements.txt                 # Python依赖包
├── README.md                        # 本文档
└── images/                          # 图片保存目录
    ├── image_001_hero_banner.jpg
    ├── image_002_product_main.jpg
    └── ... (更多智能命名的图片)
```

## 🎭 运行模式详解

### 🔄 全量下载模式（默认）
```bash
./start_download.sh all
# 或
./start_download.sh
```
- 下载网站上所有找到的图片
- 按照发现顺序命名：`image_001.jpg`, `image_002.jpg`...
- 适合首次使用或需要完整图片库

### 🎯 智能匹配模式
```bash
./start_download.sh match
```
- 根据配置文件中的关键词智能匹配图片
- 可自定义分类，涵盖网站所有主要区域
- 精确命名：`hero_main_banner.jpg`

### 👤 手动选择模式
```bash
./start_download.sh manual
```
- 显示所有找到的图片URL和信息
- 用户可以手动选择需要下载的图片
- 适合精确控制下载内容

### 🤖 基础智能重命名模式
```bash
./start_download.sh rename
```
- 对已下载的图片进行智能重命名
- 基于规则匹配和文件特征分析
- 不需要API密钥，本地处理

### 🧠 Gemini AI智能重命名模式
```bash
./start_download.sh gemini
```
- 使用Google Gemini 2.5 Flash AI进行图片内容识别
- 生成语义化的有意义文件名
- 需要配置API密钥

## 🤖 Gemini 2.5 Flash AI功能

### 🆕 新特性亮点

#### 🧠 自适应思维
- **智能调节**：根据图片复杂度自动调整分析深度
- **成本优化**：简单图片快速处理，复杂图片深度分析
- **过程透明**：可查看AI的分析思路和决策过程

#### 📊 性能提升
| 能力 | Gemini 1.5 Flash | **Gemini 2.5 Flash** | 提升 |
|------|------------------|---------------------|------|
| 图像理解 | 56.4% | **65.4%** | +9% |
| 视觉推理 | 71.7% | **79.7%** | +8% |
| 数学推理 | 27.5% | **72.0%** | +44.5% |

#### 🔍 图像识别能力
- **图片类型**：hero/banner、product、detail、icon、news、team
- **内容特征**：主图、缩略图、产品图、新闻图等
- **质量评估**：high、medium、low质量自动判断

### 💰 成本分析
- **基础分析**：约 $0.15 (100张图片)
- **深度思维分析**：约 $0.65 (高精度模式)
- **自适应调节**：智能平衡成本与质量

## ⚙️ 配置文件说明

### 📄 image_download_config.json
配置文件包含多个预定义图片分类：

#### 🎬 主视觉区域
```json
{
  "category": "hero_section",
  "filename": "hero_main_banner.jpg",
  "keywords": ["hero", "banner", "main", "carousel", "slide"]
}
```

#### 🎯 产品展示区域
- 特色产品、产品网格、产品详情等

#### ⭐ 内容区域
- 新闻文章、画廊图片、展示分类等

#### 🔧 UI元素
- 网站Logo、社交媒体图标等

## 🔧 高级功能

### 🎨 智能文件命名
**AI模式生成示例：**
```
原文件：image_094_1743125744961943.jpg
AI分析：{"type": "hero", "content": "主横幅", "confidence": 9}
新文件：image_hero_main_banner.jpg
```

### 🌐 地理位置检测
程序会自动检测网络环境和地理位置：
```
🌍 检测当前地理位置和网络环境...
📍 当前公网IP: 99.79.1.103
🗺️ 地理位置: Canada - Toronto
🏢 ISP: Amazon.com, Inc.
```

支持4个备用地理位置API：
- IPApi.co (主要)
- IP-API.com (备用1)
- IPInfo.io (备用2)
- HTTPBin.org (备用3)

### 🔒 安全特性
- **API密钥遮掩**：显示前8位和后8位，中间用*隐藏
- **环境变量支持**：支持多种安全的密钥配置方式
- **降级机制**：API不可用时自动回退到基础模式

## 📊 使用统计

### 典型下载结果
```
✅ 成功下载: 97张图片
❌ 下载失败: 0张图片
📁 总文件大小: 156.8 MB
⏱️ 总耗时: 2分15秒
🤖 AI重命名: 92/97张成功
```

### 支持的图片格式
- **输入格式**：JPG, PNG, GIF, WebP, BMP
- **输出保持**：保持原始格式和质量
- **最大尺寸**：支持高达20MB的图片文件

## ⚠️ 注意事项

### 🌍 地理位置限制
Gemini API在某些地区不可用，遇到以下错误时：
```
❌ User location is not supported for the API use.
```

**解决方案：**
1. 使用VPN连接到支持的地区（如美国、英国、日本）
2. 确保VPN全局代理模式
3. 或使用基础重命名模式：`./start_download.sh rename`

### 📋 系统要求
- **Python版本**：3.6+
- **网络连接**：稳定的互联网连接
- **磁盘空间**：至少200MB可用空间
- **权限**：images目录写入权限

### 🔑 API密钥获取
1. 访问：https://makersuite.google.com/app/apikey
2. 登录Google账户
3. 点击"Create API Key"
4. 复制生成的密钥

## 🔍 故障排除

### 常见问题解决

#### 1. 网络连接问题
```bash
# 检查网络连接
curl -I https://your-target-website.com/

# 测试地理位置API
curl -s https://ipapi.co/json/
```

#### 2. API密钥问题
```bash
# 验证API密钥设置
echo $GEMINI_API_KEY

# 测试API连接
./start_download.sh gemini
```

#### 3. 依赖包问题
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 检查Python版本
python3 --version
```

#### 4. 权限问题
```bash
# 检查目录权限
ls -la images/

# 创建目录
mkdir -p images/
chmod 755 images/
```

### 🆘 获取帮助

如果遇到问题，请提供以下信息：
1. 操作系统版本
2. Python版本
3. 错误信息截图
4. 网络连接状态
5. API密钥配置状态（隐藏密钥本身）

## 📈 版本历史

### v3.0.0 (当前版本)
- ✨ 重构为通用图片下载器
- 🔧 支持任意网站图片下载
- 📝 通用化配置文件格式
- 🖼️ 改进文件命名规则

### v2.5.0
- ✨ 升级到Gemini 2.5 Flash Preview
- 🧠 添加自适应思维功能
- 🌐 增强地理位置检测
- 🔐 优化API密钥管理
- 📊 提升图像识别精度

### v2.0.0
- 🤖 集成Gemini Vision AI
- 🎯 添加多种下载模式
- 🔄 智能重命名系统
- 🛡️ 完善错误处理

### v1.0.0
- 📥 基础图片下载功能
- ⚙️ 配置文件支持
- 🎨 智能匹配算法

## 📜 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **Google AI**：提供Gemini 2.5 Flash API
- **Python社区**：优秀的开源库支持

---

## 🚀 立即开始

```bash
# 克隆项目
git clone [项目地址]
cd Image-tools

# 配置目标网站
vim image_download_config.json

# 配置API密钥（可选，仅AI模式需要）
vim start_download.sh

# 开始下载
./start_download.sh
```

**享受智能化的图片下载体验！** 🖼️✨ 