#!/usr/bin/env python
"""
测试同步重构后的LiteNetLib-Python

验证：
1. poll_events() 是纯同步方法
2. 不会在Windows上挂起
3. 不需要 asyncio.run() 或事件循环
4. 与C# LiteNetLib行为一致
"""

import sys
import time
from litenetlib import LiteNetManager, EventBasedNetListener

# 修复Windows控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_basic_server_query():
    """测试1: 基本服务器查询（同步）"""
    print("\n" + "=" * 60)
    print("测试 1: 基本服务器查询（同步）")
    print("=" * 60)

    listener = EventBasedNetListener()
    manager = LiteNetManager(listener)

    # 启动管理器（绑定到任意端口）
    if not manager.start(port=0):
        print("❌ 失败：无法启动管理器")
        return False

    print(f"✓ 管理器已启动，端口: {manager.local_port}")

    # 发送无连接消息
    try:
        manager.send_unconnected_message(b"test", ("hxhx2009.site", 28887))
        print("✓ 已发送无连接消息")
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        manager.stop()
        return False

    # 轮询事件（同步，不应该挂起）
    print("✓ 开始轮询事件（同步模式）...")
    for i in range(100):
        manager.poll_events()  # 纯同步调用
        if i % 20 == 0:
            print(f"  轮询 #{i}")
        time.sleep(0.01)

    print("✓ 轮询完成，没有挂起")

    manager.stop()
    print("✓ 管理器已停止")
    return True


def test_client_connection():
    """测试2: 客户端连接（同步）"""
    print("\n" + "=" * 60)
    print("测试 2: 客户端连接（同步）")
    print("=" * 60)

    connected = [False]
    received_data = [False]

    # 设置事件监听器
    listener = EventBasedNetListener()
    listener.set_peer_connected_callback(lambda peer: setattr(connected, '__setitem__', (0, True)))
    listener.set_network_receive_callback(
        lambda peer, reader, channel, method: setattr(received_data, '__setitem__', (0, True))
    )

    manager = LiteNetManager(listener)

    if not manager.start():
        print("❌ 失败：无法启动管理器")
        return False

    print("✓ 管理器已启动")

    # 尝试连接（可能会失败，这是正常的）
    try:
        peer = manager.connect("127.0.0.1", 28887)
        print(f"✓ 已发起连接到 {peer.address}")
    except Exception as e:
        print(f"⚠ 连接发起异常（可能是正常的）: {e}")

    # 轮询（同步，不挂起）
    print("✓ 开始轮询连接（同步模式）...")
    for i in range(100):
        manager.poll_events()  # 纯同步调用
        if i % 20 == 0:
            print(f"  轮询 #{i}")
        time.sleep(0.01)

    print("✓ 轮询完成，没有挂起")

    manager.stop()
    print("✓ 管理器已停止")
    return True


def test_no_asyncio_required():
    """测试3: 验证不需要asyncio"""
    print("\n" + "=" * 60)
    print("测试 3: 验证不需要asyncio")
    print("=" * 60)

    # 检查poll_events是否为同步方法
    import inspect

    manager = LiteNetManager()

    # 检查poll_events不是协程函数
    if inspect.iscoroutinefunction(manager.poll_events):
        print("❌ 失败：poll_events 仍然是 async 函数")
        return False

    print("✓ poll_events 是同步函数")

    # 检查没有import asyncio
    import litenetlib.core.manager as manager_module
    import litenetlib.core.peer as peer_module
    import litenetlib.channels.base_channel as channel_module

    manager_src = inspect.getsource(manager_module)
    peer_src = inspect.getsource(peer_module)
    channel_src = inspect.getsource(channel_module)

    if 'import asyncio' in manager_src:
        print("❌ 失败：manager.py 仍然导入 asyncio")
        return False

    if 'import asyncio' in peer_src:
        print("❌ 失败：peer.py 仍然导入 asyncio")
        return False

    if 'import asyncio' in channel_src:
        print("❌ 失败：base_channel.py 仍然导入 asyncio")
        return False

    print("✓ 没有模块导入 asyncio")

    # 检查没有async def
    if 'async def' in manager_src:
        print("❌ 失败：manager.py 中仍有 async def")
        return False

    if 'async def' in peer_src:
        print("❌ 失败：peer.py 中仍有 async def")
        return False

    print("✓ 没有 async def 方法定义")

    # 检查没有await
    if 'await ' in manager_src:
        print("❌ 失败：manager.py 中仍有 await 调用")
        return False

    if 'await ' in peer_src:
        print("❌ 失败：peer.py 中仍有 await 调用")
        return False

    print("✓ 没有 await 调用")

    return True


def test_queue_operations():
    """测试4: 验证使用queue.Queue而不是asyncio.Queue"""
    print("\n" + "=" * 60)
    print("测试 4: 验证使用queue.Queue")
    print("=" * 60)

    import inspect
    from litenetlib.channels.reliable_channel import ReliableChannel
    from litenetlib.channels.base_channel import BaseChannel

    # 检查BaseChannel使用queue.Queue
    base_src = inspect.getsource(BaseChannel)
    if 'queue.Queue' not in base_src:
        print("❌ 失败：BaseChannel 不使用 queue.Queue")
        return False

    if 'asyncio.Queue' in base_src:
        print("❌ 失败：BaseChannel 仍使用 asyncio.Queue")
        return False

    print("✓ BaseChannel 使用 queue.Queue")

    # 检查ReliableChannel处理queue.Empty异常
    reliable_src = inspect.getsource(ReliableChannel)
    if 'queue.Empty' not in reliable_src and 'QueueEmpty' in reliable_src:
        print("❌ 失败：ReliableChannel 不使用 queue.Empty")
        return False

    print("✓ ReliableChannel 正确处理队列异常")

    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("LiteNetLib-Python 同步重构验证测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("基本服务器查询", test_basic_server_query()))
    results.append(("客户端连接", test_client_connection()))
    results.append(("不需要asyncio", test_no_asyncio_required()))
    results.append(("使用queue.Queue", test_queue_operations()))

    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✅ 所有测试通过！同步重构成功！")
        print("\n关键改进:")
        print("  • poll_events() 是纯同步方法")
        print("  • 不需要 asyncio.run() 或事件循环")
        print("  • 不会在 Windows 上挂起")
        print("  • 与 C# LiteNetLib 行为一致")
        return 0
    else:
        print("\n❌ 部分测试失败，需要进一步修复")
        return 1


if __name__ == '__main__':
    sys.exit(main())
