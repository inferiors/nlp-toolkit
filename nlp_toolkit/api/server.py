"""Web 服务模块（Flask）。

提供简易网页与 HTTP API：
- GET  /              网页首页
- GET  /api/tasks     可用任务清单
- POST /api/analyze   单条文本分析  body: {"task":, "text":}
- GET  /api/history   最近分析历史
"""

import os

from flask import Flask, jsonify, request, send_from_directory

from nlp_toolkit.config import TASK_REGISTRY
from nlp_toolkit.core import get_analyzer
from nlp_toolkit.storage import history

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "static")


def create_app():
    app = Flask(__name__, static_folder=None)
    history.init_db()

    @app.route("/")
    def index():
        return send_from_directory(WEB_DIR, "index.html")

    @app.route("/api/tasks")
    def tasks():
        return jsonify(TASK_REGISTRY)

    @app.route("/api/analyze", methods=["POST"])
    def analyze():
        data = request.get_json(force=True, silent=True) or {}
        task = data.get("task")
        text = (data.get("text") or "").strip()
        if not task or not text:
            return jsonify(error="task 和 text 均为必填"), 400
        try:
            analyzer = get_analyzer(task)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        result = analyzer.safe_analyze(text)
        if not result.get("ok"):
            return jsonify(error=result.get("error", "分析失败")), 500
        history.save(task, text, result["data"])
        return jsonify(result=result["data"], task=task)

    @app.route("/api/history")
    def hist():
        return jsonify(history.recent(20))

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
