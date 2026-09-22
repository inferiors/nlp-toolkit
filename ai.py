try:
    import paddlehub as hub
except ModuleNotFoundError:
    import sys
    sys.stderr.write(
        "【错误】未检测到 paddlehub 模块。\n"
        "本程序依赖 paddlehub + paddlepaddle，请使用已安装该环境的 Python 来运行，例如：\n"
        "    D:\\python\\python310\\python310.exe ai.py\n"
        "（或在对应的 Python 下执行：pip install paddlehub paddlepaddle）\n"
    )
    sys.exit(1)


class SentimentAnalyzer:
    def __init__(self):
        """初始化情感分析模型"""
        self.model = hub.Module(name="senta_bilstm")

    def analyze_sentiment(self, text):
        """
        分析输入文本的情感
        参数:
            text (str): 用户输入的文本
        返回:
            dict: 包含情感分类和置信度的字典
        """
        # 调用模型进行情感预测
        results = self.model.sentiment_classify(texts=[text])

        # 提取结果
        sentiment = results[0]['sentiment_key']
        confidence = results[0]['positive_probs'] if sentiment == 'positive' else results[0]['negative_probs']

        return {
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence
        }

    def display_result(self, result):
        """
        打印分析结果
        参数:
            result (dict): 包含情感分析信息的字典
        """
        print(f"文本: {result['text']}")
        print(f"情感分类: {result['sentiment']} (置信度: {result['confidence']:.2f})")


def main():
    try:
        # 创建情感分析器实例（首次会联网下载 senta_bilstm 模型）
        analyzer = SentimentAnalyzer()
    except Exception as e:
        import sys
        sys.stderr.write(
            "【错误】模型初始化失败：{}\n"
            "若是首次运行，请确认网络可访问 bj.bcebos.com 以下载模型；\n"
            "若提示 vocab.txt 等文件缺失，删除 C:\\Users\\shuhou\\.paddlehub\\modules\\senta_bilstm "
            "后重跑即可自动重新下载。\n".format(e)
        )
        sys.exit(1)

    while True:
        # 获取用户输入的文本
        user_input = input("请输入要分析情感的文本 (输入 'exit' 退出): ")

        if user_input.lower() == 'exit':
            print("程序已退出。")
            break

        try:
            # 调用情感分析方法
            result = analyzer.analyze_sentiment(user_input)
            # 显示结果
            analyzer.display_result(result)
        except Exception as e:
            print(f"分析失败：{e}")


# 运行主程序
if __name__ == "__main__":
    main()
