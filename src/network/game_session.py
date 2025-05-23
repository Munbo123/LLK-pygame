"""
游戏会话管理器，管理联机模式下的游戏状态
"""
from pprint import pprint
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
        self.game_over = False  # 游戏是否结束
        self.winner_id = None   # 获胜者ID
        
        # 得分相关属性
        self.player_score = 0
        self.opponent_score = 0
        self.player_elimination_count = 0
        self.opponent_elimination_count = 0
        
        # 时间相关属性
        self.total_time = 300  # 默认游戏总时间为300秒
        self.remaining_time = 300  # 剩余时间初始值
        
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
        self.network_client.register_handler('elimination_path', self._handle_elimination_path)
        self.network_client.register_handler('score_update', self._handle_score_update)
        self.network_client.register_handler('game_time_init', self._handle_game_time_init)
        self.network_client.register_handler('game_over', self._handle_game_over)
        
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
            
    def _handle_matrix_state(self, message:dict):
        """
        处理矩阵状态更新消息
        
        Args:
            message: 矩阵状态更新消息数据
        """
        pprint(f"\033[31m收到矩阵状态更新消息:\n{message}\033[0m")
        data = message.get("data", {})
        matrices = data.get("matrices", {})
        
        # 获取玩家ID
        player_id = self.network_client.user_id
        opponent_id = self.network_client.opponent_id
        
        # 检查矩阵数据是否存在
        if player_id in matrices and opponent_id in matrices:
            # 直接使用服务器发送的数据进行更新
            print("收到矩阵状态更新")
            # 直接更新矩阵
            self._update_matrix_from_data(matrices[player_id], is_player=True)
            self._update_matrix_from_data(matrices[opponent_id], is_player=False)
            
    def _update_matrix_from_data(self, matrix_data:list[list[dict]], is_player=True):
        """
        从服务器数据更新矩阵
        
        Args:
            matrix_data: 矩阵数据
            is_player: 是否是玩家矩阵
        """
        # 获取当前要更新的矩阵
        if is_player:
            self.player_matrix = matrix_data
        else:
            self.opponent_matrix = matrix_data
        
        # # 如果矩阵不存在或尺寸变化，创建新矩阵
        # if target_matrix is None:
        #     # 注意：由于在网络模式下，我们只关心矩阵状态，不需要实际的元素图像
        #     # 因此可以使用空列表作为元素，后续渲染时直接使用状态信息
        #     row = matrix_data.get("row", 0)
        #     col = matrix_data.get("col", 0)
        #     if is_player:
        #         self.player_matrix = {
        #             "matrix": matrix_data.get("matrix", []),
        #             "row": row,
        #             "col": col,
        #             "left_elements": matrix_data.get("left_elements", row * col)
        #         }
        #     else:
        #         self.opponent_matrix = {
        #             "matrix": matrix_data.get("matrix", []),
        #             "row": row,
        #             "col": col,
        #             "left_elements": matrix_data.get("left_elements", row * col)
        #         }
        # else:
        #     # 更新现有矩阵
        #     matrix = matrix_data.get("matrix", [])
        #     left_elements = matrix_data.get("left_elements", 0)
            
        #     if is_player:
        #         self.player_matrix["matrix"] = matrix
        #         self.player_matrix["left_elements"] = left_elements
        #     else:
        #         self.opponent_matrix["matrix"] = matrix
        #         self.opponent_matrix["left_elements"] = left_elements
                
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
    
    def get_player_matrix(self) -> list[list[dict]]:
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
        
    def _handle_time_update(self, message):
        """
        处理时间更新消息
        
        Args:
            message: 时间更新消息数据
        """
        data = message.get("data", {})
        self.remaining_time = data.get("remaining_time", 300)
        self.total_time = data.get("total_time", 300)
        
        print(f"更新游戏时间：剩余 {self.remaining_time} 秒，总时间 {self.total_time} 秒")
        
        # 触发回调函数(如果已设置)
        if hasattr(self, 'on_time_update') and callable(self.on_time_update):
            self.on_time_update(self.remaining_time, self.total_time)

    def get_time_info(self):
        """
        获取游戏时间信息
        
        Returns:
            tuple: (剩余时间, 总时间)
        """
        return (self.remaining_time, self.total_time)
        
    def set_time_update_callback(self, callback):
        """
        设置时间更新消息的回调函数
        
        Args:
            callback: 回调函数，接收参数(remaining_time, total_time)
        """
        self.on_time_update = callback
        
    def _handle_game_time_init(self, message):
        """
        处理游戏初始时间消息
        
        Args:
            message: 游戏初始时间消息数据
        """
        data = message.get("data", {})
        self.total_time = data.get("total_time", 300)
        self.remaining_time = self.total_time
        
        print(f"收到游戏初始时间: {self.total_time} 秒")
        
        # 触发回调函数(如果已设置)
        if hasattr(self, 'on_game_time_init') and callable(self.on_game_time_init):
            self.on_game_time_init(self.total_time)
        
    def _handle_game_over(self, message):
        """
        处理游戏结束消息
        
        Args:
            message: 游戏结束消息数据
        """
        data = message.get("data", {})
        self.winner_id = data.get("winner_id")
        reason = data.get("reason", "time_up")
        
        # 设置游戏结束状态
        self.game_over = True
        
        print(f"游戏结束！原因: {reason}, 获胜者ID: {self.winner_id}")
        
        # 更新最终得分
        scores = data.get("scores", {})
        player_id = self.network_client.user_id
        opponent_id = self.network_client.opponent_id
        
        if player_id in scores:
            player_score_data = scores[player_id]
            self.player_score = player_score_data.get("score", 0)
            self.player_elimination_count = player_score_data.get("elimination_count", 0)
        
        if opponent_id in scores:
            opponent_score_data = scores[opponent_id]
            self.opponent_score = opponent_score_data.get("score", 0)
            self.opponent_elimination_count = opponent_score_data.get("elimination_count", 0)
        
        # 触发回调函数(如果已设置)
        if hasattr(self, 'on_game_over') and callable(self.on_game_over):
            self.on_game_over(player_id in self.winner_id)
            
    def is_game_over(self):
        """
        检查游戏是否已结束
        
        Returns:
            bool: 游戏是否已结束
        """
        return self.game_over
    
    def is_player_winner(self):
        """
        检查玩家是否是获胜者
        
        Returns:
            bool: 玩家是否获胜
        """
        return self.winner_id == self.network_client.user_id
        
    def set_game_over_callback(self, callback):
        """
        设置游戏结束消息的回调函数
        
        Args:
            callback: 回调函数，接收参数(is_player_winner)，表示玩家是否获胜
        """
        self.on_game_over = callback

    def set_game_time_init_callback(self, callback):
        """
        设置游戏初始时间消息的回调函数
        
        Args:
            callback: 回调函数，接收参数(total_time)
        """
        self.on_game_time_init = callback