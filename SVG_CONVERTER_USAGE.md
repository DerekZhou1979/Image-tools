# SVG转PNG转换器使用指南

## 📖 概述

Image-tools v4.0 现在包含了强大的SVG到PNG转换功能，支持多种转换引擎和高质量输出。

## 🔧 可用转换引擎

1. **CairoSVG** (推荐) - 高质量矢量转换
2. **svglib + ReportLab** - 专业PDF/图形处理库
3. **Pillow** - 备用方案，创建占位图

## 🚀 使用方法

### 方法1: 使用启动脚本 (推荐)

```bash
# SVG转换模式
./start_download_fixed.sh svg

# 常规下载会自动转换发现的SVG文件
./start_download_fixed.sh
```

### 方法2: 直接运行转换工具

```bash
# 基本转换
python utils/svg_converter_tool.py images

# 或使用模块方式
python -m utils.svg_converter_tool images

# 检查可用引擎
python utils/svg_converter_tool.py --check-engines
```

## ⚙️ 转换选项

### 基本选项

```bash
python utils/svg_converter_tool.py [目录] [选项]

选项:
  --width 512           # 输出宽度 (默认: 512)
  --height 512          # 输出高度 (默认: 512)
  --quality high        # 质量设置: low/medium/high
  --keep-original       # 保留原始SVG文件 (默认)
  --remove-original     # 删除原始SVG文件
  --suffix "_converted" # 输出文件后缀
```

### 使用示例

```bash
# 转换为高分辨率PNG
python utils/svg_converter_tool.py images --width 1024 --height 1024

# 转换并删除原始文件
python utils/svg_converter_tool.py images --remove-original

# 带后缀转换
python utils/svg_converter_tool.py images --suffix "_png"

# 检查转换引擎状态
python utils/svg_converter_tool.py --check-engines
```

## 📁 文件结构

```
Image-tools/
├── utils/
│   ├── svg_converter.py          # 核心转换类
│   ├── svg_converter_tool.py     # 命令行工具
│   └── __init__.py               # 模块初始化
├── images/                       # 图片目录
├── image_download_config.json    # 配置文件 (包含SVG设置)
└── start_download_fixed.sh       # 启动脚本
```

## 🔧 配置文件设置

在 `image_download_config.json` 中：

```json
{
  "svg_conversion": {
    "enabled": true,
    "auto_convert": true,
    "width": 512,
    "height": 512,
    "quality": "high",
    "keep_original": true,
    "engines": ["cairosvg", "svglib", "pillow"],
    "fallback_mode": true,
    "batch_process": true
  }
}
```

### 配置说明

- `enabled`: 启用SVG转换功能
- `auto_convert`: 下载SVG后自动转换
- `width/height`: 默认输出尺寸
- `quality`: 转换质量级别
- `keep_original`: 是否保留原始SVG文件
- `engines`: 转换引擎优先级列表
- `fallback_mode`: 引擎失败时自动切换
- `batch_process`: 批量处理模式

## 🎯 使用场景

### 1. 网站图标转换

```bash
# 下载并转换网站图标
./start_download_fixed.sh
# 自动发现并转换SVG图标为PNG
```

### 2. 批量SVG处理

```bash
# 处理特定目录的所有SVG
python utils/svg_converter_tool.py /path/to/svg/files --width 256 --height 256
```

### 3. 高质量图标生成

```bash
# 生成高分辨率PNG图标
python utils/svg_converter_tool.py images --width 2048 --height 2048 --quality high
```

## 🔍 故障排除

### 问题1: 转换引擎不可用

```bash
# 安装CairoSVG (推荐)
pip install cairosvg

# 安装svglib + reportlab
pip install svglib reportlab
```

### 问题2: 转换质量不佳

- 尝试增加输出分辨率: `--width 1024 --height 1024`
- 使用高质量设置: `--quality high`
- 确保使用CairoSVG引擎

### 问题3: 文件路径问题

```bash
# 使用绝对路径
python utils/svg_converter_tool.py /absolute/path/to/images

# 或从项目根目录运行
python -m utils.svg_converter_tool images
```

## 📊 性能建议

1. **批量处理**: 一次性转换多个文件比单独转换更高效
2. **合理分辨率**: 根据实际需要选择分辨率，避免过大文件
3. **引擎选择**: CairoSVG提供最佳质量，Pillow作为备用
4. **存储空间**: 考虑是否需要保留原始SVG文件

## 🧩 编程接口

### 在Python代码中使用

```python
from utils.svg_converter import SVGConverter

# 创建转换器
converter = SVGConverter(default_width=512, default_height=512)

# 转换单个文件
success = converter.convert_svg_to_png('icon.svg', 'icon.png')

# 批量转换目录
stats = converter.convert_directory('images/')
print(f"转换成功: {stats['converted']} 个文件")
```

### 便捷函数

```python
from utils.svg_converter import convert_svg_images

# 一行代码转换目录
stats = convert_svg_images('images/', keep_original=True)
```

## ✨ 特色功能

- **多引擎支持**: 自动选择最佳可用引擎
- **智能回退**: 引擎失败时自动切换备用方案
- **质量控制**: 支持多种质量级别设置
- **批量处理**: 高效的批量转换算法
- **路径智能**: 自动处理相对和绝对路径
- **状态监控**: 详细的转换状态和统计信息

---

## 🎉 总结

SVG转PNG转换器为Image-tools项目增加了强大的图像格式转换能力，特别适合处理现代网站中广泛使用的SVG图标和矢量图形。通过多引擎支持和智能回退机制，确保在各种环境下都能获得最佳的转换效果。 