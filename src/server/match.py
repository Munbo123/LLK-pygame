import uuid
import time
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.logic.matrix_logic import Matrix

class Match:
    """管理两个玩家之间的对局"""
    
    def __init__(self, player1_id, player1_name, player2_id, player2_name, elements):
        """初始化一个新的对局
        
        Args:
            player1_id: 第一个玩家ID
            player1_name: 第一个玩家名称
            player2_id: 第二个玩家ID
            player2_name: 第二个玩家名称
            elements: 用于初始化矩阵的元素列表
        """
        self.match_id = str(uuid.uuid4())
        self.player1 = {
            "id": player1_id,
            "name": player1_name,
            "ready": False,
            "matrix": Matrix(6, 6, elements)  # 创建6x6的矩阵实例
        }
        
        self.player2 = {
            "id": player2_id,
            "name": player2_name,
            "ready": False,
            "matrix": Matrix(6, 6, elements)  # 创建6x6的矩阵实例
        }
        
        self.created_at = time.time() * 1000  # 毫秒时间戳
        
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
        
        try:
            # 获取当前格子状态
            cell = player["matrix"].get_cell(row, col)
            current_status = cell["status"]
            
            # 处理点击逻辑
            if current_status == "normal":
                # 设置为选中状态
                player["matrix"].set_status(row, col, "selected")
                return {"success": True, "action": "selected", "position": [row, col]}
            elif current_status == "selected":
                # 取消选中
                player["matrix"].set_status(row, col, "normal")
                return {"success": True, "action": "deselected", "position": [row, col]}
            elif current_status == "eliminated":
                # 已消除的格子不能点击
                return {"success": False, "error": "此格子已被消除"}
            else:
                return {"success": False, "error": f"未知状态: {current_status}"}
                
        except Exception as e:
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
    
    def _get_matrix_data(self, matrix):
        """将矩阵对象转换为可序列化的字典
        
        Args:
            matrix: Matrix对象
            
        Returns:
            dict: 表示矩阵的字典
        """
        matrix_data = matrix.get_matrix()
        row = matrix.get_row()
        col = matrix.get_col()
        left_elements = matrix.get_left_elements()
        
        return {
            "matrix": matrix_data,
            "row": row,
            "col": col,
            "left_elements": left_elements
        }