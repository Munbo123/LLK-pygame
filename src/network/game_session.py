"""
游戏会话管理器，管理联机模式下的游戏状态
"""
import pprint
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
        
        # 得分相关属性
        self.player_score = 0
        self.opponent_score = 0
        self.player_elimination_count = 0
        self.opponent_elimination_count = 0
        
        # 初始化消除路径相关属性
        self.elimination_path = None
        self.elimination_player_id = None
            
        # 注册网络事件处理器
        self._register_network_handlers()
        
    def _register_network_handlers(self):
        """注册网络事件处理器"""
        self.network_client.register_handler('match_success', self._handle_match_success)
        self.network_client.register_handler('ready_status_update', self._handle_ready_status)
        self.network_client.register_handler('matrix_state', self._handle_matrix_state)
        self.network_client.register_handler('game_start', self._handle_game_start)
        # 注册新的消除路径消息处理器
        self.network_client.register_handler('elimination_path', self._handle_elimination_path)
        # 注册得分更新消息处理器
        self.network_client.register_handler('score_update', self._handle_score_update)
        
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
        
        # 检查矩阵数据是否存在
        if player_id in matrices and opponent_id in matrices:
            # 直接使用服务器发送的数据进行更新
            print("\n收到矩阵状态更新：")
            if player_id in matrices:
                player_matrix = matrices[player_id]
                matrix_data = player_matrix.get('matrix', [])
                row = player_matrix.get('row', 0)
                col = player_matrix.get('col', 0)
                
                print(f"玩家矩阵 ({row}x{col}):")
                pp = pprint.PrettyPrinter(indent=2, width=120)
                
                # 打印简化版的矩阵，只显示索引和状态
                simplified_matrix = []
                for r in range(min(row, len(matrix_data))):
                    row_data = []
                    for c in range(min(col, len(matrix_data[r]))):
                        cell = matrix_data[r][c]
                        row_data.append({
                            'i': cell.get('index', -1),  # 使用'i'代替'index'使输出更紧凑
                            's': cell.get('status', 'n')[0]  # 只使用状态的首字母
                        })
                    simplified_matrix.append(row_data)
                pp.pprint(simplified_matrix)
            
            # 直接更新矩阵
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
    
    def get_opponent_ready_status(self):
        """
        获取对手准备状态
        
        Returns:
            bool: 对手是否已准备
        """
        return self.opponent_ready
    
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

    def _handle_game_start(self, message):
        """
        处理游戏开始消息
        
        Args:
            message: 游戏开始消息数据
        """
        # 设置游戏已开始状态
        self.game_started = True
        print("收到游戏开始消息，游戏现在正式开始")
        
    def _handle_elimination_path(self, message):
        """
        处理消除路径消息
        
        Args:
            message: 消除路径消息数据
        """
        data = message.get("data", {})
        
        # 提取消除路径信息
        elimination_path = data.get("path", [])
        player_id = data.get("player_id")
        
        if elimination_path:
            print(f"收到消除路径: {elimination_path}, 玩家ID: {player_id}")
            
            # 保存消除路径信息，供界面类使用
            self.elimination_path = elimination_path
            self.elimination_player_id = player_id
            
            # 触发回调函数(如果已设置)
            if hasattr(self, 'on_elimination_path') and callable(self.on_elimination_path):
                self.on_elimination_path(elimination_path, player_id)
    
    def get_elimination_path(self):
        """
        获取最新的消除路径信息
        
        Returns:
            tuple: (路径列表, 玩家ID)
        """
        path = self.elimination_path
        player_id = self.elimination_player_id
        
        # 返回后清空，避免重复处理
        self.elimination_path = None
        self.elimination_player_id = None
        
        return (path, player_id)
        
    def set_elimination_path_callback(self, callback):
        """
        设置消除路径消息的回调函数
        
        Args:
            callback: 回调函数，接收参数(path, player_id)
        """
        self.on_elimination_path = callback

    def _handle_score_update(self, message):
        """
        处理得分更新消息
        
        Args:
            message: 得分更新消息数据
        """
        data = message.get("data", {})
        scores = data.get("scores", {})
        
        # 获取玩家ID
        player_id = self.network_client.user_id
        opponent_id = self.network_client.opponent_id
        
        # 更新玩家得分
        if player_id in scores:
            player_score_data = scores[player_id]
            self.player_score = player_score_data.get("score", 0)
            self.player_elimination_count = player_score_data.get("elimination_count", 0)
            print(f"更新玩家得分: {self.player_score}, 消除数量: {self.player_elimination_count}")
        
        # 更新对手得分
        if opponent_id in scores:
            opponent_score_data = scores[opponent_id]
            self.opponent_score = opponent_score_data.get("score", 0)
            self.opponent_elimination_count = opponent_score_data.get("elimination_count", 0)
            print(f"更新对手得分: {self.opponent_score}, 消除数量: {self.opponent_elimination_count}")
            
        # 触发回调函数(如果已设置)
        if hasattr(self, 'on_score_update') and callable(self.on_score_update):
            self.on_score_update(self.player_score, self.opponent_score)
            
    def get_scores(self):
        """
        获取玩家和对手的得分
        
        Returns:
            tuple: (玩家得分, 对手得分)
        """
        return (self.player_score, self.opponent_score)
    
    def get_elimination_counts(self):
        """
        获取玩家和对手的消除数量
        
        Returns:
            tuple: (玩家消除数量, 对手消除数量)
        """
        return (self.player_elimination_count, self.opponent_elimination_count)
        
    def set_score_update_callback(self, callback):
        """
        设置得分更新消息的回调函数
        
        Args:
            callback: 回调函数，接收参数(player_score, opponent_score)
        """
        self.on_score_update = callback