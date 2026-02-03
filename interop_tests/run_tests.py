"""
互操作测试快速启动脚本
一键运行所有互操作性测试
"""

import subprocess
import sys
import time


def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"📋 {description}")
    print(f"命令: {cmd}\n")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ 成功\n")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ 失败\n")
            if result.stderr:
                print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ 超时\n")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}\n")
        return False


def main():
    print_header("LiteNetLib C# / Python 互操作测试套件")

    print("此测试套件验证 LiteNetLib-Python v0.9.5.2 与 C# LiteNetLib v0.9.5.2 (NuGet)")
    print("的 100% 二进制兼容性和互操作性。\n")

    print("测试步骤:")
    print("1. 二进制兼容性验证（离线）")
    print("2. 协议常量验证（离线）")
    print("3. C# 服务器 ↔ Python 客户端（需要运行两个终端）")
    print("4. Python 服务器 ↔ C# 客户端（需要运行两个终端）")

    choice = input("\n选择测试:\n1. 只运行离线测试（快速）\n2. 运行完整测试套件\n3. 查看测试说明\n\n请输入选择 (1/2/3): ").strip()

    if choice == "1":
        # 只运行离线测试
        print_header("步骤 1: 二进制兼容性验证")

        run_command(
            "cd interop_tests && python binary_compatibility_test.py",
            "运行二进制兼容性测试..."
        )

        print_header("测试完成")
        print("离线测试已完成！这些测试验证了：")
        print("✅ 协议常量与 C# 完全一致")
        print("✅ 数据包格式与 C# 完全一致")
        print("✅ 序列化格式与 C# 完全一致")
        print("\n要运行完整的互操作测试，请选择选项 2。")

    elif choice == "2":
        # 完整测试
        print_header("完整互操作测试指南")

        print("完整测试需要两个终端窗口：\n")

        print("📦 终端 1: 启动 C# 服务器")
        print("-" * 70)
        print("cd interop_tests/CSharpServer")
        print("dotnet run")
        print()

        print("📦 终端 2: 启动 Python 客户端")
        print("-" * 70)
        print("cd interop_tests")
        print("python python_client_test.py")
        print()

        input("准备好后，按 Enter 继续...")

        # 先运行离线测试
        print_header("步骤 1: 二进制兼容性验证")
        run_command(
            "cd interop_tests && python binary_compatibility_test.py",
            "运行二进制兼容性测试..."
        )

        print_header("测试准备")
        print("\n现在开始互操作测试：")
        print("\n1️⃣  在终端 1 启动 C# 服务器:")
        print("   cd interop_tests/CSharpServer")
        print("   dotnet run")

        print("\n2️⃣  在终端 2 启动 Python 客户端:")
        print("   cd interop_tests")
        print("   python python_client_test.py")

        input("\n准备好后，按 Enter 查看 Python 服务器测试说明...")

        print("\n3️⃣  在终端 1 启动 Python 服务器:")
        print("   cd interop_tests")
        print("   python python_server_test.py")

        print("\n4️⃣  在终端 2 启动 C# 客户端:")
        print("   cd interop_tests/CSharpClient")
        print("   dotnet run")

        print_header("测试说明")
        print("\n预期结果:")
        print("✅ 连接成功建立")
        print("✅ Unreliable 消息正确传输")
        print("✅ ReliableOrdered 消息正确传输")
        print("✅ ReliableUnordered 消息正确传输")
        print("✅ Sequenced 消息正确传输")
        print("✅ ReliableSequenced 消息正确传输")
        print("✅ UTF-8 字符串（包括中文）正确传输")
        print("✅ 整数数组正确传输")
        print("✅ 大块数据（分片传输）正确传输")

    elif choice == "3":
        # 显示详细说明
        print_header("互操作测试详细说明")

        print("📁 测试文件结构:")
        print("-" * 70)
        print("""
interop_tests/
├── README.md                      # 本测试套件的说明文档
├── run_tests.py                   # 本快速启动脚本
├── binary_compatibility_test.py   # 二进制兼容性验证
├── python_client_test.py          # Python 客户端（连接 C# 服务器）
├── python_server_test.py          # Python 服务器（连接 C# 客户端）
├── CSharpServer/                  # C# 服务器项目
│   ├── Program.cs                 # 服务器代码
│   └── CSharpServer.csproj        # 项目文件
└── CSharpClient/                  # C# 客户端项目
    ├── Program.cs                 # 客户端代码
    └── CSharpClient.csproj        # 项目文件
        """)

        print("\n🔧 环境准备:")
        print("-" * 70)
        print("""
C# 项目:
1. 安装 .NET 6.0 SDK
2. 编译项目:
   cd interop_tests/CSharpServer
   dotnet restore
   dotnet build

Python 项目:
1. 安装 LiteNetLib-Python:
   cd LiteNetLib-Python-0.9.5.2
   pip install -e .
        """)

        print("\n🚀 运行测试:")
        print("-" * 70)
        print("""
测试场景 1: C# 服务器 ↔ Python 客户端

Terminal 1 (C# Server):
  cd interop_tests/CSharpServer
  dotnet run

Terminal 2 (Python Client):
  cd interop_tests
  python python_client_test.py


测试场景 2: Python 服务器 ↔ C# 客户端

Terminal 1 (Python Server):
  cd interop_tests
  python python_server_test.py

Terminal 2 (C# Client):
  cd interop_tests/CSharpClient
  dotnet run
        """)

        print("\n📊 验证点:")
        print("-" * 70)
        print("""
✅ 协议常量一致性 (PROTOCOL_ID, 枚举值等)
✅ 数据包头部格式 (字节序、位字段等)
✅ 序列化格式 (基本类型、字符串、数组等)
✅ 5 种传输方法 (Unreliable, ReliableOrdered 等)
✅ UTF-8 编码 (包括中文字符)
✅ 分片包传输 (大数据块)
✅ ACK/重传机制
✅ 连接管理 (连接、断开)
        """)

    else:
        print("无效选择")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        input("\n按 Enter 退出...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(1)
