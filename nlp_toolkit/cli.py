"""命令行入口。

子命令：
    analyze   单条或批量文本分析（支持 txt / csv 输入，结果导出 csv / json）
    serve     启动 Web 网页服务
    report    对一批文本生成可视化图表（情感饼图 / 关键词柱状图 / 词云）
    history   查看或清空分析历史

示例：
    python -m nlp_toolkit.cli analyze --task sentiment --text "这部电影太好看了"
    python -m nlp_toolkit.cli analyze --task keyword --file data/sample.txt --out output/kw.csv
    python -m nlp_toolkit.cli serve --port 5000
    python -m nlp_toolkit.cli report --task sentiment --file data/sample.txt
"""

import argparse
import os

from nlp_toolkit.config import OUTPUT_DIR, SAMPLE_TEXT, available_tasks
from nlp_toolkit.core import get_analyzer
from nlp_toolkit.io import load_inputs, write_csv, write_json
from nlp_toolkit.storage import history
from nlp_toolkit.viz import sentiment_pie, keyword_bar, wordcloud_image


def _build_analyzer(task, top_k):
    kwargs = {"top_k": top_k} if task == "keyword" else {}
    return get_analyzer(task, **kwargs)


def cmd_analyze(args):
    analyzer = _build_analyzer(args.task, args.top_k)

    if args.file:
        inputs = load_inputs(args.file, args.csv_column)
        print(f"已从 {args.file} 载入 {len(inputs)} 条文本。")
    else:
        text = args.text if args.text is not None else input("请输入要分析的文本: ")
        inputs = [{"id": 1, "text": text}]

    items, ok, fail = [], 0, 0
    for it in inputs:
        res = analyzer.safe_analyze(it["text"])
        if res.get("ok"):
            ok += 1
            if not args.no_history:
                history.save(args.task, it["text"], res["data"])
            items.append({"id": it["id"], "text": it["text"], "data": res["data"]})
            _print_one(args.task, res["data"])
        else:
            fail += 1
            print(f"[失败] id={it['id']}: {res.get('error')}")

    print(f"\n完成：成功 {ok} 条，失败 {fail} 条。")
    if args.out:
        if args.out.lower().endswith(".json"):
            path = write_json(items, args.out)
        else:
            path = write_csv(args.task, items, args.out)
        print(f"结果已写出：{path}")


def _print_one(task, data):
    if task == "sentiment":
        print(f"  情感: {data['sentiment']} (置信度 {data['confidence']})")
    elif task == "ner":
        ents = data["entities"]
        print(f"  实体({len(ents)}): " + "; ".join(f"{e['word']}/{e['type']}" for e in ents))
    elif task == "keyword":
        print("  关键词: " + ", ".join(f"{k['word']}({k['weight']})" for k in data["keywords"]))
    elif task == "classification":
        print(f"  分类: {data['category']} (命中 {data['total_hits']})")


def cmd_serve(args):
    from nlp_toolkit.api import create_app

    print(f"启动 Web 服务：http://{args.host}:{args.port}/")
    create_app().run(host=args.host, port=args.port, debug=False)


def cmd_report(args):
    analyzer = _build_analyzer(args.task, args.top_k)
    if args.file:
        inputs = load_inputs(args.file)
    else:
        inputs = [{"id": 1, "text": args.text or SAMPLE_TEXT}]

    texts = [it["text"] for it in inputs if it["text"].strip()]
    results = [analyzer.analyze(t) for t in texts]

    if args.task == "sentiment":
        out = os.path.join(OUTPUT_DIR, "sentiment_pie.png")
        sentiment_pie([r for r in results], out)
        print(f"情感饼图已生成：{out}")
    elif args.task == "keyword":
        merged = {}
        for r in results:
            for k in r["keywords"]:
                merged[k["word"]] = max(merged.get(k["word"], 0), k["weight"])
        kw = [{"word": w, "weight": v} for w, v in merged.items()]
        kw.sort(key=lambda x: x["weight"], reverse=True)
        bar = os.path.join(OUTPUT_DIR, "keyword_bar.png")
        keyword_bar(kw, bar)
        print(f"关键词柱状图已生成：{bar}")
        wc = wordcloud_image(kw, os.path.join(OUTPUT_DIR, "keyword_wordcloud.png"))
        if wc:
            print(f"词云已生成：{wc}")
        else:
            print("（未安装 wordcloud，已跳过词云，可 pip install wordcloud 启用）")
    else:
        print(f"任务 {args.task} 暂不支持可视化报告。")


def cmd_history(args):
    if args.clear:
        history.clear()
        print("历史已清空。")
        return
    rows = history.recent(args.limit)
    if not rows:
        print("暂无历史记录。")
        return
    for r in rows:
        print(f"[{r['id']}] {r['task']} | {r['created_at']} | {r['text'][:30]}...")


def build_parser():
    parser = argparse.ArgumentParser(description="中文 NLP 分析工具箱")
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="文本分析")
    p_an.add_argument("--task", required=True, choices=available_tasks(), help="任务名")
    p_an.add_argument("--text", help="待分析文本（与 --file 二选一）")
    p_an.add_argument("--file", help="输入文件（.txt 按行 / .csv 指定列）")
    p_an.add_argument("--csv-column", type=int, default=0, help="CSV 文本列索引（默认第 0 列）")
    p_an.add_argument("--out", help="结果输出路径（.csv 或 .json）")
    p_an.add_argument("--top-k", type=int, default=10, help="关键词抽取数量（仅 keyword）")
    p_an.add_argument("--no-history", action="store_true", help="不写入历史库")
    p_an.set_defaults(func=cmd_analyze)

    p_serve = sub.add_parser("serve", help="启动 Web 服务")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=5000)
    p_serve.set_defaults(func=cmd_serve)

    p_rep = sub.add_parser("report", help="生成可视化报告")
    p_rep.add_argument("--task", required=True, choices=["sentiment", "keyword"], help="仅支持 sentiment / keyword")
    p_rep.add_argument("--text", help="单条文本")
    p_rep.add_argument("--file", help="输入文件")
    p_rep.add_argument("--top-k", type=int, default=10)
    p_rep.set_defaults(func=cmd_report)

    p_his = sub.add_parser("history", help="查看 / 清空历史")
    p_his.add_argument("--limit", type=int, default=20)
    p_his.add_argument("--clear", action="store_true")
    p_his.set_defaults(func=cmd_history)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
