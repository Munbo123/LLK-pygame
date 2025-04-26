"""
网络客户端模块，处理WebSocket连接和消息收发
"""
import asyncio
import websockets
import json
import threading
import time
import concurrent.futures
from queue import Queue


class NetworkClient:
    """网络客户端类，处理与服务器的WebSocket通信"""
    
    def __init__(self, server_url="ws://localhost:8765"):
        """
        初始化网络客户端
        
        Args:
            server_url: WebSocket服务器URL
        """
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.user_id = None
        self.user_name = None
        self.match_id = None
        self.opponent_id = None
        self.opponent_name = None
        
        # 游戏状态变量
        self.countdown_active = False  # 倒计时是否激活
        self.countdown_seconds = 0     # 倒计时剩余秒数
        self.game_started = False      # 游戏是否已开始
        
        # 消息队列，用于接收从服务器发来的消息
        self.message_queue = Queue()
        
        # 用于回调函数的事件处理器字典
        self.event_handlers = {
            'connection_response': [],
            'match_success': [],
            'ready_status_update': [],
            'matrix_state': [],
            'disconnect_response': [],
            'countdown_start': [],      # 新增：倒计时开始
            'countdown_update': [],     # 新增：倒计时更新
            'countdown_cancel': [],     # 新增：倒计时取消
            'game_start': [],           # 新增：游戏开始
            'error': []
        }
        
        # 异步事件循环
        self.loop = None
        self.thread = None
        
        # 断开连接的事件和状态
        self.disconnect_event = None  # 将在stop方法中创建
        self.closing = False  # 标记是否正在关闭连接

        
    def start(self):
        """
        启动网络客户端，在新线程中创建异步事件循环
        """
        print(self.thread)
        if self.thread is not None:
            return
        
        def run_event_loop():
            """在新线程中运行异步事件循环"""
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.connect_and_listen())
        
        self.thread = threading.Thread(target=run_event_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """
        停止网络客户端，使用事件机制实现优雅断开
        """
        if self.thread is None:
            print("客户端线程未运行，无需停止")
            return
            
        # 检查是否已连接
        if self.connected and self.loop is not None:
            # 创建断开连接事件
            self.disconnect_event = threading.Event()
            self.closing = True
            
            # 向服务端发送断开连接的消息
            send_message = {
                "type": "disconnect_request",
                "data": {
                    "user_id": self.user_id,
                    "timestamp": int(time.time() * 1000)
                }
            }
            self.send_message(send_message)
            
            # 等待断开连接事件被触发或超时
            if not self.disconnect_event.wait(timeout=5):
                print("等待断开连接响应超时，将强制关闭连接")
                # 如果超时，尝试强制关闭连接
                try:
                    asyncio.run_coroutine_threadsafe(self._close(), self.loop)
                except Exception as e:
                    print(f"强制关闭连接时出错: {e}")
            
            # 重置断开连接事件和状态
            self.disconnect_event = None
            self.closing = False
                
        # 重置客户端状态
        self.connected = False
        self.websocket = None
        self.user_id = None
        self.match_id = None
        self.opponent_id = None
        self.opponent_name = None
        
        # 停止事件循环
        if self.thread is not None and self.thread.is_alive():
            try:
                if self.loop is not None and self.loop.is_running():
                    self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                print(f"停止事件循环时出错: {e}")
        
        # 重置线程和事件循环
        self.thread = None
        self.loop = None
        print("网络客户端已完全停止")
            
    async def _close(self):
        """
        关闭WebSocket连接的异步方法
        """
        try:
            if self.websocket is not None:
                print("正在关闭WebSocket连接...")
                await self.websocket.close()
                print("WebSocket连接已关闭")
        except Exception as e:
            print(f"关闭WebSocket连接时出错: {e}")
        finally:
            # 确保连接状态被重置
            self.websocket = None
            self.connected = False

    async def connect_and_listen(self):
        """
        连接到服务器并监听消息
        """
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"连接到服务器 {self.server_url}")
            
            # 发送连接请求
            await self._send_connection_request()
            
            # 持续监听服务器消息
            while not self.closing:  # 使用closing标志控制循环
                try:
                    # 使用带超时的接收方法，定期检查closing标志
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=0.5)
                    
                    message_data = json.loads(message)
                    print(f"收到消息: {message_data}")
                    message_type = message_data.get("type")
                    
                    # 将消息放入队列
                    self.message_queue.put(message_data)
                    
                    # 处理特定类型的消息
                    if message_type == "connection_response":
                        await self._handle_connection_response(message_data)
                    elif message_type == "match_success":
                        await self._handle_match_success(message_data)
                    elif message_type == "disconnect_response":
                        # 处理断开连接响应
                        print("收到服务器断开连接响应")
                        
                        # 正常关闭websocket连接
                        if self.websocket:
                            await self.websocket.close()
                            
                        # 设置状态和触发事件    
                        self.connected = False
                        if self.closing and self.disconnect_event:
                            self.disconnect_event.set()
                            
                        # 触发事件处理器
                        for handler in self.event_handlers["disconnect_response"]:
                            handler(message_data)
                            
                        break  # 退出监听循环
                    
                    # 处理倒计时相关消息
                    elif message_type == "countdown_start":
                        await self._handle_countdown_start(message_data)
                    elif message_type == "countdown_update":
                        await self._handle_countdown_update(message_data)
                    elif message_type == "countdown_cancel":
                        await self._handle_countdown_cancel(message_data)
                    elif message_type == "game_start":
                        await self._handle_game_start(message_data)
                        
                    elif message_type in self.event_handlers:
                        # 触发对应类型的事件处理器
                        for handler in self.event_handlers[message_type]:
                            handler(message_data)
                    
                except asyncio.TimeoutError:
                    # 超时只用于检查closing标志，不是错误
                    continue
                except json.JSONDecodeError:
                    print(f"无效的JSON消息: {message}")
                except Exception as e:
                    print(f"处理消息时出错: {e}")
                    
        except websockets.exceptions.ConnectionClosedError:
            print("与服务器的连接已关闭")
            self.connected = False
        except Exception as e:
            print(f"连接服务器时出错: {e}")
            self.connected = False
        finally:
            self.connected = False
    
    async def _handle_countdown_start(self, message_data):
        """
        处理倒计时开始消息
        
        Args:
            message_data: 倒计时开始消息数据
        """
        data = message_data.get("data", {})
        duration = data.get("duration", 3)
        
        # 设置倒计时状态
        self.countdown_active = True
        self.countdown_seconds = duration
        
        print(f"倒计时开始，初始值: {duration}秒")
        
        # 触发倒计时开始事件
        for handler in self.event_handlers["countdown_start"]:
            handler(message_data)
    
    async def _handle_countdown_update(self, message_data):
        """
        处理倒计时更新消息
        
        Args:
            message_data: 倒计时更新消息数据
        """
        data = message_data.get("data", {})
        remaining = data.get("remaining_seconds", 0)
        
        # 更新倒计时状态
        self.countdown_seconds = remaining
        
        print(f"倒计时更新: {remaining}秒")
        
        # 触发倒计时更新事件
        for handler in self.event_handlers["countdown_update"]:
            handler(message_data)
    
    async def _handle_countdown_cancel(self, message_data):
        """
        处理倒计时取消消息
        
        Args:
            message_data: 倒计时取消消息数据
        """
        data = message_data.get("data", {})
        reason = data.get("reason", "未知原因")
        player_id = data.get("player_id")
        
        # 重置倒计时状态
        self.countdown_active = False
        self.countdown_seconds = 0
        
        print(f"倒计时取消: {reason}")
        
        # 触发倒计时取消事件
        for handler in self.event_handlers["countdown_cancel"]:
            handler(message_data)
    
    async def _handle_game_start(self, message_data):
        """
        处理游戏开始消息
        
        Args:
            message_data: 游戏开始消息数据
        """
        # 重置倒计时状态
        self.countdown_active = False
        self.countdown_seconds = 0
        
        # 设置游戏状态
        self.game_started = True
        
        print("游戏开始!")
        
        # 触发游戏开始事件
        # 确保使用一个明确的副本遍历处理器列表，避免潜在修改问题
        handlers = self.event_handlers["game_start"].copy()
        for handler in handlers:
            try:
                handler(message_data)
            except Exception as e:
                print(f"调用游戏开始处理器时出错: {e}")
            
    async def _send_connection_request(self):
        """
        发送连接请求到服务器
        """
        connection_request = {
            "type": "connection_request",
            "data": {
                "user_name": self.user_name or "未命名玩家",
                "timestamp": int(time.time() * 1000)
            }
        }

        print(f"发送连接请求: {connection_request}")
        
        await self.websocket.send(json.dumps(connection_request))
        
    async def _handle_connection_response(self, response):
        """
        处理服务器的连接响应
        
        Args:
            response: 连接响应数据
        """
        data = response.get("data", {})
        status = data.get("connection_status")
        
        if status == "connected":
            self.connected = True
            self.user_id = data.get("user_id")
            # 移除这里的打印，避免与NetworkMode中的打印重复
            # print(f"连接成功，用户ID: {self.user_id}")
            
            # 触发连接响应事件
            for handler in self.event_handlers["connection_response"]:
                handler(response)
        else:
            print(f"连接失败: {data.get('message')}")
            self.connected = False
            
    async def _handle_match_success(self, message):
        """
        处理匹配成功消息
        
        Args:
            message: 匹配成功消息数据
        """
        data = message.get("data", {})
        self.match_id = data.get("match_id")
        
        player1 = data.get("player1", {})
        player2 = data.get("player2", {})
        
        # 确定对手信息
        if player1.get("id") == self.user_id:
            self.opponent_id = player2.get("id")
            self.opponent_name = player2.get("name")
        else:
            self.opponent_id = player1.get("id")
            self.opponent_name = player1.get("name")
            
        print(f"匹配成功，对局ID: {self.match_id}，对手: {self.opponent_name}")
        
        # 触发匹配成功事件
        for handler in self.event_handlers["match_success"]:
            handler(message)
    
    def register_handler(self, event_type, handler):
        """
        注册事件处理器
        
        Args:
            event_type: 事件类型，如'connection_response'，'match_success'等
            handler: 回调函数，接受一个参数(消息数据)
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            
    def unregister_handler(self, event_type, handler):
        """
        注销事件处理器
        
        Args:
            event_type: 事件类型
            handler: 要注销的处理器函数
        """
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            
    def send_message(self, message):
        """
        向服务器发送消息
        
        Args:
            message: 要发送的消息(字典或JSON字符串)
        """
        if not self.connected or self.websocket is None:
            print("未连接到服务器，无法发送消息")
            return False

        print(f"向服务端发送消息: {message}")

        # 将消息转换为JSON字符串
        if isinstance(message, dict):
            message = json.dumps(message)
            
        # 在事件循环中发送消息
        asyncio.run_coroutine_threadsafe(
            self._async_send_message(message), 
            self.loop
        )
        
        return True
        
    async def _async_send_message(self, message):
        """
        异步发送消息
        
        Args:
            message: 要发送的消息(JSON字符串)
        """
        try:
            await self.websocket.send(message)
        except Exception as e:
            print(f"发送消息时出错: {e}")
            
    def set_user_name(self, name):
        """
        设置用户名
        
        Args:
            name: 用户名
        """
        self.user_name = name
        
    def is_connected(self):
        """
        检查是否已连接到服务器
        
        Returns:
            bool: 是否已连接
        """
        return self.connected
        
    def send_ready_message(self, ready_status):
        """
        发送准备状态消息
        
        Args:
            ready_status: 准备状态(True/False)
            
        Returns:
            bool: 是否成功发送
        """
        if not self.connected or not self.match_id:
            return False
            
        ready_message = {
            "type": "ready_message",
            "data": {
                "ready_status": ready_status,
                "match_id": self.match_id,
                "user": {
                    "id": self.user_id,
                    "name": self.user_name
                },
                "timestamp": int(time.time() * 1000)
            }
        }
        
        return self.send_message(ready_message)
        
    def send_click_message(self, row, col):
        """
        发送点击消息
        
        Args:
            row: 点击的行
            col: 点击的列
            
        Returns:
            bool: 是否成功发送
        """
        if not self.connected or not self.match_id:
            return False
            
        click_message = {
            "type": "click_message",
            "data": {
                "position": {
                    "row": row,
                    "col": col
                },
                "match_id": self.match_id,
                "user": {
                    "id": self.user_id,
                    "name": self.user_name
                },
                "timestamp": int(time.time() * 1000)
            }
        }
        
        return self.send_message(click_message)