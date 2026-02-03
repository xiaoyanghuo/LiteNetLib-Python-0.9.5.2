"""
TestPyPI 发布辅助脚本
提供交互式界面来发布到 TestPyPI
"""

import os
import sys
import subprocess


def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")


def check_package():
    """检查包"""
    print("📋 检查包...")
    result = subprocess.run(
        [sys.executable, "-m", "twine", "check", "dist/*"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("❌ 包检查失败:")
        print(result.stderr)
        return False
    print("✅ 包检查通过\n")
    return True


def upload_to_testpypi():
    """发布到 TestPyPI"""
    print("🚀 发布到 TestPyPI...")

    result = subprocess.run(
        [sys.executable, "-m", "twine", "upload", "--repository", "testpypi", "dist/*"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print("❌ 发布失败\n")
        return False

    print("\n✅ 发布成功！")
    print("📦 TestPyPI URL: https://test.pypi.org/project/litenetlib-python/\n")
    return True


def install_from_testpypi():
    """从 TestPyPI 安装测试"""
    print("📥 从 TestPyPI 安装测试...")

    # 先卸载旧版本
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "litenetlib-python", "-y"],
        capture_output=True
    )

    # 从 TestPyPI 安装
    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            "--index-url", "https://test.pypi.org/simple/",
            "litenetlib-python"
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("❌ 安装失败:")
        print(result.stderr)
        return False

    # 验证安装
    print("\n🔍 验证安装...")
    result = subprocess.run(
        [
            sys.executable, "-c",
            "from litenetlib.core.constants import NetConstants; "
            "print('✅ 安装成功!'); "
            "print('PROTOCOL_ID:', NetConstants.PROTOCOL_ID); "
            "print('ACK:', NetConstants.ACK); "
            "print('MERGED:', NetConstants.MERGED)"
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("❌ 验证失败:")
        print(result.stderr)
        return False

    print("\n✅ TestPyPI 安装验证通过\n")
    return True


def show_package_info():
    """显示包信息"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "litenetlib-python"],
        capture_output=True,
        text=True
    )
    print(result.stdout)


def main():
    print_header("TestPyPI 发布工具")

    print("LiteNetLib-Python v0.9.5.2 TestPyPI 发布\n")

    print("请确保已完成以下步骤:")
    print("1. 注册 TestPyPI 账号: https://test.pypi.org/account/register/")
    print("2. 创建 API Token: https://test.pypi.org/manage/account/token/")
    print("3. 配置认证（环境变量或 .pypirc）")

    print("\n配置方法:")
    print("""
# Windows Command Prompt
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-xxxxxxxxxxxxx

# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-xxxxxxxxxxxxx"

# Linux/Mac
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-xxxxxxxxxxxxx"
    """)

    input("\n按 Enter 继续...")

    # 检查包
    print_header("步骤 1: 检查包")
    if not check_package():
        input("按 Enter 退出...")
        return 1

    # 发布
    print_header("步骤 2: 发布到 TestPyPI")
    if not upload_to_testpypi():
        input("按 Enter 退出...")
        return 1

    # 安装测试
    print_header("步骤 3: 从 TestPyPI 安装测试")
    if not install_from_testpypi():
        input("按 Enter 退出...")
        return 1

    # 显示信息
    print_header("安装的包信息")
    show_package_info()

    print_header("完成")
    print("✅ TestPyPI 发布和安装测试完成！\n")

    print("后续步骤:")
    print("1. 访问 TestPyPI 查看包: https://test.pypi.org/project/litenetlib-python/")
    print("2. 如果一切正常，可以发布到正式 PyPI")
    print("3. 清理: pip uninstall litenetlib-python -y")

    input("\n按 Enter 退出...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 退出...")
        sys.exit(1)
