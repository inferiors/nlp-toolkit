# 中文 NLP 分析工具箱（nlp_toolkit）

一个基于 [PaddleHub](https://github.com/PaddlePaddle/PaddleHub) 的**多任务中文文本分析项目**，提供情感分析、命名实体识别、关键词抽取、文本分类四大能力，并配套命令行（CLI）、Web 网页、批量处理、可视化与历史记录。

> 本项目由最初的单文件情感分析脚本（`ai.py`）升级而来，旨在成为一个结构清晰、可演示、可扩展的中文 NLP 入门级项目。

## 功能一览

| 任务 | 引擎 | 说明 |
|------|------|------|
| 情感分析 `sentiment` | PaddleHub `senta_bilstm` | 中文文本正/负面二分类 + 置信度 |
| 命名实体识别 `ner` | PaddleHub `LAC` | 抽取人名 / 地名 / 机构名 / 时间等实体 |
| 关键词抽取 `keyword` | jieba (TextRank) | 关键词及权重，支持词云 |
| 文本分类 `classification` | 主题词典规则 | 美食 / 影视 / 天气 / 科技 / 财经 / 体育 归类 |

## 项目结构

```
nlp_toolkit/
├── config.py            # 全局配置（路径、任务注册表）
├── core/                # 分析层：四个分析器 + 统一工厂
│   ├── base.py          # 分析器抽象基类
│   ├── sentiment.py     # 情感分析
│   ├── ner.py           # 命名实体识别
│   ├── keyword.py       # 关键词抽取
│   └── classification.py# 文本分类
├── io/                  # 支撑层：文件读取 / 结果写出
├── viz/                 # 支撑层：matplotlib 可视化
├── storage/             # 支撑层：SQLite 历史记录
├── api/                 # Web 服务（Flask）
├── web/static/          # 简易前端页面
├── data/sample.txt      # 示例文本
└── tests/               # 单元测试
cli.py                   # 命令行入口
run.py                   # 一键启动 Web
requirements.txt         # 依赖清单
```

## 环境准备

**必须使用已安装 PaddleHub 的 Python**（本项目开发/验证环境）：

```
D:\python\python310\python310.exe     # 已预装 paddlehub 2.4.0 + paddle 2.6.2
```

安装新增轻量依赖：

```
D:\python\python310\python310.exe -m pip install -r nlp_toolkit/requirements.txt
```

## 使用方式

### 1. 命令行（CLI）

```bash
# 单条文本情感分析
python -m nlp_toolkit.cli analyze --task sentiment --text "这部电影太好看了"

# 批量分析（txt 按行 / csv 指定列），结果导出 CSV
python -m nlp_toolkit.cli analyze --task keyword --file nlp_toolkit/data/sample.txt --out output/kw.csv

# 生成可视化报告
python -m nlp_toolkit.cli report --task sentiment --file nlp_toolkit/data/sample.txt
python -m nlp_toolkit.cli report --task keyword --file nlp_toolkit/data/sample.txt

# 查看 / 清空历史
python -m nlp_toolkit.cli history --limit 10
python -m nlp_toolkit.cli history --clear
```

### 2. Web 网页

```bash
python run.py                 # 默认 http://localhost:5000/
# 或
python -m nlp_toolkit.cli serve --port 5000
```

浏览器打开 `http://localhost:5000/`，选择任务、粘贴文本即可分析；下方展示最近历史。

### 3. 作为库调用

```python
from nlp_toolkit.core import get_analyzer

analyzer = get_analyzer("sentiment")
print(analyzer.analyze("这家餐厅的菜很难吃"))   # {'sentiment': 'negative', 'confidence': 0.99, ...}
```

## 测试

```bash
python nlp_toolkit/tests/test_core.py    # 无需 pytest，直接运行
```

## 扩展指南

- **新增任务**：在 `core/` 下继承 `BaseAnalyzer` 实现 `analyze()`，并在 `core/__init__.py` 的 `_ANALYZER_CLASSES` 与 `config.TASK_REGISTRY` 注册即可，CLI / Web / 批量流程自动支持。
- **替换引擎**：情感 / 实体当前用 PaddleHub，可在对应模块内替换为 transformers 等模型，对外接口不变。
