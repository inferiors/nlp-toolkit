"""输入读取模块。

支持从纯文本（按行拆分）与 CSV（指定列）读取待分析文本，
统一返回 [{ "id": int, "text": str }, ...]，供批量流程消费。
"""

import csv
import os


def read_text_file(path: str, one_line_one_doc: bool = True):
    """读取 txt 文件。

    参数:
        path: 文件路径
        one_line_one_doc: True 时每行作为一个文本；False 时整文件作为一个文本
    返回:
        list[dict]: [{"id":, "text":}, ...]
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if one_line_one_doc:
        texts = [ln.strip() for ln in content.splitlines() if ln.strip()]
    else:
        texts = [content.strip()] if content.strip() else []
    return [{"id": i + 1, "text": t} for i, t in enumerate(texts)]


def read_csv_column(path: str, column):
    """读取 CSV 中某一列作为文本。

    参数:
        path: csv 路径
        column: 列名（str）或列索引（int，从 0 开始）
    返回:
        list[dict]
    """
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f) if isinstance(column, int) else csv.DictReader(f)
        if isinstance(column, int):
            for i, row in enumerate(reader):
                if column < len(row) and row[column].strip():
                    rows.append({"id": i + 1, "text": row[column].strip()})
        else:
            for i, row in enumerate(reader):
                val = (row.get(column) or "").strip()
                if val:
                    rows.append({"id": i + 1, "text": val})
    return rows


def load_inputs(path: str, csv_column=None):
    """按扩展名自动分发读取。

    参数:
        path: 输入文件路径（.txt / .csv）
        csv_column: 仅 CSV 使用，指定文本所在列
    返回:
        list[dict]
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        col = csv_column if csv_column is not None else 0
        return read_csv_column(path, col)
    return read_text_file(path)
