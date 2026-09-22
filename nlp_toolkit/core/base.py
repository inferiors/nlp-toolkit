"""分析器抽象基类。

所有具体分析任务（情感 / 实体 / 关键词 / 分类）都继承 BaseAnalyzer，
统一对外暴露 `analyze(text)` 接口，便于在 CLI / Web / 批量流程里无差别调用。
"""

from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """分析器基类：定义每个任务必须实现的接口与通用能力。"""

    # 子类必须覆盖：任务标识（与 config.TASK_REGISTRY 对应）
    name: str = "base"
    # 子类必须覆盖：一句话描述
    description: str = ""

    @abstractmethod
    def analyze(self, text: str):
        """对单段文本执行分析，返回结构化结果（dict / list）。

        参数:
            text (str): 待分析的文本
        返回:
            与具体任务相关的结构化数据
        """
        raise NotImplementedError

    def safe_analyze(self, text: str):
        """带异常兜底的 analyze，避免单条文本出错中断整个批量流程。"""
        try:
            return {"ok": True, "data": self.analyze(text)}
        except Exception as exc:  # noqa: BLE001 - 批量场景需要吞掉单条异常
            return {"ok": False, "error": str(exc)}
