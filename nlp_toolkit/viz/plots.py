"""可视化模块。

基于 matplotlib 生成分析图表：
- 情感分布饼图（批量情感分析结果）
- 关键词词频柱状图
- 关键词词云（可选，需 wordcloud，缺失时自动跳过）

所有图片使用 Agg 后端生成，不依赖图形界面，可直接落盘或供 Web 展示。
"""

import os

import matplotlib

matplotlib.use("Agg")  # 无界面环境下必须设置为非交互后端
import matplotlib.pyplot as plt

# 让 matplotlib 正确显示中文（优先 Windows 常见中文字体，缺失时回退）
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False  # 修复负号显示为方块的问题


def sentiment_pie(results, out_path):
    """绘制情感分布饼图。

    参数:
        results: 情感分析返回 dict 列表（每个含 "sentiment"）
        out_path: 输出图片路径
    """
    pos = sum(1 for r in results if r.get("sentiment") == "positive")
    neg = sum(1 for r in results if r.get("sentiment") == "negative")
    others = len(results) - pos - neg

    labels, sizes, colors = [], [], []
    if pos:
        labels.append(f"正面 {pos}")
        sizes.append(pos)
        colors.append("#E24B4A")
    if neg:
        labels.append(f"负面 {neg}")
        sizes.append(neg)
        colors.append("#378ADD")
    if others:
        labels.append(f"其他 {others}")
        sizes.append(others)
        colors.append("#B4B2A9")

    fig, ax = plt.subplots(figsize=(5, 5))
    if sizes:
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
    else:
        ax.text(0.5, 0.5, "无数据", ha="center", va="center")
    ax.set_title("情感分布")
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def keyword_bar(keywords, out_path, top_n=10):
    """绘制关键词词频柱状图。

    参数:
        keywords: [{"word":, "weight":}, ...]
        out_path: 输出路径
    """
    top = keywords[:top_n][::-1]  # 倒序使最大值在顶部
    words = [k["word"] for k in top]
    weights = [k["weight"] for k in top]

    fig, ax = plt.subplots(figsize=(6, max(3, len(words) * 0.4)))
    ax.barh(words, weights, color="#1D9E75")
    ax.set_xlabel("权重")
    ax.set_title("关键词权重 Top %d" % len(words))
    for i, v in enumerate(weights):
        ax.text(v, i, f" {v:.3f}", va="center", fontsize=9)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def wordcloud_image(keywords, out_path, width=600, height=400):
    """生成关键词词云（可选功能）。

    依赖 wordcloud 库；若未安装则直接返回 None，调用方降级为柱状图。
    """
    try:
        from wordcloud import WordCloud
    except ImportError:
        return None

    freq = {k["word"]: float(k["weight"]) for k in keywords}
    if not freq:
        return None
    wc = WordCloud(
        font_path=None, width=width, height=height, background_color="white"
    ).generate_from_frequencies(freq)
    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


__all__ = ["sentiment_pie", "keyword_bar", "wordcloud_image"]
