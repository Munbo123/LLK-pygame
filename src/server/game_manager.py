"""
游戏管理器模块，负责管理玩家匹配和对局管理
"""
import uuid
import time
import asyncio
import json  # 添加 json 模块导入
from src.server.match import Match


class GameManager:
    """游戏管理器类，负责管理玩家队列和对局"""
    
    def __init__(self, elements):
        """
        初始化游戏管理器
        
        Args:
            elements: 用于初始化矩阵的元素列表
        """
        self.waiting_queue = []  # 等待匹配的玩家队列
        self.matches = {}  # 进行中的对局，键为对局ID
        self.player_to_match = {}  # 玩家ID到对局ID的映射
        self.elements = elements  # 用于初始化矩阵的元素
        self.client_handler = None  # 客户端处理器引用，用于发送消息
    
    def set_client_handler(self, client_handler):
        """设置客户端处理器引用
        
        Args:
            client_handler: ClientHandler实例
        """
        self.client_handler = client_handler
    
    def add_player(self, player_id, player_name):
        """
        添加玩家到等待队列
        
        Args:
            player_id: 玩家ID
            player_name: 玩家名称
            
        Returns:
            tuple: (是否成功匹配, 匹配结果信息)
        """
        # 将玩家添加到等待队列
        self.waiting_queue.append({"id": player_id, "name": player_name})
        
        # 检查是否有足够的玩家可以匹配
        if len(self.waiting_queue) >= 2:
            # 取出两个玩家进行匹配
            player1 = self.waiting_queue.pop(0)
            player2 = self.waiting_queue.pop(0)
            
            # 创建新的对局
            match = Match(
                player1["id"], player1["name"], 
                player2["id"], player2["name"],
                self.elements
            )
            
            # 保存对局信息
            self.matches[match.match_id] = match
            
            # 更新玩家到对局的映射
            self.player_to_match[player1["id"]] = match.match_id
            self.player_to_match[player2["id"]] = match.match_id
            
            # 生成匹配成功的响应
            match_success = {
                "type": "match_success",
                "data": {
                    "player1": {
                        "id": player1["id"],
                        "name": player1["name"]
                    },
                    "player2": {
                        "id": player2["id"],
                        "name": player2["name"]
                    },
                    "match_id": match.match_id,
                    "timestamp": int(time.time() * 1000)
                }
            }
            
            return True, match_success
        
        return False, None
    
    def remove_player(self, player_id):
        """
        从等待队列中移除玩家
        
        Args:
            player_id: 要移除的玩家ID
            
        Returns:
            bool: 是否成功移除
        """
        # 从等待队列中移除
        for i, player in enumerate(self.waiting_queue):
            if player["id"] == player_id:
                self.waiting_queue.pop(i)
                return True
                
        # 如果玩家在对局中，需要处理对局结束逻辑
        match_id = self.player_to_match.get(player_id)
        if match_id:
            match = self.matches.get(match_id)
            if match:
                # 获取对手ID
                opponent = match.get_opponent_by_id(player_id)
                if opponent:
                    # 清理对局相关数据
                    self.player_to_match.pop(player_id, None)
                    self.player_to_match.pop(opponent["id"], None)
                    self.matches.pop(match_id, None)
                    return True
        
        return False
    
    def update_ready_status(self, player_id, match_id, status):
        """
        更新玩家的准备状态
        
        Args:
            player_id: 玩家ID
            match_id: 对局ID
            status: 新的准备状态
            
        Returns:
            tuple: (更新是否成功, 准备状态信息)
        """
        # 检查对局是否存在
        match = self.matches.get(match_id)
        if not match:
            return False, {"error": "对局不存在"}
        
        # 如果玩家取消准备且倒计时正在进行，取消倒计时
        if not status and match.countdown_active:
            cancel_reason = "玩家取消准备"
            cancel_message = match.get_countdown_cancel_json(cancel_reason, player_id)
            match.cancel_countdown()
            
            # 如果有客户端处理器，通知双方倒计时取消
            if self.client_handler:
                asyncio.create_task(self.notify_players(match, cancel_message))
        
        # 更新玩家准备状态
        if match.update_ready_status(player_id, status):
            # 获取更新后的准备状态
            ready_status_json = match.get_ready_status_json()
            
            # 如果双方都已准备好且倒计时尚未开始，启动倒计时
            if match.are_all_ready() and not match.countdown_active and not match.game_started:
                # 标记倒计时已启动
                match.countdown_active = True
                
                # 创建并启动倒计时任务
                match.countdown_task = asyncio.create_task(
                    self.start_countdown(match)
                )
                
            return True, ready_status_json
        else:
            return False, {"error": "无法更新准备状态"}
    
    async def start_countdown(self, match:Match):
        """
        启动游戏倒计时
        
        Args:
            match: Match对象
        """
        if not self.client_handler:
            print("错误: 客户端处理器未设置，无法发送倒计时消息")
            return
            
        try:
            # 发送倒计时开始消息
            countdown_start = match.get_countdown_start_json()
            await self.notify_players(match, countdown_start)
            
            # 3秒倒计时
            for remaining in range(3, 0, -1):
                # 如果倒计时被取消，提前退出
                if not match.countdown_active:
                    return
                    
                # 发送倒计时更新消息
                countdown_update = match.get_countdown_update_json(remaining)
                await self.notify_players(match, countdown_update)
                
                # 等待1秒
                await asyncio.sleep(1)
                
            # 倒计时结束，发送游戏开始消息
            if match.countdown_active:
                # 初始化游戏矩阵
                if match.initialize_game_matrices():
                    print(f"对局 {match.match_id} 的游戏矩阵已初始化")
                else:
                    print(f"对局 {match.match_id} 的游戏矩阵初始化失败")
                
                # 发送游戏开始消息
                game_start = match.get_game_start_json()
                await self.notify_players(match, game_start)
                
                # 发送矩阵状态
                matrix_state = match.get_match_state_json()
                await self.notify_players(match, json.loads(matrix_state))
                
                # 发送初始游戏时间信息
                game_time_init = match.get_game_time_init_json()
                await self.notify_players(match, game_time_init)
                
                # 更新游戏状态
                match.game_started = True
                match.countdown_active = False
                
                # 启动游戏计时器，仅用于服务端计时，不再发送更新
                match.game_timer_active = True
                match.last_time_update = time.time()
                match.game_timer_task = asyncio.create_task(
                    self.run_game_timer(match)
                )
                
        except Exception as e:
            print(f"倒计时过程中出错: {e}")
            match.countdown_active = False
    
    async def notify_players(self, match, message):
        """
        向对局中的两个玩家发送消息
        
        Args:
            match: Match对象
            message: 要发送的消息（字典或JSON字符串）
        """
        if not self.client_handler:
            return
            
        try:
            # 向两个玩家发送消息
            await self.client_handler.send_to_client(match.player1["id"], message)
            await self.client_handler.send_to_client(match.player2["id"], message)
        except Exception as e:
            print(f"通知玩家时出错: {e}")
    
    def handle_click(self, player_id, match_id, row, col):
        """
        处理玩家的点击操作
        
        Args:
            player_id: 玩家ID
            match_id: 对局ID
            row: 点击的行
            col: 点击的列
            
        Returns:
            tuple: (处理是否成功, 点击处理结果)
        """
        # 检查对局是否存在
        match = self.matches.get(match_id)
        if not match:
            return False, {"error": "对局不存在"}
        
        # 处理点击操作
        result = match.handle_click(player_id, row, col)
        
        # 如果点击操作成功，返回更新后的矩阵状态
        if result.get("success", False):
            matrix_state = match.get_match_state_json()
            
            # 如果是消除操作且得分更新，发送得分更新消息
            if result.get("action") == "eliminated" and result.get("score_updated", False):
                # 获取得分更新消息
                score_update = match.get_score_update_json()
                
                # 如果有客户端处理器，向双方发送得分更新
                if self.client_handler:
                    asyncio.create_task(self.notify_players(match, score_update))
                    
            return True, matrix_state
        else:
            return False, result
    
    def get_match_by_player(self, player_id):
        """
        根据玩家ID获取对局
        
        Args:
            player_id: 玩家ID
            
        Returns:
            Match: 对局对象或None
        """
        match_id = self.player_to_match.get(player_id)
        if match_id:
            return self.matches.get(match_id)
        return None

    async def run_game_timer(self, match:Match):
        """
        运行游戏计时器，监控游戏时间（不再发送时间更新消息）
        
        Args:
            match: Match对象
        """
        if not self.client_handler:
            print("错误: 客户端处理器未设置，无法发送游戏结束消息")
            return
            
        try:
            # 时间更新间隔
            update_interval = 0.5
            
            # 游戏计时器循环
            while match.game_timer_active and match.remaining_time > 0:
                # 计算经过的时间
                current_time = time.time()
                elapsed = current_time - match.last_time_update
                match.last_time_update = current_time
                
                # 更新剩余时间
                game_over = match.update_game_time(elapsed)
                
                # 如果游戏结束(时间耗尽)，处理游戏结束逻辑
                if game_over:
                    print(f"对局 {match.match_id} 时间耗尽，游戏结束")
                    # 确定获胜者 (根据得分)
                    winner_id = self._determine_winner(match)
                    
                    # 发送游戏结束消息
                    game_over_message = match.get_game_over_json(winner_id, "time_up")
                    await self.notify_players(match, game_over_message)
                    
                    match.game_timer_active = False
                    break
                
                # 等待下一次更新
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            print(f"对局 {match.match_id} 的游戏计时器被取消")
        except Exception as e:
            print(f"游戏计时器运行出错: {e}")
        finally:
            match.game_timer_active = False

    def _determine_winner(self, match:Match):
        """
        根据得分和消除数量确定获胜者
        
        Args:
            match: Match对象
            
        Returns:
            str: 获胜玩家的ID，如果平局则返回得分更高的玩家
        """
        player1_score = match.player1["score"]
        player2_score = match.player2["score"]
        
        # 得分高的玩家获胜
        if player1_score > player2_score:
            return [match.player1["id"]]
        elif player2_score > player1_score:
            return [match.player2["id"]]
        else:
            # 平局，返回两个玩家的ID
            return [match.player1["id"], match.player2["id"]]