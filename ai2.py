import paddle
import paddle.nn as nn
import paddle.vision.transforms as T
import paddle.vision.datasets as D

# 设置设备（GPU或CPU）
device = paddle.set_device('gpu' if paddle.is_compiled_with_cuda() else 'cpu')

# 加载MNIST数据集
transform = T.Compose([T.Transpose(), T.Normalize([127.5], [127.5])])
train_dataset = D.MNIST(mode='train', transform=transform)
test_dataset = D.MNIST(mode='test', transform=transform)

# 创建数据加载器
train_loader = paddle.io.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = paddle.io.DataLoader(test_dataset, batch_size=64, shuffle=False)


# 定义简单的神经网络模型
class SimpleNN(nn.Layer):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(in_features=28 * 28, out_features=128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(in_features=128, out_features=10)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


# 实例化模型并设置到设备
model = SimpleNN()
model = model.to(device)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = paddle.optimizer.Adam(parameters=model.parameters(), learning_rate=0.001)


# 训练模型
def train(model, train_loader, criterion, optimizer, device, epochs=5):
    model.train()
    for epoch in range(epochs):
        for batch_id, (data, label) in enumerate(train_loader):
            data, label = data.to(device), label.to(device)

            # 前向传播
            logits = model(data)
            loss = criterion(logits, label)

            # 反向传播和优化
            loss.backward()
            optimizer.step()
            optimizer.clear_grad()

            if batch_id % 100 == 0:
                print(f"Epoch [{epoch + 1}/{epochs}], Step [{batch_id}], Loss: {loss.numpy()}")  # 直接打印 loss 数值


# 测试模型
def evaluate(model, test_loader, criterion, device):
    model.eval()
    correct = 0
    total = 0
    with paddle.no_grad():
        for data, label in test_loader:
            data, label = data.to(device), label.to(device)
            logits = model(data)
            pred = paddle.argmax(logits, axis=1)
            correct += (pred == label).sum().item()  # 直接累加 item() 结果
            total += label.shape[0]
    accuracy = correct / total
    print(f"Accuracy: {accuracy:.4f}")  # 精度打印保留4位小数


# 训练和测试模型
train(model, train_loader, criterion, optimizer, device, epochs=5)
evaluate(model, test_loader, criterion, device)
