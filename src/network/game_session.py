"""
游戏会话管理器，管理联机模式下的游戏状态
"""
import pygame
from src.logic.matrix_logic import Matrix
from src.network.network_client import NetworkClient

class GameSession:
    """游戏会话类，管理联机模式下的游戏状态"""
    
    def __init__(self, network_client:NetworkClient):
        """
        初始化游戏会话
        
        Args:
            network_client: NetworkClient实例
        """
        self.network_client = network_client
        self.match_id = None
        self.player_matrix = None
        self.opponent_matrix = None
        self.player_ready = False
        self.opponent_ready = False
        self.all_ready = False
        self.game_started = False
        
        # 注册网络事件处理器
        self._register_network_handlers()
        
    def _register_network_handlers(self):
        """注册网络事件处理器"""
        self.network_client.register_handler('match_success', self._handle_match_success)
        self.network_client.register_handler('ready_status_update', self._handle_ready_status)
        self.network_client.register_handler('matrix_state', self._handle_matrix_state)
        
    def _handle_match_success(self, message):
        """
        处理匹配成功消息
        
        Args:
            message: 匹配成功消息数据
        """
        data = message.get("data", {})
        self.match_id = data.get("match_id")
        
        # 重置游戏状态
        self.player_ready = False
        self.opponent_ready = False
        self.all_ready = False
        self.game_started = False
        
    def _handle_ready_status(self, message):
        """
        处理准备状态更新消息
        
        Args:
            message: 准备状态更新消息数据
        """
        data = message.get("data", {})
        player_statuses = data.get("player_statuses", {})
        
        # 获取玩家ID
        player_id = self.network_client.user_id
        opponent_id = self.network_client.opponent_id
        
        # 更新准备状态
        if player_id in player_statuses:
            self.player_ready = player_statuses[player_id].get("ready", False)
            
        if opponent_id in player_statuses:
            self.opponent_ready = player_statuses[opponent_id].get("ready", False)
            
        # 更新整体准备状态
        self.all_ready = data.get("all_ready", False)
        
        # 如果所有玩家都准备好了，游戏开始
        if self.all_ready and not self.game_started:
            self.game_started = True
            
    def _handle_matrix_state(self, message):
        """
        处理矩阵状态更新消息
        
        Args:
            message: 矩阵状态更新消息数据
        """
        data = message.get("data", {})
        matrices = data.get("matrices", {})
        
        # 获取玩家ID
        player_id = self.network_client.user_id
        opponent_id = self.network_client.opponent_id
        
        # 更新矩阵
        if player_id in matrices and opponent_id in matrices:
            self._update_matrix_from_data(matrices[player_id], is_player=True)
            self._update_matrix_from_data(matrices[opponent_id], is_player=False)
            
    def _update_matrix_from_data(self, matrix_data, is_player=True):
        """
        从服务器数据更新矩阵
        
        Args:
            matrix_data: 矩阵数据
            is_player: 是否是玩家矩阵
        """
        # 获取当前要更新的矩阵
        target_matrix = self.player_matrix if is_player else self.opponent_matrix
        
        # 如果矩阵不存在或尺寸变化，创建新矩阵
        if target_matrix is None:
            # 注意：由于在网络模式下，我们只关心矩阵状态，不需要实际的元素图像
            # 因此可以使用空列表作为元素，后续渲染时直接使用状态信息
            row = matrix_data.get("row", 0)
            col = matrix_data.get("col", 0)
            if is_player:
                self.player_matrix = {
                    "matrix": matrix_data.get("matrix", []),
                    "row": row,
                    "col": col,
                    "left_elements": matrix_data.get("left_elements", row * col)
                }
            else:
                self.opponent_matrix = {
                    "matrix": matrix_data.get("matrix", []),
                    "row": row,
                    "col": col,
                    "left_elements": matrix_data.get("left_elements", row * col)
                }
        else:
            # 更新现有矩阵
            matrix = matrix_data.get("matrix", [])
            left_elements = matrix_data.get("left_elements", 0)
            
            if is_player:
                self.player_matrix["matrix"] = matrix
                self.player_matrix["left_elements"] = left_elements
            else:
                self.opponent_matrix["matrix"] = matrix
                self.opponent_matrix["left_elements"] = left_elements
                
    def toggle_ready(self):
        """
        切换准备状态
        
        Returns:
            bool: 操作是否成功
        """
        # 切换状态并发送到服务器
        new_status = not self.player_ready
        result = self.network_client.send_ready_message(new_status)
        
        # 如果发送成功，预先更新本地状态（稍后会被服务器确认）
        if result:
            self.player_ready = new_status
            
        return result
    
    def send_click(self, row, col):
        """
        发送点击消息
        
        Args:
            row: 行
            col: 列
            
        Returns:
            bool: 操作是否成功
        """
        return self.network_client.send_click_message(row, col)
    
    def is_game_started(self):
        """
        检查游戏是否已开始
        
        Returns:
            bool: 游戏是否已开始
        """
        return self.game_started
    
    def get_player_matrix(self):
        """
        获取玩家矩阵
        
        Returns:
            dict: 玩家矩阵数据
        """
        return self.player_matrix
    
    def get_opponent_matrix(self):
        """
        获取对手矩阵
        
        Returns:
            dict: 对手矩阵数据
        """
        return self.opponent_matrix
    
    def get_ready_status(self):
        """
        获取准备状态
        
        Returns:
            tuple: (玩家准备状态, 对手准备状态, 全部准备状态)
        """
        return (self.player_ready, self.opponent_ready, self.all_ready)
    
    def reset(self):
        """
        重置会话状态
        """
        self.match_id = None
        self.player_matrix = None
        self.opponent_matrix = None
        self.player_ready = False
        self.opponent_ready = False
        self.all_ready = False
        self.game_started = False