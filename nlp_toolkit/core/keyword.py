"""关键词抽取模块。

基于 jieba 的 TextRank / TF-IDF 算法抽取文本关键词，并给出权重。
可视化层可据此绘制词频柱状图或词云。
"""

from .base import BaseAnalyzer


class KeywordAnalyzer(BaseAnalyzer):
    name = "keyword"
    description = "关键词抽取（关键词 + 权重 + 词云）"

    def __init__(self, top_k: int = 10, algorithm: str = "textrank"):
        import jieba
        import jieba.analyse

        self._jieba = jieba
        self._analyse = jieba.analyse
        # 关闭 jieba 的日志输出，保持命令行整洁
        jieba.setLogLevel(20)
        self.top_k = top_k
        self.algorithm = algorithm

    def analyze(self, text: str):
        """抽取关键词。

        返回:
            dict: {
                "keywords": [{"word": ..., "weight": float}, ...],  # 按权重降序
                "top_k": int,
                "algorithm": str,
            }
        """
        text = (text or "").strip()
        if not text:
            raise ValueError("输入文本为空")

        if self.algorithm == "tfidf":
            pairs = self._analyse.extract_tags(
                text, topK=self.top_k, withWeight=True, allowPOS=()
            )
        else:  # textrank
            pairs = self._analyse.textrank(
                text, topK=self.top_k, withWeight=True, allowPOS=("ns", "n", "vn", "v", "nr")
            )

        keywords = [{"word": w, "weight": round(float(s), 4)} for w, s in pairs]
        return {"keywords": keywords, "top_k": self.top_k, "algorithm": self.algorithm}
