import uuid
import time
import json
import sys
import os
import random

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.logic.matrix_logic import Matrix

class Match:
    """管理两个玩家之间的对局"""
    
    def __init__(self, player1_id, player1_name, player2_id, player2_name, element_len=10):
        """初始化一个新的对局
        
        Args:
            player1_id: 第一个玩家ID
            player1_name: 第一个玩家名称
            player2_id: 第二个玩家ID
            player2_name: 第二个玩家名称
            element_len: 元素长度（默认10）
        """
        self.match_id = str(uuid.uuid4())
        self.element_len = element_len  # 元素长度
        self.player1 = {
            "id": player1_id,
            "name": player1_name,
            "ready": False,
            "matrix": None,  # 游戏开始时才初始化矩阵
            "selected_cells": [],  # 存储玩家选中的单元格位置
            "score": 0,  # 玩家得分
            "elimination_count": 0  # 消除的方块对数量
        }
        
        self.player2 = {
            "id": player2_id,
            "name": player2_name,
            "ready": False,
            "matrix": None,  # 游戏开始时才初始化矩阵
            "selected_cells": [],  # 存储玩家选中的单元格位置
            "score": 0,  # 玩家得分
            "elimination_count": 0  # 消除的方块对数量
        }
        
        self.created_at = time.time() * 1000  # 毫秒时间戳
        
        # 倒计时相关状态
        self.countdown_active = False  # 倒计时是否激活
        self.game_started = False      # 游戏是否已开始
        self.countdown_task = None     # 倒计时任务引用
        
        # 游戏时间相关状态
        self.total_game_time = 10     # 游戏总时间，默认60秒
        self.remaining_time = self.total_game_time  # 剩余时间
        self.game_timer_active = False  # 游戏计时器是否激活
        self.game_timer_task = None     # 游戏计时器任务引用
        self.last_time_update = time.time()  # 上次更新时间的时间戳
        
        
        # 游戏设置
        self.rows = 6  # 矩阵行数
        self.cols = 6  # 矩阵列数
        
    def initialize_game_matrices(self):
        """
        初始化游戏矩阵，为每个玩家创建一个新的矩阵
        
        Returns:
            bool: 是否成功初始化矩阵
        """
        if self.game_started:
            # 已经初始化过了
            return False
            
        try:
            # 为每个玩家创建矩阵
            self.player1["matrix"] = Matrix(self.rows, self.cols,element_len=self.element_len)
            self.player2["matrix"] = Matrix(self.rows, self.cols,element_len=self.element_len)
            
            self.game_started = True
            return True
            
        except Exception as e:
            print(f"初始化游戏矩阵时出错: {e}")
            return False
    
    def get_player_by_id(self, player_id):
        """根据玩家ID获取玩家信息
        
        Args:
            player_id: 玩家ID
            
        Returns:
            玩家信息字典或None（如果未找到）
        """
        if self.player1["id"] == player_id:
            return self.player1
        elif self.player2["id"] == player_id:
            return self.player2
        return None
    
    def get_opponent_by_id(self, player_id):
        """根据玩家ID获取对手信息
        
        Args:
            player_id: 玩家ID
            
        Returns:
            对手信息字典或None（如果未找到）
        """
        if self.player1["id"] == player_id:
            return self.player2
        elif self.player2["id"] == player_id:
            return self.player1
        return None
    
    def update_ready_status(self, player_id, status):
        """更新玩家准备状态
        
        Args:
            player_id: 玩家ID
            status: 新的准备状态
            
        Returns:
            bool: 是否成功更新
        """
        player = self.get_player_by_id(player_id)
        if not player:
            return False
        
        player["ready"] = status
        return True
    
    def are_all_ready(self):
        """检查所有玩家是否都已准备好
        
        Returns:
            bool: 如果所有玩家都准备好了，返回True，否则返回False
        """
        return self.player1["ready"] and self.player2["ready"]
    
    def handle_click(self, player_id, row, col):
        """处理玩家的点击操作
        
        Args:
            player_id: 点击的玩家ID
            row: 点击的行
            col: 点击的列
            
        Returns:
            dict: 包含操作结果的字典
        """
        player = self.get_player_by_id(player_id)
        if not player:
            return {"success": False, "error": "玩家不存在"}
        
        if not player["matrix"]:
            return {"success": False, "error": "游戏尚未开始"}
        
        try:
            # 获取当前格子状态
            player_matrix:Matrix = player["matrix"]
            cell = player_matrix.get_cell(row, col)
            current_status = cell["status"]
            
            # 处理点击逻辑
            if current_status == "normal":
                # 设置为选中状态
                player_matrix.set_status(row, col, "selected")
                # 添加到选中列表
                player["selected_cells"].append((row, col))
                
                # 检查是否有两个选中的单元格
                if len(player["selected_cells"]) == 2:
                    cell1_pos = player["selected_cells"][0]
                    cell2_pos = player["selected_cells"][1]
                    
                    # # 获取两个单元格的元素
                    # cell1 = player_matrix.get_cell(cell1_pos[0], cell1_pos[1])
                    # cell2 = player_matrix.get_cell(cell2_pos[0], cell2_pos[1])
                    
                    # 使用is_eliminable方法检查两个元素是否可以消除（考虑连接路径）
                    path = player_matrix.is_eliminable(
                        cell1_pos[0], cell1_pos[1],
                        cell2_pos[0], cell2_pos[1]
                    )
                    
                    if path:  # 如果有可行的连接路径
                        # 设置为消除状态
                        player_matrix.set_status(cell1_pos[0], cell1_pos[1], "eliminated")
                        player_matrix.set_status(cell2_pos[0], cell2_pos[1], "eliminated")
                        
                        # 减少剩余元素计数
                        player_matrix.decrease_elements(2)
                        
                        # 清空选中的单元格
                        player["selected_cells"] = []
                        
                        # 更新玩家得分和消除计数
                        player["score"] += 10  # 每消除一对方块得10分
                        player["elimination_count"] += 1
                        
                        print(f"玩家 {player['name']} 消除成功，当前得分: {player['score']}, 消除数量: {player['elimination_count']}")
                        
                        # 返回消除成功信息及连接路径
                        return {
                            "success": True, 
                            "action": "eliminated", 
                            "positions": [list(cell1_pos), list(cell2_pos)],
                            "path": [[p[0], p[1]] for p in path],  # 转换路径格式
                            "score_updated": True  # 标记分数已更新
                        }
                    else:
                        # 两个元素不可连接，取消选中状态
                        player_matrix.set_status(cell1_pos[0], cell1_pos[1], "normal")
                        player_matrix.set_status(cell2_pos[0], cell2_pos[1], "normal")
                        
                        # 清空选中的单元格
                        player["selected_cells"] = []
                        
                        # 返回取消选中信息
                        return {
                            "success": True, 
                            "action": "mismatch", 
                            "positions": [list(cell1_pos), list(cell2_pos)]
                        }
                
                # 只选中了一个单元格
                return {"success": True, "action": "selected", "position": [row, col]}
                
            elif current_status == "selected":
                # 取消选中状态
                player_matrix.set_status(row, col, "normal")
                
                # 从选中列表中移除
                if (row, col) in player["selected_cells"]:
                    player["selected_cells"].remove((row, col))
                
                return {"success": True, "action": "deselected", "position": [row, col]}
                
            elif current_status == "eliminated":
                # 已消除的格子不能点击
                return {"success": False, "error": "此格子已被消除"}
                
            else:
                return {"success": False, "error": f"未知状态: {current_status}"}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def get_match_state_json(self):
        """获取当前对局状态的JSON表示
        
        Returns:
            str: 对局状态的JSON字符串
        """
        match_state = {
            "type": "matrix_state",
            "data": {
                "match_id": self.match_id,
                "matrices": {
                    self.player1["id"]: self._get_matrix_data(self.player1["matrix"]),
                    self.player2["id"]: self._get_matrix_data(self.player2["matrix"])
                },
                "timestamp": int(time.time() * 1000)
            }
        }
        return json.dumps(match_state)
    
    def get_ready_status_json(self):
        """获取当前准备状态的JSON表示
        
        Returns:
            str: 准备状态的JSON字符串
        """
        ready_status = {
            "type": "ready_status_update",
            "data": {
                "match_id": self.match_id,
                "player_statuses": {
                    self.player1["id"]: {
                        "ready": self.player1["ready"],
                        "name": self.player1["name"]
                    },
                    self.player2["id"]: {
                        "ready": self.player2["ready"],
                        "name": self.player2["name"]
                    }
                },
                "all_ready": self.are_all_ready(),
                "timestamp": int(time.time() * 1000)
            }
        }
        return json.dumps(ready_status)
    
    def get_countdown_start_json(self):
        """获取倒计时开始的JSON表示
        
        Returns:
            dict: 倒计时开始的消息字典
        """
        return {
            "type": "countdown_start",
            "data": {
                "match_id": self.match_id,
                "duration": 3,
                "message": "双方已准备，游戏即将开始",
                "timestamp": int(time.time() * 1000)
            }
        }
        
    def get_countdown_update_json(self, remaining_seconds):
        """获取倒计时更新的JSON表示
        
        Args:
            remaining_seconds: 剩余秒数
            
        Returns:
            dict: 倒计时更新的消息字典
        """
        return {
            "type": "countdown_update",
            "data": {
                "match_id": self.match_id,
                "remaining_seconds": remaining_seconds,
                "timestamp": int(time.time() * 1000)
            }
        }
        
    def get_countdown_cancel_json(self, reason, player_id=None):
        """获取倒计时取消的JSON表示
        
        Args:
            reason: 取消原因
            player_id: 取消的玩家ID（如果适用）
            
        Returns:
            dict: 倒计时取消的消息字典
        """
        return {
            "type": "countdown_cancel",
            "data": {
                "match_id": self.match_id,
                "reason": reason,
                "player_id": player_id,
                "timestamp": int(time.time() * 1000)
            }
        }
        
    def get_game_start_json(self):
        """获取游戏开始的JSON表示
        
        Returns:
            dict: 游戏开始的消息字典
        """
        return {
            "type": "game_start",
            "data": {
                "match_id": self.match_id,
                "message": "游戏正式开始",
                "timestamp": int(time.time() * 1000)
            }
        }
        
    def cancel_countdown(self):
        """取消倒计时
        
        Returns:
            bool: 是否成功取消
        """
        if not self.countdown_active:
            return False
            
        self.countdown_active = False
        if self.countdown_task and not self.countdown_task.cancelled():
            self.countdown_task.cancel()
            self.countdown_task = None
        return True
    
    def _get_matrix_data(self, matrix:Matrix) -> list[list[dict]]:
        """将矩阵对象转换为可序列化的字典
        
        Args:
            matrix: Matrix对象
            
        Returns:
            dict: 表示矩阵的二维数组
        """
        matrix_data = matrix.get_matrix()
        return matrix_data
    
    def get_score_update_json(self):
        """获取当前得分状态的JSON表示
        
        Returns:
            dict: 得分更新的消息字典
        """
        return {
            "type": "score_update",
            "data": {
                "match_id": self.match_id,
                "scores": {
                    self.player1["id"]: {
                        "score": self.player1["score"],
                        "elimination_count": self.player1["elimination_count"],
                        "user_name": self.player1["name"]
                    },
                    self.player2["id"]: {
                        "score": self.player2["score"],
                        "elimination_count": self.player2["elimination_count"],
                        "user_name": self.player2["name"]
                    }
                },
                "timestamp": int(time.time() * 1000)
            }
        }
    
    def get_time_update_json(self):
        """获取时间更新的JSON表示
        
        Returns:
            dict: 时间更新的消息字典
        """
        return {
            "type": "time_update",
            "data": {
                "match_id": self.match_id,
                "remaining_time": int(self.remaining_time),
                "total_time": self.total_game_time,
                "timestamp": int(time.time() * 1000)
            }
        }
        
    def update_game_time(self, elapsed_seconds):
        """更新游戏剩余时间
        
        Args:
            elapsed_seconds: 经过的秒数
            
        Returns:
            bool: 是否游戏结束(时间耗尽)
        """
        self.remaining_time -= elapsed_seconds
        self.remaining_time = max(0, self.remaining_time)
        
        # 返回游戏是否结束(时间耗尽)
        return self.remaining_time <= 0

    def get_game_over_json(self, winner_id, reason):
        """获取游戏结束的JSON表示
        
        Args:
            winner_id: 获胜玩家ID
            reason: 游戏结束原因
            
        Returns:
            dict: 游戏结束的消息字典
        """
        return {
            "type": "game_over",
            "data": {
                "match_id": self.match_id,
                "winner_id": winner_id,
                "reason": reason,
                "scores": {
                    self.player1["id"]: {
                        "score": self.player1["score"],
                        "elimination_count": self.player1["elimination_count"],
                        "user_name": self.player1["name"]
                    },
                    self.player2["id"]: {
                        "score": self.player2["score"],
                        "elimination_count": self.player2["elimination_count"],
                        "user_name": self.player2["name"]
                    }
                },
                "timestamp": int(time.time() * 1000)
            }
        }

    def get_game_time_init_json(self):
        """获取游戏初始时间的JSON表示
        
        Returns:
            dict: 游戏初始时间的消息字典
        """
        return {
            "type": "game_time_init",
            "data": {
                "match_id": self.match_id,
                "total_time": self.total_game_time,
                "timestamp": int(time.time() * 1000)
            }
        }