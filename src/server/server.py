"""
连连看游戏服务器主模块，整合所有服务器组件
"""
import asyncio
import websockets
import pygame
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.image_processor import process_fruit_sheet
from src.server.game_manager import GameManager
from src.server.client_handler import ClientHandler

game_background_path = r"./assets/fruit_bg.bmp"
sheet_path = r"./assets/fruit_element.bmp"
mask_path = r"./assets/fruit_mask.bmp"


class GameServer:
    """游戏服务器类，启动和管理WebSocket服务器"""
    
    def __init__(self, host="localhost", port=8765):
        """
        初始化游戏服务器
        
        Args:
            host: 服务器主机地址
            port: 服务器端口
        """
        self.host = host
        self.port = port
        self.elements = None
        self.game_manager = None
        self.client_handler = None
        
    async def initialize(self):
        """初始化服务器组件"""
        # 初始化pygame以加载图像
        pygame.init()
        
        # 加载连连看游戏元素
        self.elements = process_fruit_sheet(sheet_path=sheet_path, mask_path=mask_path)
        
        # 初始化游戏管理器
        self.game_manager = GameManager(self.elements)
        
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
    # 使用硬编码的端口和主机地址
    host = 'localhost'
    port = 8765
    
    print(f"正在启动服务器于 {host}:{port}...")
    server = GameServer(host, port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("服务器已关闭")
    except Exception as e:
        print(f"服务器发生错误: {e}")
    finally:
        pygame.quit()
        print("服务器资源已清理")


if __name__ == "__main__":
    main()