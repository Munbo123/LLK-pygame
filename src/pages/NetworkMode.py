import pygame
import random
import time
import pprint

from src.logic.matrix_logic import Matrix
from src.components.Button import Button
from src.components.ProgressBar import Progress_bar
from src.components.Scoreboard import Scoreboard  # 导入新创建的计分板组件
from src.components.MatrixRenderer import MatrixRenderer  # 导入新创建的矩阵渲染器组件
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
        self.row = 6  # 设置为与服务端相同的行数
        self.col = 6  # 设置为与服务端相同的列数

        # 屏幕对象及其宽高
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # 游戏背景
        self.background = pygame.image.load(game_background_path).convert_alpha()
        
        # 初始化按钮
        self.init_buttons()
        
        # 加载水果图集和遮罩图像
        self.fruit_images = process_fruit_sheet(sheet_path, mask_path)
        
        # 打印水果图片数量，用于调试
        print(f"加载了 {len(self.fruit_images)} 个水果图片")
        
        # 游戏相关状态变量
        self.is_ready = False  # 准备状态
        self.game_started = False  # 游戏是否开始
        self.player_score = 0  # 玩家分数
        self.opponent_score = 0  # 对手分数
        
        # 倒计时相关状态
        self.countdown_active = False  # 倒计时是否激活
        self.countdown_seconds = 0     # 倒计时剩余秒数
        
        # 添加连接和匹配状态变量
        self.connection_status = "未连接"  # 初始连接状态
        self.match_status = "请先连接服务器"  # 初始匹配状态
        
        # 添加用户名变量
        self.player_name = player_name  # 自己的用户名
        self.opponent_name = "None"     # 对手的用户名，初始为None
        
        # 记录上一帧的时间，用于计算时间差
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        # 初始化计分板组件
        scoreboard_width = 200  # 增加计分板宽度从160到200
        scoreboard_height = 200
        scoreboard_x = (self.screen_width - scoreboard_width) // 2
        scoreboard_y = (self.screen_height - scoreboard_height) // 2
        self.scoreboard = Scoreboard(screen=self.screen, 
                                    position=(scoreboard_x, scoreboard_y), 
                                    size=(scoreboard_width, scoreboard_height))
        
        # 设置计分板初始状态
        self.scoreboard.update_connection_status(self.connection_status)
        self.scoreboard.update_match_status(self.match_status)
        self.scoreboard.update_ready_status(self.is_ready, False)  # 初始时双方都未准备
        self.scoreboard.update_game_status(self.game_started)
        self.scoreboard.update_scores(self.player_score, self.opponent_score)
        
        # 初始化玩家和对手的矩阵渲染器
        # 左侧玩家矩阵位置 
        self.left_area_x = 20
        self.left_area_y = 140
        # 右侧对手矩阵位置
        self.right_area_x = self.screen_width - 20 - self.col * 40
        self.right_area_y = 140
        
        # 初始化玩家矩阵渲染器
        self.player_matrix_renderer = MatrixRenderer(
            screen=self.screen,
            position=(self.left_area_x, self.left_area_y),
            cell_size=(40, 40),
            row=self.row,
            col=self.col,
            fruit_images=self.fruit_images
        )
        
        # 初始化对手矩阵渲染器
        self.opponent_matrix_renderer = MatrixRenderer(
            screen=self.screen,
            position=(self.right_area_x, self.right_area_y),
            cell_size=(40, 40),
            row=self.row,
            col=self.col,
            fruit_images=self.fruit_images
        )
        
        # 确保game_matrix_x和game_matrix_y与left_area_x和left_area_y一致
        self.game_matrix_x = self.left_area_x
        self.game_matrix_y = self.left_area_y

        # 动画列表
        self.animations = []
        self.elimination_animations = []

        # 网络客户端和游戏会话对象
        self.network_client = network_client
        self.game_session = game_session

        # 保存事件处理器引用，以便后续可以注销
        self.connection_handler = self.handle_connection_response
        self.match_handler = self.handle_match_success
        self.countdown_start_handler = self.handle_countdown_start
        self.countdown_update_handler = self.handle_countdown_update
        self.countdown_cancel_handler = self.handle_countdown_cancel
        self.game_start_handler = self.handle_game_start

        
        # 先注销可能已存在的事件处理器，防止重复注册
        self.network_client.unregister_handler('connection_response', self.connection_handler)
        self.network_client.unregister_handler('match_success', self.match_handler)
        self.network_client.unregister_handler('countdown_start', self.countdown_start_handler)
        self.network_client.unregister_handler('countdown_update', self.countdown_update_handler)
        self.network_client.unregister_handler('countdown_cancel', self.countdown_cancel_handler)
        self.network_client.unregister_handler('game_start', self.game_start_handler)

        
        # 注册网络事件处理器
        self.network_client.register_handler('connection_response', self.connection_handler)
        self.network_client.register_handler('match_success', self.match_handler)
        self.network_client.register_handler('countdown_start', self.countdown_start_handler)
        self.network_client.register_handler('countdown_update', self.countdown_update_handler)
        self.network_client.register_handler('countdown_cancel', self.countdown_cancel_handler)
        self.network_client.register_handler('game_start', self.game_start_handler)

        
        
        # 启动连接
        self.network_client.start()
        self.network_client.set_user_name(self.player_name)
        
        # 初始状态下准备按钮不可用
        self.update_ready_button_state()
    
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
            
        # 更新准备按钮状态
        self.update_ready_button_state()
    
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
        
        # 匹配成功时不立即设置游戏开始，等待倒计时结束
        # self.game_started = True  # 移除这一行
        
        # 更新准备按钮状态
        self.update_ready_button_state()

    def handle_countdown_start(self, message):
        """
        处理倒计时开始消息
        
        Args:
            message: 倒计时开始消息数据
        """
        data = message.get("data", {})
        duration = data.get("duration", 3)
        
        # 设置倒计时状态
        self.countdown_active = True
        self.countdown_seconds = duration
        
        print(f"倒计时开始，初始值: {duration}秒")
    
    def handle_countdown_update(self, message):
        """
        处理倒计时更新消息
        
        Args:
            message: 倒计时更新消息数据
        """
        data = message.get("data", {})
        remaining = data.get("remaining_seconds", 0)
        
        # 更新倒计时状态
        self.countdown_seconds = remaining
        
        print(f"倒计时更新: {remaining}秒")
    
    def handle_countdown_cancel(self, message):
        """
        处理倒计时取消消息
        
        Args:
            message: 倒计时取消消息数据
        """
        data = message.get("data", {})
        reason = data.get("reason", "未知原因")
        
        # 重置倒计时状态
        self.countdown_active = False
        self.countdown_seconds = 0
        
        print(f"倒计时取消: {reason}")
    
    def handle_game_start(self, message):
        """
        处理游戏开始消息
        
        Args:
            message: 游戏开始消息数据
        """
        # 重置倒计时状态
        self.countdown_active = False
        self.countdown_seconds = 0
        
        # 设置游戏已开始状态，并禁用准备按钮
        self.game_started = True
        self.ready_button.disable_button()
        
        print("游戏开始!")

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
   
    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(self.background, (0, 0))

        # 绘制按钮
        for button in self.all_buttons:
            button.draw()

        self.draw_scoreboard()  # 绘制计分板

        # 如果网络会话存在，绘制游戏元素
        if self.game_session and self.game_session.is_game_started():
            self.draw_game_area()   # 绘制游戏区域
            
        
        if self.countdown_active:
            self.draw_countdown()
        
        # 更新显示
        pygame.display.flip()

    def draw_countdown(self):
        """绘制倒计时显示"""
        # 倒计时字体和颜色
        font = pygame.font.SysFont('fangsong', 48, bold=True)
        countdown_color = (255, 0, 0)  # 红色
        
        # 创建倒计时文本
        countdown_text = f"即将开始 {self.countdown_seconds}s"
        text_surface = font.render(countdown_text, True, countdown_color)
        
        # 计算位置（屏幕顶部中间）
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 50))
        
        # 绘制倒计时文本
        self.screen.blit(text_surface, text_rect)

    def draw_scoreboard(self):
        """
        绘制计分板
        """
        # 首先更新计分板状态
        self.scoreboard.update_game_status(self.game_started)
        self.scoreboard.update_scores(self.player_score, self.opponent_score)
        self.scoreboard.update_ready_status(self.is_ready, self.game_session.get_opponent_ready_status() if self.match_status == "匹配成功" else False)
        self.scoreboard.update_connection_status(self.connection_status)
        self.scoreboard.update_match_status(self.match_status)
        
        # 调用计分板组件的绘制方法
        self.scoreboard.draw()

    def draw_game_area(self):
        # 定义左侧和右侧游戏区域，使用实例变量以保持一致性
        left_area_x = self.left_area_x
        left_area_y = self.left_area_y
        right_area_x = self.right_area_x
        right_area_y = self.right_area_y

        # 绘制左侧区域标题（包含玩家名称）
        font = pygame.font.SysFont('fangsong', 20)
        left_title = font.render("我方游戏区", True, (0, 100, 0))
        self.screen.blit(left_title, (left_area_x, left_area_y - 30))
        
        # 绘制右侧区域标题（包含对手名称）
        right_title = font.render("对方游戏区", True, (200, 0, 0))
        self.screen.blit(right_title, (right_area_x, right_area_y - 30))
        
        # 绘制玩家名称（显示在红框区域）
        name_font = pygame.font.SysFont('fangsong', 18)
        
        # 左侧显示自己的用户名，并添加"（我）"标识
        player_name_text = name_font.render(f"{self.player_name}（我）", True, (0, 0, 0))
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
        
        # 右侧显示对手的用户名（保持不变）
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

        # 从游戏会话获取矩阵数据
        player_matrix_data = self.game_session.get_player_matrix()
        opponent_matrix_data = self.game_session.get_opponent_matrix()
        
        # 更新玩家矩阵渲染器数据
        self.player_matrix_renderer.update_matrix_data(player_matrix_data)
        # 绘制玩家矩阵
        self.player_matrix_renderer.draw()
        
        # 更新对手矩阵渲染器数据
        self.opponent_matrix_renderer.update_matrix_data(opponent_matrix_data)
        # 绘制对手矩阵
        self.opponent_matrix_renderer.draw()

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
                    # 只有在按钮启用状态且匹配成功时才处理点击
                    if self.ready_button.is_button_enabled() and self.match_status == "匹配成功":
                        print("准备按钮 clicked")
                        self.is_ready = not self.is_ready
                        if self.is_ready:
                            self.ready_button.set_text("取消准备")
                        else:
                            self.ready_button.set_text("准备")
                        # 发送准备状态到服务器
                        self.network_client.send_ready_message(self.is_ready)
                    else:
                        print('准备按钮clicked，但不可用')
                
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
                    left_area_x = self.game_matrix_x
                    left_area_y = self.game_matrix_y
                    
                    # 获取玩家矩阵信息
                    player_matrix_data = self.game_session.get_player_matrix()
                    if player_matrix_data:
                        matrix_row = player_matrix_data.get("row", self.row)
                        matrix_col = player_matrix_data.get("col", self.col)
                        
                        # 计算矩阵区域
                        matrix_width = matrix_col * 40
                        matrix_height = matrix_row * 40
                        
                        # 检查是否在矩阵区域内点击
                        if (left_area_x <= mouse_x < left_area_x + matrix_width and
                            left_area_y <= mouse_y < left_area_y + matrix_height):
                            
                            # 计算行列索引
                            col = (mouse_x - left_area_x) // 40
                            row = (mouse_y - left_area_y) // 40
                            
                            print(f"点击了游戏区域: 行={row}, 列={col}")
                            
                            # 向服务器发送点击信息
                            self.game_session.send_click(row, col)

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

    def update_ready_button_state(self):
        """
        根据匹配状态更新准备按钮的可用状态
        """
        # 只有在匹配成功后准备按钮才可用
        print(f'{self.match_status}')
        if self.match_status == "匹配成功":
            self.ready_button.enable_button()
        else:
            self.ready_button.disable_button()
            # 如果按钮被禁用，确保状态一致
            self.is_ready = False
            self.ready_button.set_text("准备")

    def draw_matrix(self, matrix_data, start_x, start_y, is_player=True):
        """
        绘制矩阵
        
        Args:
            matrix_data: 矩阵数据字典
            start_x: 起始X坐标
            start_y: 起始Y坐标
            is_player: 是否是玩家矩阵
        """
        if not matrix_data:
            return
            
        matrix = matrix_data.get("matrix", [])
        row = matrix_data.get("row", 0)
        col = matrix_data.get("col", 0)
        
        # 如果矩阵数据为空，不绘制
        if not matrix or row == 0 or col == 0:
            return
            
        # 遍历矩阵，绘制每个元素
        for r in range(row):
            for c in range(col):
                # 计算元素位置
                x = start_x + c * 40
                y = start_y + r * 40
                
                try:
                    # 获取当前元素
                    cell = matrix[r][c]
                    element_index = cell.get("index", 0)
                    status = cell.get("status", "normal")
                    
                    # 根据状态绘制背景
                    rect = pygame.Rect(x, y, 40, 40)
                    
                    if status == "eliminated":
                        # 已消除的元素，绘制灰色背景
                        pygame.draw.rect(self.screen, (220, 220, 220), rect)
                        pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                    elif status == "selected":
                        # 选中的元素，绘制黄色背景
                        pygame.draw.rect(self.screen, (255, 255, 200), rect)
                        pygame.draw.rect(self.screen, (255, 200, 0), rect, 2)
                    else:
                        # 普通元素，绘制白色背景和黑色边框
                        pygame.draw.rect(self.screen, (255, 255, 255), rect)
                        pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                    
                    # 如果元素未被消除，绘制水果图像
                    if status != "eliminated":
                        # 首先验证索引的有效性，确保在范围内
                        if element_index >= 0 and element_index < len(self.fruit_images):
                            fruit_image = self.fruit_images[element_index]
                            
                            # 计算图像位置，居中显示
                            image_x = x + (40 - fruit_image.get_width()) // 2
                            image_y = y + (40 - fruit_image.get_height()) // 2
                            
                            # 绘制水果图像
                            self.screen.blit(fruit_image, (image_x, image_y))
                        else:
                            # 索引超出范围，使用默认图像（第一张）
                            if len(self.fruit_images) > 0:
                                fruit_image = self.fruit_images[0]
                                
                                # 计算图像位置，居中显示
                                image_x = x + (40 - fruit_image.get_width()) // 2
                                image_y = y + (40 - fruit_image.get_height()) // 2
                                
                                # 绘制水果图像
                                self.screen.blit(fruit_image, (image_x, image_y))
                except Exception as e:
                    pass

