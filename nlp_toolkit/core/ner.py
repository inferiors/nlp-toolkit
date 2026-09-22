"""命名实体识别（NER）模块。

基于 PaddleHub 的 LAC（Lexical Analysis of Chinese）模型，对中文文本做分词与词性 /
实体标注，并抽取出常见实体（人名、地名、机构名、时间等）。

LAC 返回的标签含义（节选）：
    PER 人名 | LOC 地名 | ORG 机构名 | TIME 时间 | n 普通名词 | v 动词 ...
"""

from .base import BaseAnalyzer

# 我们关心的实体标签 -> 中文名
# LAC 常用标签：PER 人名 / ORG 机构名 / LOC 地名 / ns 地名 / TIME 时间
ENTITY_LABELS = {
    "PER": "人名",
    "ORG": "机构名",
    "LOC": "地名",
    "ns": "地名",
    "nt": "机构名",
    "TIME": "时间",
}


class NerAnalyzer(BaseAnalyzer):
    name = "ner"
    description = "命名实体识别（人名 / 地名 / 机构名等）"

    def __init__(self):
        import paddlehub as hub

        # 首次实例化会联网下载 LAC 模型（若缓存缺失）
        self._model = hub.Module(name="lac")

    def analyze(self, text: str):
        """抽取文本中的实体。

        返回:
            dict: {
                "tokens": [{"word": ..., "tag": ...}, ...],   # 全部分词与标签
                "entities": [{"word": ..., "type": ...}, ...], # 仅实体
            }
        """
        text = (text or "").strip()
        if not text:
            raise ValueError("输入文本为空")

        # LAC 返回 [{"word": [...], "tag": [...]}, ...]，每条文本对应一个 dict
        results = self._model.lexical_analysis(texts=[text])
        item = results[0]
        words, tags = item["word"], item["tag"]

        tokens = [{"word": w, "tag": t} for w, t in zip(words, tags)]
        entities = [
            {"word": w, "type": ENTITY_LABELS.get(t, t)}
            for w, t in zip(words, tags)
            if t in ENTITY_LABELS
        ]
        return {"tokens": tokens, "entities": entities}
