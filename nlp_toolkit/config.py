"""项目全局配置。

集中管理模型选择、路径、数据库位置等，避免把常量散落在各模块里。
所有路径都基于本文件所在目录向上推导，确保无论在哪个工作目录运行都能定位资源。
"""

import os

# 项目根目录：本文件位于 nlp_toolkit/config.py，故根目录为上一级
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录：存放示例文本
DATA_DIR = os.path.join(BASE_DIR, "data")

# 输出目录：可视化图片、批量结果等默认落盘位置
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# SQLite 历史数据库路径
HISTORY_DB = os.path.join(BASE_DIR, "nlp_history.db")

# 默认示例文本
SAMPLE_TEXT = (
    "百度公司位于北京海淀区，李彦宏创办了这家人工智能企业。"
    "今天天气晴朗，我去电影院看了一部非常好看的科幻电影，"
    "餐厅的菜品味道鲜美，服务态度也很周到，整体体验非常满意。"
)


# 任务清单：任务名 -> 中文描述，供 CLI / Web 动态展示可用能力
TASK_REGISTRY = {
    "sentiment": "情感分析（正面 / 负面 + 置信度）",
    "ner": "命名实体识别（人名 / 地名 / 机构名等）",
    "keyword": "关键词抽取（关键词 + 权重 + 词云）",
    "classification": "文本分类（基于主题词典的规则归类）",
}


def available_tasks():
    """返回当前所有已注册的任务名列表。"""
    return list(TASK_REGISTRY.keys())
