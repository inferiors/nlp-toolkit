"""便捷启动脚本。

双击或在命令行运行即可启动 Web 网页服务：
    python run.py            # 默认 0.0.0.0:5000
    python run.py --port 8088
"""

import sys
import os

# 确保能 import nlp_toolkit（脚本位于项目根目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp_toolkit.api import create_app


def main():
    import argparse

    parser = argparse.ArgumentParser(description="启动 NLP 工具箱 Web 服务")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    print(f"NLP 工具箱已启动：http://localhost:{args.port}/")
    create_app().run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
