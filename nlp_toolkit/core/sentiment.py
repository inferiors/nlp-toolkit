"""情感分析模块。

基于 PaddleHub 的 senta_bilstm 模型，对中文文本做二分类情感判断，
返回情感标签（positive / negative）与对应置信度。
"""

from .base import BaseAnalyzer


class SentimentAnalyzer(BaseAnalyzer):
    name = "sentiment"
    description = "情感分析（正面 / 负面 + 置信度）"

    def __init__(self):
        import paddlehub as hub

        # 首次实例化会联网下载 senta_bilstm 模型（若缓存缺失）
        self._model = hub.Module(name="senta_bilstm")

    def analyze(self, text: str):
        """分析单段文本情感。

        返回:
            dict: {
                "sentiment": "positive" | "negative",
                "confidence": float,
                "positive_probs": float,
                "negative_probs": float,
            }
        """
        text = (text or "").strip()
        if not text:
            raise ValueError("输入文本为空")

        results = self._model.sentiment_classify(texts=[text])
        item = results[0]
        sentiment = item["sentiment_key"]
        confidence = (
            item["positive_probs"] if sentiment == "positive" else item["negative_probs"]
        )
        return {
            "sentiment": sentiment,
            "confidence": round(float(confidence), 4),
            "positive_probs": round(float(item["positive_probs"]), 4),
            "negative_probs": round(float(item["negative_probs"]), 4),
        }
