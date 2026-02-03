# LiteNetLib C# / Python 互操作测试

## 测试目的

证明 LiteNetLib-Python v0.9.5.2 与 C# LiteNetLib v0.9.5.2（NuGet）100% 二进制兼容，可以无缝互通。

## 测试环境准备

### 1. C# 项目设置

```bash
# 创建 C# 测试项目
dotnet new console -n CSharpServer
cd CSharpServer
dotnet add package LiteNetLib --version 0.9.5.2
```

### 2. Python 项目设置

```bash
# 已在当前目录
cd LiteNetLib-Python-0.9.5.2
pip install -e .
```

## 测试场景

### 场景 1: C# 服务器 ↔ Python 客户端
- C# 服务器监听，Python 客户端连接
- 测试所有 5 种传输方法
- 验证数据序列化/反序列化

### 场景 2: Python 服务器 ↔ C# 客户端
- Python 服务器监听，C# 客户端连接
- 测试所有 5 种传输方法
- 验证数据序列化/反序列化

### 场景 3: 二进制兼容性验证
- 验证协议常量
- 验证数据包格式
- 验证序列化格式

### 场景 4: 高级功能测试
- 分片包传输
- MERGED 包处理
- ACK/重传机制
- 连接/断开流程

## 运行测试

### 步骤 1: 启动 C# 服务器

```bash
cd interop_tests/CSharpServer
dotnet run
```

### 步骤 2: 启动 Python 客户端

```bash
cd interop_tests
python python_client_test.py
```

### 步骤 3: 启动 Python 服务器

```bash
cd interop_tests
python python_server_test.py
```

### 步骤 4: 启动 C# 客户端

```bash
cd interop_tests/CSharpClient
dotnet run
```

## 预期结果

所有测试应该通过，输出：
```
✅ Connection successful
✅ Unreliable message received
✅ Reliable ordered message received
✅ Reliable unordered message received
✅ Sequenced message received
✅ Reliable sequenced message received
✅ String serialization correct
✅ Integer serialization correct
✅ Large data transfer successful
✅ Fragmentation working correctly
```

## 测试文件说明

- `CSharpServer/` - C# 服务器实现
- `CSharpClient/` - C# 客户端实现
- `python_server_test.py` - Python 服务器测试
- `python_client_test.py` - Python 客户端测试
- `binary_compatibility_test.py` - 二进制兼容性验证
- `protocol_verification.py` - 协议常量验证
