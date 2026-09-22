"""历史记录模块。

使用 SQLite 持久化每一次分析请求，便于回溯、统计与审计。
数据库文件位置见 config.HISTORY_DB。
"""

import json
import os
import sqlite3
from datetime import datetime

from nlp_toolkit.config import HISTORY_DB


def _connect():
    conn = sqlite3.connect(HISTORY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """创建历史表（幂等）。"""
    os.makedirs(os.path.dirname(os.path.abspath(HISTORY_DB)), exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                text TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save(task: str, text: str, result):
    """保存一条分析记录。

    参数:
        task: 任务名
        text: 输入文本
        result: 任意可 JSON 序列化的结果
    返回:
        int: 新插入记录的自增 id
    """
    init_db()
    payload = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO analysis_history (task, text, result, created_at) "
            "VALUES (?, ?, ?, ?)",
            (task, text, payload, datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid


def recent(limit: int = 20):
    """查询最近 limit 条记录。"""
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, task, text, result, created_at FROM analysis_history "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def clear():
    """清空历史表。"""
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM analysis_history")
    return True


__all__ = ["init_db", "save", "recent", "clear"]
