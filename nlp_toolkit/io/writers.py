"""结果写出模块。

将分析结果统一序列化为 CSV / JSON，便于交付与二次处理。
"""

import csv
import json
import os


def _flatten(task: str, item: dict):
    """把单次分析结果拍平成一行（供 CSV 使用）。"""
    base = {"id": item.get("id"), "text": item.get("text"), "task": task}
    data = item.get("data", {})
    if task == "sentiment":
        base.update(
            {
                "sentiment": data.get("sentiment"),
                "confidence": data.get("confidence"),
            }
        )
    elif task == "ner":
        ents = data.get("entities", [])
        base.update(
            {
                "entities": "; ".join(f"{e['word']}/{e['type']}" for e in ents),
                "entity_count": len(ents),
            }
        )
    elif task == "keyword":
        kws = data.get("keywords", [])
        base.update(
            {
                "keywords": "; ".join(f"{k['word']}({k['weight']})" for k in kws),
            }
        )
    elif task == "classification":
        base.update(
            {
                "category": data.get("category"),
                "total_hits": data.get("total_hits"),
            }
        )
    return base


def write_csv(task: str, items: list, path: str):
    """将一批结果写入 CSV。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    rows = [_flatten(task, it) for it in items]
    if not rows:
        return path
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_json(items: list, path: str):
    """将一批结果写入 JSON。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path
