"""
游戏管理器模块，负责管理玩家匹配和对局管理
"""
import uuid
import time
from .match import Match


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
        
        # 更新玩家准备状态
        if match.update_ready_status(player_id, status):
            # 返回更新后的准备状态
            return True, match.get_ready_status_json()
        else:
            return False, {"error": "无法更新准备状态"}
    
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