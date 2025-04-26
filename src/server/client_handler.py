"""
客户端处理器模块，负责处理每个连接的客户端
"""
import asyncio
import json
import uuid
import time
import websockets

from src.server.game_manager import GameManager


class ClientHandler:
    """客户端处理器类，负责处理客户端连接和消息"""
    
    def __init__(self, game_manager:GameManager):
        """
        初始化客户端处理器
        
        Args:
            game_manager: 游戏管理器实例
        """
        self.game_manager = game_manager
        self.clients = {}  # 存储客户端连接，键为客户端ID
        
    async def handle_client(self, websocket):
        """
        处理客户端连接
        
        Args:
            websocket: WebSocket连接
        """
        client_id = str(uuid.uuid4())
        print(f"新的客户端连接: {client_id}")
        
        try:
            # 等待客户端发送连接请求
            connection_data = await websocket.recv()
            connection_request = json.loads(connection_data)
            
            # 验证连接请求类型
            if connection_request.get("type") != "connection_request":
                send_message = {
                    "type": "error",
                    "data": {
                        "message": "无效的连接请求",
                        "timestamp": int(time.time() * 1000)
                    }
                }
                print(f'发送了{send_message}')
                # 发送错误消息给客户端
                await websocket.send(json.dumps(send_message))
                return
            
            # 从请求中获取用户名
            user_name = connection_request.get("data", {}).get("user_name", f"玩家_{client_id[:8]}")
            
            # 保存客户端连接
            self.clients[client_id] = {
                "websocket": websocket,
                "name": user_name,
                "connected_at": time.time()
            }
            
            # 发送连接响应
            send_message = {
                "type": "connection_response",
                "data": {
                    "connection_status": "connected",
                    "user_id": client_id,
                    "message": "成功连接到服务器",
                    "timestamp": int(time.time() * 1000)
                }
            }
            print(f'发送了{send_message}')
            await websocket.send(json.dumps(send_message))
            
            # 添加玩家到游戏管理器，尝试匹配
            matched, match_data = self.game_manager.add_player(client_id, user_name)
            
            # 如果找到了匹配
            if matched:
                # 获取匹配到的玩家信息
                player1 = match_data["data"]["player1"]
                player2 = match_data["data"]["player2"]
                
                # 向两个玩家发送匹配成功消息
                await self.send_to_client(player1["id"], json.dumps(match_data))
                await self.send_to_client(player2["id"], json.dumps(match_data))
            
            # 开始处理客户端消息
            await self.process_messages(websocket, client_id)
            print(f"客户端消息处理完成: {client_id}")
            
        except websockets.exceptions.ConnectionClosedOK:
            print(f"客户端正常断开连接: {client_id}")
        except websockets.exceptions.ConnectionClosedError:
            print(f"客户端异常断开连接: {client_id}")
        except Exception as e:
            print(f"处理客户端时出错: {e}")
        finally:
            # 客户端断开连接，清理资源
            self.game_manager.remove_player(client_id)
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def process_messages(self, websocket, client_id):
        """
        处理来自客户端的消息
        
        Args:
            websocket: WebSocket连接
            client_id: 客户端ID
        """
        async for message in websocket:
            try:
                # 解析消息
                message_data = json.loads(message)
                print(f"收到来自 {client_id} 的消息: {message_data}")
                message_type = message_data.get("type")
                
                if message_type == "ready_message":
                    # 处理准备消息
                    await self.handle_ready_message(client_id, message_data)
                elif message_type == "click_message":
                    # 处理点击消息
                    await self.handle_click_message(client_id, message_data)
                elif message_type == "disconnect_request":
                    # 处理断开连接请求
                    print(f"客户端请求断开连接: {client_id}")
                    # 发送断开断开连接响应
                    send_message = {
                        "type": "disconnect_response",
                        "data": {
                            "user_id": client_id,
                            "status": "disconnected",
                            "message": "连接已成功断开",
                            "timestamp": int(time.time() * 1000)
                        }
                    }
                    await self.send_to_client(client_id, send_message)
                    break
                else:
                    send_message = {
                        "type": "error",
                        "data": {
                            "message": f"不支持的消息类型: {message_type}",
                            "timestamp": int(time.time() * 1000)
                        }
                    }
                    print(f'发送了{send_message}')
                    # 不支持的消息类型
                    await websocket.send(json.dumps(send_message))
            except json.JSONDecodeError:
                # 无效的JSON格式
                send_message = {
                    "type": "error",
                    "data": {
                        "message": "无效的消息格式",
                        "timestamp": int(time.time() * 1000)
                    }
                }
                print(f'发送了{send_message}')
                await websocket.send(json.dumps(send_message))
            except Exception as e:
                print(f"处理消息时出错: {e}")
    
    async def handle_ready_message(self, client_id, message_data):
        """
        处理准备消息
        
        Args:
            client_id: 客户端ID
            message_data: 准备消息数据
        """
        # 从消息中获取数据
        data = message_data.get("data", {})
        match_id = data.get("match_id")
        ready_status = data.get("ready_status", False)
        
        if not match_id:
            # 没有指定对局ID
            await self.send_error_to_client(client_id, "未指定对局ID")
            return
        
        # 更新准备状态
        success, status_data = self.game_manager.update_ready_status(
            client_id, match_id, ready_status
        )
        
        if success:
            # 获取匹配对象
            match = self.game_manager.matches.get(match_id)
            if match:
                # 向双方发送准备状态更新
                await self.send_to_client(match.player1["id"], status_data)
                await self.send_to_client(match.player2["id"], status_data)
        else:
            # 更新失败
            await self.send_error_to_client(client_id, status_data.get("error", "更新准备状态失败"))
    
    async def handle_click_message(self, client_id, message_data):
        """
        处理点击消息
        
        Args:
            client_id: 客户端ID
            message_data: 点击消息数据
        """
        # 从消息中获取数据
        data = message_data.get("data", {})
        match_id = data.get("match_id")
        position = data.get("position", {})
        row = position.get("row")
        col = position.get("col")
        
        if not match_id:
            # 没有指定对局ID
            await self.send_error_to_client(client_id, "未指定对局ID")
            return
        
        if row is None or col is None:
            # 没有指定有效的位置
            await self.send_error_to_client(client_id, "未指定有效的位置")
            return
        
        # 处理点击操作
        success, result = self.game_manager.handle_click(
            client_id, match_id, row, col
        )
        
        if success:
            # 获取匹配对象
            match = self.game_manager.matches.get(match_id)
            if match:
                # 向双方发送更新后的矩阵状态
                await self.send_to_client(match.player1["id"], result)
                await self.send_to_client(match.player2["id"], result)
        else:
            # 点击处理失败
            error_msg = result.get("error", "处理点击操作失败")
            await self.send_error_to_client(client_id, error_msg)
    
    async def send_to_client(self, client_id, message):
        """
        向指定客户端发送消息
        
        Args:
            client_id: 客户端ID
            message: 要发送的消息（字符串或字典）
        """
        # 检查客户端是否存在
        client = self.clients.get(client_id)
        if not client:
            print(f"尝试向不存在的客户端发送消息: {client_id}")
            return
        
        try:
            print(f"向客户端 {client_id} 发送消息: {message}")
            # 如果消息是字典，转换为JSON字符串
            if isinstance(message, dict):
                message = json.dumps(message)
                
            await client["websocket"].send(message)
        except Exception as e:
            print(f"向客户端发送消息失败: {e}")
    
    async def send_error_to_client(self, client_id, error_message):
        """
        向客户端发送错误消息
        
        Args:
            client_id: 客户端ID
            error_message: 错误消息
        """
        error_data = {
            "type": "error",
            "data": {
                "message": error_message,
                "timestamp": int(time.time() * 1000)
            }
        }

        print(f'发送了{error_data}')

        await self.send_to_client(client_id, error_data)