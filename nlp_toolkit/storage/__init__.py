"""存储层入口。"""

from .history import init_db, save, recent, clear

__all__ = ["init_db", "save", "recent", "clear"]
