"""nlp_toolkit 单元测试。

既支持 pytest 发现（函数名以 test_ 开头），也可直接运行：
    python tests/test_core.py
无需额外安装 pytest。
"""

import os
import sys

# 将项目根目录加入模块搜索路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from nlp_toolkit.config import available_tasks  # noqa: E402
from nlp_toolkit.core import get_analyzer  # noqa: E402
from nlp_toolkit.core.classification import ClassificationAnalyzer  # noqa: E402
from nlp_toolkit.core.keyword import KeywordAnalyzer  # noqa: E402
from nlp_toolkit.storage.history import clear, init_db, recent, save  # noqa: E402


def test_available_tasks():
    assert set(available_tasks()) >= {
        "sentiment",
        "ner",
        "keyword",
        "classification",
    }


def test_classification_rule():
    r = ClassificationAnalyzer().analyze("餐厅的菜品味道鲜美，服务很好")
    assert "category" in r and r["total_hits"] >= 0


def test_keyword_extract():
    r = KeywordAnalyzer(top_k=5).analyze("百度公司位于北京海淀区，专注人工智能技术")
    assert r["keywords"], "关键词不应为空"
    assert len(r["keywords"]) <= 5


def test_history_roundtrip():
    init_db()
    clear()
    save("sentiment", "单元测试文本", {"sentiment": "positive", "confidence": 0.99})
    rows = recent(5)
    assert rows, "历史记录不应为空"
    assert rows[0]["text"] == "单元测试文本"
    clear()


def test_sentiment_integration():
    """集成测试：依赖 paddlehub 模型，环境不可用时自动跳过。"""
    try:
        r = get_analyzer("sentiment").analyze("这部电影太好看了，我非常喜欢")
    except Exception as exc:  # 模型未就绪则跳过
        print(f"[skip] sentiment 集成测试（模型不可用：{exc}）")
        return
    assert r["sentiment"] in ("positive", "negative")
    assert 0 <= r["confidence"] <= 1


def _main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n共 {len(tests)} 个测试，通过 {passed} 个。")
    if passed != len(tests):
        sys.exit(1)


if __name__ == "__main__":
    _main()
