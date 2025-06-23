#!/bin/bash

# ========================================
# 🔑 API密钥配置区域 
# ========================================
# 请将您的Gemini API密钥填入下面的变量中
# 获取API密钥: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=""

# 如果配置了API密钥，则导出为环境变量
if [ -n "$GEMINI_API_KEY" ]; then
    export GEMINI_API_KEY
    echo "🔐 已从脚本配置中加载API密钥"
fi

echo "🖼️ Image-tools 通用图片下载器"
echo "========================="

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查pip是否已安装
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip，请先安装pip"
    exit 1
fi

# 检查是否为Gemini模式，如果是则先检查API密钥
if [ "$1" = "gemini" ]; then
    echo "🧠 Gemini Vision AI模式检查..."
    if [ -z "$GEMINI_API_KEY" ]; then
        echo ""
        echo "❌ 未设置 GEMINI_API_KEY 环境变量"
        echo ""
        echo "🔑 请选择以下任一方式设置API密钥:"
        echo ""
        echo "   方式1 - 在脚本中配置 (推荐):"
        echo "      1. 编辑 start_download.sh 文件"
        echo "      2. 在脚本开头找到: GEMINI_API_KEY=\"\""
        echo "      3. 将您的API密钥填入引号中"
        echo "      4. 保存文件后重新运行"
        echo ""
        echo "   方式2 - 环境变量设置:"
        echo "      临时设置: export GEMINI_API_KEY='你的API密钥'"
        echo "      永久设置: echo 'export GEMINI_API_KEY=\"你的API密钥\"' >> ~/.zshrc"
        echo ""
        echo "   方式3 - 命令行传递:"
        echo "      GEMINI_API_KEY='你的API密钥' ./start_download.sh gemini"
        echo ""
        echo "💡 获取API密钥: https://makersuite.google.com/app/apikey"
        echo "💡 设置完成后，请重新运行: ./start_download.sh gemini"
        echo ""
        exit 1
    else
        echo "✅ 发现 GEMINI_API_KEY 环境变量"
        # 显示API密钥的前几位和后几位，中间用*隐藏
        masked_key="${GEMINI_API_KEY:0:8}****${GEMINI_API_KEY: -8}"
        echo "🔐 API密钥: $masked_key"
    fi
fi

echo "📦 正在安装依赖包..."
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt 2>/dev/null || echo "依赖包安装可能失败，继续运行..."

echo ""
# 创建images目录（如果不存在）
mkdir -p images

# 检查是否为Gemini模式，如果是则跳过清理
if [ "$1" = "gemini" ] || [ "$1" = "rename" ]; then
    echo "🧠 Gemini/重命名模式: 保留现有图片文件，跳过清理步骤..."
    if [ "$(ls -A images/)" ]; then
        echo "📂 发现 $(ls images/ | wc -l) 个现有图片文件"
    else
        echo "📂 images目录为空"
    fi
else
    echo "🧹 清理旧的下载文件..."
    # 清空images目录中的所有文件
    if [ "$(ls -A images/)" ]; then
        echo "📂 发现 $(ls images/ | wc -l) 个旧文件，正在清理..."
        rm -f images/*
        echo "✅ 旧文件清理完成"
    else
        echo "📂 images目录为空，无需清理"
    fi
fi

echo ""
echo "🚀 开始运行图片下载器..."
echo ""
echo "📖 可用模式："
echo "   默认模式: 全量下载所有找到的图片"
echo "   匹配模式: 根据配置文件智能匹配特定图片"
echo "   手动模式: 显示所有图片供用户选择"
echo "   重命名模式: 对已下载的图片进行智能重命名"
echo "   Gemini模式: 使用AI视觉识别进行智能重命名 🧠"
echo ""

# 检查是否有命令行参数
if [ $# -eq 0 ]; then
    echo "🔄 使用默认的全量下载模式..."
    python3 image_downloader.py --all
elif [ "$1" = "match" ]; then
    echo "🎯 使用智能匹配模式..."
    python3 image_downloader.py --match
elif [ "$1" = "manual" ]; then
    echo "👤 使用手动选择模式..."
    python3 image_downloader.py --manual
elif [ "$1" = "all" ]; then
    echo "📥 使用全量下载模式..."
    python3 image_downloader.py --all
elif [ "$1" = "rename" ]; then
    echo "🤖 使用智能重命名模式..."
    python3 image_downloader.py --rename
elif [ "$1" = "gemini" ]; then
    echo "🧠 使用Gemini Vision AI智能重命名模式..."
    echo "💡 提示: 本次运行可能产生API费用 (约0.24美元/97张图片)"
    python3 image_downloader.py --gemini
else
    echo "❓ 未知参数: $1"
    echo "可用参数: all, match, manual, rename, gemini"
    echo "使用默认的全量下载模式..."
    python3 image_downloader.py --all
fi

echo ""
echo "✨ 操作完成！请查看images目录中的图片文件。"
echo ""
echo "💡 使用提示："
echo "   ./start_download.sh        - 全量下载模式（默认）"
echo "   ./start_download.sh all    - 全量下载模式"
echo "   ./start_download.sh match  - 智能匹配模式"
echo "   ./start_download.sh manual - 手动选择模式"
echo "   ./start_download.sh rename - 智能重命名模式"
echo "   ./start_download.sh gemini - Gemini Vision AI重命名模式 🧠" 