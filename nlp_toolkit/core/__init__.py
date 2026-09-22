"""分析层入口：提供统一的分析器工厂。"""

from .base import BaseAnalyzer
from .sentiment import SentimentAnalyzer
from .ner import NerAnalyzer
from .keyword import KeywordAnalyzer
from .classification import ClassificationAnalyzer

# 任务名 -> 分析器类，便于运行时按字符串动态实例化
_ANALYZER_CLASSES = {
    "sentiment": SentimentAnalyzer,
    "ner": NerAnalyzer,
    "keyword": KeywordAnalyzer,
    "classification": ClassificationAnalyzer,
}


def get_analyzer(task_name: str, **kwargs) -> BaseAnalyzer:
    """根据任务名创建对应的分析器实例。

    参数:
        task_name (str): sentiment / ner / keyword / classification
        **kwargs: 透传给分析器构造参数（如 keyword 的 top_k）
    返回:
        BaseAnalyzer 子类实例
    异常:
        ValueError: 未知任务名
    """
    cls = _ANALYZER_CLASSES.get(task_name)
    if cls is None:
        raise ValueError(
            f"未知任务: {task_name}，可选: {list(_ANALYZER_CLASSES.keys())}"
        )
    return cls(**kwargs)


def list_analyzers():
    """列出所有可用分析器类名（调试用）。"""
    return {k: v.__name__ for k, v in _ANALYZER_CLASSES.items()}


__all__ = [
    "BaseAnalyzer",
    "SentimentAnalyzer",
    "NerAnalyzer",
    "KeywordAnalyzer",
    "ClassificationAnalyzer",
    "get_analyzer",
    "list_analyzers",
]
