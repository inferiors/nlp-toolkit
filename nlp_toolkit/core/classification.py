"""文本分类模块（规则词典版）。

不依赖额外训练模型，使用预定义主题词典对文本做软匹配打分，
输出最匹配的主题类别及各类别置信度。适合做演示与可扩展骨架——
后续可替换为 paddlehub / transformers 的真实分类模型而无需改动接口。
"""

from .base import BaseAnalyzer

# 主题词典：类别 -> 关键词列表
TOPIC_DICT = {
    "美食": ["餐厅", "菜", "味道", "好吃", "美食", "口味", "食材", "烹饪", "饭店", "料理"],
    "影视": ["电影", "电影院", "演员", "导演", "剧情", "科幻", "电视剧", "票房", "上映"],
    "天气": ["天气", "晴", "雨", "雪", "温度", "气温", "阴", "风", "湿度", "阳光"],
    "科技": ["人工智能", "模型", "算法", "技术", "芯片", "软件", "程序", "数据", "智能", "互联网"],
    "财经": ["公司", "企业", "股票", "股价", "营收", "投资", "金融", "利润", "市值", "经济"],
    "体育": ["比赛", "球员", "球队", "冠军", "联赛", "足球", "篮球", "运动员", "赛季", "比分"],
}


class ClassificationAnalyzer(BaseAnalyzer):
    name = "classification"
    description = "文本分类（基于主题词典的规则归类）"

    def __init__(self):
        pass

    def analyze(self, text: str):
        """按主题词典打分归类。

        返回:
            dict: {
                "category": str,            # 得分最高的类别
                "scores": {类别: 分数},     # 各类别命中次数
                "total_hits": int,
            }
        """
        text = (text or "").strip()
        if not text:
            raise ValueError("输入文本为空")

        scores = {cat: 0 for cat in TOPIC_DICT}
        for cat, words in TOPIC_DICT.items():
            for w in words:
                scores[cat] += text.count(w)

        total = sum(scores.values())
        if total == 0:
            return {"category": "其他", "scores": scores, "total_hits": 0}

        # 归一化为 0~1 的置信度
        norm = {cat: round(cnt / total, 4) for cat, cnt in scores.items()}
        category = max(norm, key=norm.get)
        return {"category": category, "scores": norm, "total_hits": total}
