import pygame
import random
import time

from src.logic.matrix_logic import Matrix
from src.components.Button import Button
from src.components.ProgressBar import Progress_bar
from src.utils.image_processor import process_fruit_sheet
from src.utils.config import load_config
from src.network.network_client import NetworkClient
from src.network.game_session import GameSession

game_background_path = r"./assets/fruit_bg.bmp"
sheet_path = r"./assets/fruit_element.bmp"
mask_path = r"./assets/fruit_mask.bmp"
player_name = "Munbo123" # 玩家名称

class Network_mode:
    def __init__(self, screen:pygame.Surface,network_client:NetworkClient, game_session:GameSession):
        # 读取配置信息
        config = load_config()
        self.row = config.get("rows", 10)  # 默认行数为10
        self.col = config.get("columns", 10)  # 默认列数为10
        self.row = 4
        self.col = 4


        # 屏幕对象及其宽高
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # 游戏背景
        self.background = pygame.image.load(game_background_path).convert_alpha()
        
        # 初始化按钮
        self.init_buttons()
        
        # 加载水果图集和遮罩图像
        self.fruit_images = process_fruit_sheet(sheet_path, mask_path)
        
        # 游戏相关状态变量
        self.is_ready = False  # 准备状态
        self.game_started = False  # 游戏是否开始
        self.player_score = 0  # 玩家分数
        self.opponent_score = 0  # 对手分数
        
        # 添加连接和匹配状态变量
        self.connection_status = "未连接"  # 初始连接状态
        self.match_status = "请先连接服务器"  # 初始匹配状态
        
        # 添加用户名变量
        self.player_name = player_name  # 自己的用户名
        self.opponent_name = "None"     # 对手的用户名，初始为None
        
        # 记录上一帧的时间，用于计算时间差
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        # 游戏矩阵的起始位置
        self.game_matrix_x = 20
        self.game_matrix_y = 50

        # 动画列表
        self.animations = []

        # 网络客户端和游戏会话对象
        self.network_client = network_client
        self.game_session = game_session

        # 保存事件处理器引用，以便后续可以注销
        self.connection_handler = self.handle_connection_response
        self.match_handler = self.handle_match_success
        
        # 先注销可能已存在的事件处理器，防止重复注册
        self.network_client.unregister_handler('connection_response', self.connection_handler)
        self.network_client.unregister_handler('match_success', self.match_handler)
        
        # 注册网络事件处理器
        self.network_client.register_handler('connection_response', self.connection_handler)
        self.network_client.register_handler('match_success', self.match_handler)
        
        # 启动连接
        self.network_client.start()
        self.network_client.set_user_name(self.player_name)
    
    def handle_connection_response(self, message):
        """
        处理连接响应事件，更新连接状态
        
        Args:
            message: 连接响应消息数据
        """
        data = message.get("data", {})
        status = data.get("connection_status")
        
        if status == "connected":
            self.connection_status = "已连接"
            self.match_status = "匹配中"
            print(f"连接成功，用户ID: {self.network_client.user_id}")
        else:
            self.connection_status = "连接失败"
            self.match_status = "请先连接服务器"
            print(f"连接失败: {data.get('message')}")
    
    def handle_match_success(self, message):
        """
        处理匹配成功事件，更新对手用户名和匹配状态
        
        Args:
            message: 匹配成功消息数据
        """
        # 从网络客户端中获取对手用户名
        self.opponent_name = self.network_client.opponent_name
        # 更新匹配状态
        self.match_status = "匹配成功"
        print(f"匹配成功，对手名称: {self.opponent_name}")
        
        # 更新游戏状态
        self.game_started = True

    def init_buttons(self):
        # 定义按钮尺寸
        main_button_size = (100, 50)
        other_button_size = (75, 35)
        self.all_buttons = []

        # 准备按钮（左上角）
        self.ready_button = Button(screen=self.screen, position=(20, 20), rect=main_button_size, text="准备", font='fangsong')
        self.all_buttons.append(self.ready_button)
        
        # 返回按钮（左下角）
        self.return_button = Button(screen=self.screen, position=(20, 600-35), rect=other_button_size, text="返回", font='fangsong')
        self.all_buttons.append(self.return_button)
        
        # 重新连接按钮（右下角）
        self.reconnect_button = Button(screen=self.screen, position=(800-75-20, 600-35), rect=other_button_size, text="重连", font='fangsong')
        self.all_buttons.append(self.reconnect_button)

    def initialize_game(self):
        # 在游戏开始时初始化游戏矩阵
        # 这里仅为界面设计，实际游戏逻辑会由服务器控制
        pass
        
    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(self.background, (0, 0))

        # 绘制按钮
        for button in self.all_buttons:
            button.draw()
        
        # 绘制计分板（位于中间）
        self.draw_scoreboard()
        
        # 如果游戏已开始，绘制游戏区域
        if self.game_started:
            self.draw_game_area()
        else:
            # 显示等待信息
            font = pygame.font.SysFont('fangsong', 24)
            if not self.is_ready:
                waiting_text = "请点击准备按钮"
            else:
                waiting_text = "等待对手准备..."
            
            text_surface = font.render(waiting_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(140, 30))  # Positioned in the top left area
            self.screen.blit(text_surface, text_rect)
        
        # 绘制所有当前动画效果
        for animation in self.animations:
            if animation.get('type') == 'path':
                # 绘制路径动画
                path = animation['path']
                color = animation['color']
                
                # 计算元素宽高
                element_width = element_height = 40  # 假设水果图像的宽高为40
                
                # 只有至少有两个点的路径才能绘制
                if len(path) >= 2:
                    # 绘制路径连线
                    for i in range(len(path) - 1):
                        start_row, start_col = path[i]
                        end_row, end_col = path[i + 1]
                        
                        # 计算像素坐标
                        start_x = self.game_matrix_x + start_col * element_width + element_width // 2
                        start_y = self.game_matrix_y + start_row * element_height + element_height // 2
                        end_x = self.game_matrix_x + end_col * element_width + element_width // 2
                        end_y = self.game_matrix_y + end_row * element_height + element_height // 2
                        
                        # 绘制路径线
                        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 3)
                        
                        # 在路径点绘制小圆点
                        pygame.draw.circle(self.screen, (0, 0, 255), (start_x, start_y), 5)
                    
                    # 绘制最后一个点
                    last_row, last_col = path[-1]
                    last_x = self.game_matrix_x + last_col * element_width + element_width // 2
                    last_y = self.game_matrix_y + last_row * element_height + element_height // 2
                    pygame.draw.circle(self.screen, (0, 0, 255), (last_x, last_y), 5)

        pygame.display.flip()

    def draw_scoreboard(self):
        # 绘制中间的计分板
        scoreboard_width = 160
        scoreboard_height = 200
        scoreboard_x = (self.screen_width - scoreboard_width) // 2
        scoreboard_y = (self.screen_height - scoreboard_height) // 2
        
        # 绘制计分板背景
        pygame.draw.rect(self.screen, (240, 240, 240), (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height), 2)
        
        # 绘制标题
        font_title = pygame.font.SysFont('fangsong', 24)
        title_text = font_title.render("计分板", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(scoreboard_x + scoreboard_width // 2, scoreboard_y + 25))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分割线
        pygame.draw.line(self.screen, (0, 0, 0), 
                         (scoreboard_x + 10, scoreboard_y + 50), 
                         (scoreboard_x + scoreboard_width - 10, scoreboard_y + 50), 
                         2)
        
        # 绘制玩家分数
        font_score = pygame.font.SysFont('fangsong', 20)
        
        # 玩家分数
        player_text = font_score.render(f"我方得分: {self.player_score}", True, (0, 100, 0))
        self.screen.blit(player_text, (scoreboard_x + 20, scoreboard_y + 70))
        
        # 对手分数
        opponent_text = font_score.render(f"对方得分: {self.opponent_score}", True, (200, 0, 0))
        self.screen.blit(opponent_text, (scoreboard_x + 20, scoreboard_y + 100))
        
        # 显示连接状态
        status_color = (0, 150, 0) if self.connection_status == "已连接" else (150, 0, 0)
        status_text = font_score.render(f"状态: {self.connection_status}", True, status_color)
        self.screen.blit(status_text, (scoreboard_x + 20, scoreboard_y + 130))
        
        # 显示匹配状态
        match_color = (0, 0, 0)
        if self.match_status == "匹配成功":
            match_color = (0, 150, 0)
        elif self.match_status == "匹配中":
            match_color = (150, 150, 0)
        else:
            match_color = (150, 0, 0)
        
        match_text = font_score.render(f"匹配: {self.match_status}", True, match_color)
        self.screen.blit(match_text, (scoreboard_x + 20, scoreboard_y + 160))

    def draw_game_area(self):
        # 定义左侧和右侧游戏区域
        left_area_x = 20
        left_area_y = 50
        right_area_x = self.screen_width - 20 - self.col * 40  # 40是每个元素的宽度
        right_area_y = 50

        # 假设左侧是玩家自己的游戏区域，右侧是对手的游戏区域
        # 这里仅绘制示例网格，实际游戏中需要根据服务器数据渲染
        
        # 绘制左侧区域标题（包含玩家名称）
        font = pygame.font.SysFont('fangsong', 20)
        left_title = font.render("我方游戏区", True, (0, 100, 0))
        self.screen.blit(left_title, (left_area_x, left_area_y - 30))
        
        # 绘制右侧区域标题（包含对手名称）
        right_title = font.render("对方游戏区", True, (200, 0, 0))
        self.screen.blit(right_title, (right_area_x, right_area_y - 30))
        
        # 绘制玩家名称（显示在红框区域）
        name_font = pygame.font.SysFont('fangsong', 18)
        
        # 左侧显示自己的用户名
        player_name_text = name_font.render(self.player_name, True, (0, 0, 0))
        player_name_rect = player_name_text.get_rect(center=(left_area_x + self.col * 20, left_area_y + self.row * 40 + 30))
        # 绘制红框背景
        pygame.draw.rect(self.screen, (255, 200, 200), 
                        (player_name_rect.left - 10, player_name_rect.top - 5, 
                         player_name_rect.width + 20, player_name_rect.height + 10), 0)
        # 绘制红框边框
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (player_name_rect.left - 10, player_name_rect.top - 5, 
                         player_name_rect.width + 20, player_name_rect.height + 10), 2)
        self.screen.blit(player_name_text, player_name_rect)
        
        # 右侧显示对手的用户名
        opponent_name_text = name_font.render(self.opponent_name, True, (0, 0, 0))
        opponent_name_rect = opponent_name_text.get_rect(center=(right_area_x + self.col * 20, right_area_y + self.row * 40 + 30))
        # 绘制红框背景
        pygame.draw.rect(self.screen, (255, 200, 200), 
                        (opponent_name_rect.left - 10, opponent_name_rect.top - 5, 
                         opponent_name_rect.width + 20, opponent_name_rect.height + 10), 0)
        # 绘制红框边框
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (opponent_name_rect.left - 10, opponent_name_rect.top - 5, 
                         opponent_name_rect.width + 20, opponent_name_rect.height + 10), 2)
        self.screen.blit(opponent_name_text, opponent_name_rect)

        # 在这里应该根据从服务器接收的游戏状态数据来渲染游戏区域
        # 目前仅绘制网格示意图
        
        # 绘制左侧网格（玩家）
        for row in range(self.row):
            for col in range(self.col):
                rect = pygame.Rect(left_area_x + col * 40, left_area_y + row * 40, 40, 40)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
        
        # 绘制右侧网格（对手）
        for row in range(self.row):
            for col in range(self.col):
                rect = pygame.Rect(right_area_x + col * 40, right_area_y + row * 40, 40, 40)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def handle(self):
        next_page_id, done = None, False

        # 计算时间增量
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # 更新所有动画的存活时间，移除过期的动画
        i = 0
        while i < len(self.animations):
            self.animations[i]['expire'] -= delta_time
            if self.animations[i]['expire'] <= 0:
                # 动画结束时，如果有回调函数，则执行
                animation = self.animations[i]
                if 'callback' in animation and animation['callback'] is not None:
                    animation['callback'](*animation.get('callback_args', []))
                # 移除过期动画
                self.animations.pop(i)
            else:
                i += 1

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查按钮点击
                if self.ready_button.collidepoint(event.pos):
                    print("准备按钮 clicked")
                    self.is_ready = not self.is_ready
                    if self.is_ready:
                        self.ready_button.set_text("取消准备")
                    else:
                        self.ready_button.set_text("准备")
                    # 在这里应该发送准备状态到服务器
                
                elif self.return_button.collidepoint(event.pos):
                    print("返回按钮 clicked")
                    next_page_id, done = self.back_button_event()             
                elif self.reconnect_button.collidepoint(event.pos):
                    print("重新连接按钮 clicked")
                    self.reconnect_button_event()
                
                # 如果游戏已开始，处理游戏区域的点击事件
                if self.game_started:
                    # 获取鼠标点击位置
                    mouse_x, mouse_y = event.pos
                    
                    # 检查是否点击了左侧游戏区域（玩家区域）
                    if (self.game_matrix_x <= mouse_x < self.game_matrix_x + self.col * 40 and
                        self.game_matrix_y <= mouse_y < self.game_matrix_y + self.row * 40):
                        
                        # 计算行列索引
                        col = (mouse_x - self.game_matrix_x) // 40
                        row = (mouse_y - self.game_matrix_y) // 40
                        
                        print(f"点击了游戏区域: 行={row}, 列={col}")
                        # 在这里应该向服务器发送点击信息

        return (next_page_id, done)
    

    def back_button_event(self):
        """
        返回按钮事件处理函数
        """
        # 断开网络连接
        try:
            self.network_client.stop()
            print("已断开与服务器的连接")
        except Exception as e:
            print(f"断开连接时出错: {e}")
        
        # 重置游戏会话和状态
        self.game_session.reset()
        self.connection_status = "未连接"
        self.match_status = "请先连接服务器"
        self.opponent_name = "None"
        self.is_ready = False
        self.game_started = False
        
        return 'main_menu', False      


    def reconnect_button_event(self):
        """
        重新连接按钮事件处理函数
        """
        print("重新连接按钮 clicked")
        # 先尝试断开现有连接
        try:
            self.network_client.stop()
            print("断开了之前的连接")
        except Exception as e:
            print(f"断开之前连接时出错: {e}")
        
        # 重置游戏会话和状态
        self.game_session.reset()
        self.connection_status = "未连接"
        self.match_status = "请先连接服务器"
        self.opponent_name = "None"
        self.is_ready = False
        self.game_started = False
        
        # 重新启动连接
        try:
            self.network_client.start()
            self.network_client.set_user_name(self.player_name)
            print("尝试重新连接服务器...")
        except Exception as e:
            print(f"重新连接服务器时出错: {e}")