"""
计分板组件，用于在游戏中显示玩家分数和状态信息
"""
import pygame

class Scoreboard:
    """计分板组件类"""
    
    def __init__(self, screen, position=(0, 0), size=(200, 200)):
        """
        初始化计分板
        
        Args:
            screen: Pygame屏幕对象
            position: 计分板左上角位置 (x, y)
            size: 计分板大小 (宽, 高)
        """
        self.screen = screen
        self.x, self.y = position
        self.width, self.height = size
        
        # 游戏状态相关
        self.is_game_started = False
        self.player_score = 0
        self.opponent_score = 0
        self.is_player_ready = False
        self.is_opponent_ready = False
        self.connection_status = "未连接"
        self.match_status = "请先连接服务器"
        
        # 颜色定义
        self.background_color = (240, 240, 240)  # 背景颜色
        self.border_color = (0, 0, 0)           # 边框颜色
        self.title_color = (0, 0, 0)            # 标题颜色
        self.ready_color = (0, 150, 0)          # 已准备颜色
        self.not_ready_color = (150, 0, 0)      # 未准备颜色
        self.connected_color = (0, 150, 0)      # 已连接颜色
        self.disconnected_color = (150, 0, 0)   # 未连接颜色
        
        # 字体
        self.font_title = pygame.font.SysFont('fangsong', 24)
        self.font_score = pygame.font.SysFont('fangsong', 20)
    
    def set_position(self, position):
        """
        设置计分板位置
        
        Args:
            position: 新位置 (x, y)
        """
        self.x, self.y = position
    
    def set_size(self, size):
        """
        设置计分板大小
        
        Args:
            size: 新大小 (宽, 高)
        """
        self.width, self.height = size
    
    def update_game_status(self, is_started):
        """
        更新游戏开始状态
        
        Args:
            is_started: 游戏是否已开始
        """
        self.is_game_started = is_started
    
    def update_scores(self, player_score, opponent_score):
        """
        更新玩家和对手分数
        
        Args:
            player_score: 玩家分数
            opponent_score: 对手分数
        """
        self.player_score = player_score
        self.opponent_score = opponent_score
    
    def update_ready_status(self, player_ready, opponent_ready):
        """
        更新准备状态
        
        Args:
            player_ready: 玩家是否准备
            opponent_ready: 对手是否准备
        """
        self.is_player_ready = player_ready
        self.is_opponent_ready = opponent_ready
    
    def update_connection_status(self, status):
        """
        更新连接状态
        
        Args:
            status: 连接状态文本
        """
        self.connection_status = status
    
    def update_match_status(self, status):
        """
        更新匹配状态
        
        Args:
            status: 匹配状态文本
        """
        self.match_status = status
    
    def draw(self):
        """
        绘制计分板
        """
        # 绘制计分板背景
        pygame.draw.rect(self.screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.border_color, (self.x, self.y, self.width, self.height), 2)
        
        # 绘制标题
        title_text = self.font_title.render("计分板", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.x + self.width // 2, self.y + 25))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分割线
        pygame.draw.line(self.screen, self.border_color, 
                         (self.x + 10, self.y + 50), 
                         (self.x + self.width - 10, self.y + 50), 
                         2)
        
        # 根据游戏状态显示不同的信息
        if self.is_game_started:
            # 游戏已开始，显示分数
            # 玩家分数
            player_text = self.font_score.render(f"我方得分: {self.player_score}", True, self.ready_color)
            self.screen.blit(player_text, (self.x + 20, self.y + 70))
            
            # 对手分数
            opponent_text = self.font_score.render(f"对方得分: {self.opponent_score}", True, self.not_ready_color)
            self.screen.blit(opponent_text, (self.x + 20, self.y + 100))
        else:
            # 游戏未开始，显示准备状态
            # 我方准备状态
            my_ready_status = "已准备" if self.is_player_ready else "未准备"
            my_ready_color = self.ready_color if self.is_player_ready else self.not_ready_color
            my_status_text = self.font_score.render(f"我方状态: {my_ready_status}", True, my_ready_color)
            self.screen.blit(my_status_text, (self.x + 20, self.y + 70))
            
            # 对手准备状态
            opponent_ready_status = "未匹配"
            opponent_ready_color = self.not_ready_color
            
            # 只有在匹配成功后才显示对手准备状态
            if self.match_status == "匹配成功":
                opponent_ready_status = "已准备" if self.is_opponent_ready else "未准备"
                opponent_ready_color = self.ready_color if self.is_opponent_ready else self.not_ready_color
                
            opponent_status_text = self.font_score.render(f"对方状态: {opponent_ready_status}", True, opponent_ready_color)
            self.screen.blit(opponent_status_text, (self.x + 20, self.y + 100))
        
        # 显示连接状态
        status_color = self.connected_color if self.connection_status == "已连接" else self.disconnected_color
        status_text = self.font_score.render(f"状态: {self.connection_status}", True, status_color)
        self.screen.blit(status_text, (self.x + 20, self.y + 130))
        
        # 显示匹配状态
        match_color = self.title_color
        if self.match_status == "匹配成功":
            match_color = self.connected_color
        elif self.match_status == "匹配中":
            match_color = (150, 150, 0)  # 黄色
        else:
            match_color = self.disconnected_color
        
        match_text = self.font_score.render(f"匹配: {self.match_status}", True, match_color)
        self.screen.blit(match_text, (self.x + 20, self.y + 160))