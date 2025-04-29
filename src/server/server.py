"""
连连看游戏服务器主模块，整合所有服务器组件
"""
import asyncio
import websockets
import sys
import os
import argparse  # 导入argparse模块用于命令行参数解析

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.server.game_manager import GameManager
from src.server.client_handler import ClientHandler


class GameServer:
    """游戏服务器类，启动和管理WebSocket服务器"""
    
    def __init__(self, host="0.0.0.0", port=8765,element_len=10):
        """
        初始化游戏服务器
        
        Args:
            host: 服务器主机地址
            port: 服务器端口
        """
        self.host = host
        self.port = port
        self.game_manager = None
        self.client_handler = None
        self.element_len = element_len # 元素数量，客户端必须有大于等于这个数量的元素才能正常运行
        
    async def initialize(self):
        """初始化服务器组件"""
    
        # 初始化游戏管理器
        self.game_manager = GameManager(self.element_len)
        
        # 初始化客户端处理器
        self.client_handler = ClientHandler(self.game_manager)
        
        print(f"服务器初始化完成，准备启动于 {self.host}:{self.port}")
        
    async def start(self):
        """启动WebSocket服务器"""
        await self.initialize()
        
        # 修复：移除path参数，适应新版本websockets API
        handler = self.client_handler.handle_client
        
        async with websockets.serve(
            handler,
            self.host,
            self.port
        ):
            print(f"连连看游戏服务器已启动于 ws://{self.host}:{self.port}")
            # 保持服务器运行
            await asyncio.Future()  # 永不完成的Future，使服务器持续运行


def main():
    """主函数，启动服务器"""
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description='连连看游戏服务器')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8765, help='服务器端口号 (默认: 8765)')
    parser.add_argument('--element_len', type=int, default=10, help='元素数量 (默认: 10)')
    
    # 解析命令行参数
    args = parser.parse_args()
    host = args.host
    port = args.port
    element_len = args.element_len
    
    print(f"正在启动服务器于 {host}:{port}...")
    server = GameServer(host, port,element_len)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("服务器已关闭")
    except Exception as e:
        print(f"服务器发生错误: {e}")
    finally:
        print("服务器资源已清理")


if __name__ == "__main__":
    main()