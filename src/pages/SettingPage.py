import pygame
import os

# 设置环境变量以支持中文输入法
os.environ['SDL_IM_MODULE'] = 'ime'  # Windows系统使用ime

from src.components.Button import Button
from src.utils.config import load_config, update_game_size, update_config


class Setting_page:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = self.screen.get_height()

        # 启用文本输入模式，改善中文输入支持
        pygame.key.start_text_input()
        # 可以设置输入区域，提高输入法候选框的显示位置
        pygame.key.set_text_input_rect(pygame.Rect(self.screen_width // 2 - 30, 395, 200, 40))

        # 加载配置
        self.config = load_config()
        self.rows = self.config.get("rows", 10)
        self.columns = self.config.get("columns", 10)
        self.username = self.config.get("username", "player")  # 添加用户名配置读取
        
        # 初始化按钮
        self.init_buttons()
        
        # 创建字体
        self.title_font = pygame.font.SysFont("SimHei", 48)
        self.label_font = pygame.font.SysFont("SimHei", 30)
        self.value_font = pygame.font.SysFont("SimHei", 36)
        
        # 保存消息提示
        self.save_message = ""
        self.message_timer = 0
        
        # 用户名输入相关变量
        self.username_active = False  # 是否正在输入用户名
        self.username_input_rect = pygame.Rect(self.screen_width // 2 - 30, 395, 200, 40)
        self.username_cursor_visible = True
        self.username_cursor_timer = 0
    
    def init_buttons(self):
        # 创建按钮列表
        self.all_buttons = []
        
        # 返回按钮
        self.return_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 - 200-10, self.screen_height - 100),
            rect=(200, 50),
            text="返回",
            font='SimHei'
        )
        self.all_buttons.append(self.return_button)
        
        # 保存设置按钮
        self.save_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 + 10, self.screen_height - 100),
            rect=(200, 50),
            text="保存设置",
            font='SimHei'
        )
        self.all_buttons.append(self.save_button)
        
        # 行数增减按钮
        button_width, button_height = 30, 30
        
        # 行数增加按钮
        self.row_plus_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 + 50, 200),
            rect=(button_width, button_height),
            text="+",
            font='SimHei'
        )
        self.all_buttons.append(self.row_plus_button)
        
        # 行数减少按钮
        self.row_minus_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 - 50, 200),
            rect=(button_width, button_height),
            text="-",
            font='SimHei'
        )
        self.all_buttons.append(self.row_minus_button)
        
        # 列数增加按钮
        self.col_plus_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 + 50, 300),
            rect=(button_width, button_height),
            text="+",
            font='SimHei'
        )
        self.all_buttons.append(self.col_plus_button)
        
        # 列数减少按钮
        self.col_minus_button = Button(
            screen=self.screen,
            position=(self.screen_width // 2 - 50, 300),
            rect=(button_width, button_height),
            text="-",
            font='SimHei'
        )
        self.all_buttons.append(self.col_minus_button)

    def draw(self):
        # 清屏
        self.screen.fill((30, 30, 30))  # 使用深灰色背景以便按钮更清晰
   
        # 绘制标题
        title_text = self.title_font.render("游戏设置", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 绘制行数设置
        row_label = self.label_font.render("行数:", True, (255, 255, 255))
        self.screen.blit(row_label, (self.screen_width // 2 - 150, 200))
        
        row_value = self.value_font.render(f"{self.rows}", True, (255, 255, 0))
        self.screen.blit(row_value, (self.screen_width // 2 - 10, 195))
        
        # 绘制列数设置
        col_label = self.label_font.render("列数:", True, (255, 255, 255))
        self.screen.blit(col_label, (self.screen_width // 2 - 150, 300))
        
        col_value = self.value_font.render(f"{self.columns}", True, (255, 255, 0))
        self.screen.blit(col_value, (self.screen_width // 2 - 10, 295))
        
        # 绘制用户名设置
        username_label = self.label_font.render("用户名:", True, (255, 255, 255))
        self.screen.blit(username_label, (self.screen_width // 2 - 150, 400))
        
        # 绘制用户名输入框
        username_box_color = (100, 100, 200) if self.username_active else (70, 70, 70)
        pygame.draw.rect(self.screen, username_box_color, self.username_input_rect, 2)
        
        # 绘制用户名文本
        username_surface = self.label_font.render(self.username, True, (255, 255, 0))
        self.screen.blit(username_surface, (self.username_input_rect.x + 5, self.username_input_rect.y + 5))
        

        # 如果正在输入用户名，显示闪烁的光标
        if self.username_active:
            # 每30帧切换光标显示状态
            self.username_cursor_timer += 1
            if self.username_cursor_timer > 30:
                self.username_cursor_visible = not self.username_cursor_visible
                self.username_cursor_timer = 0
                
            if self.username_cursor_visible:
                cursor_pos = self.label_font.size(self.username)[0]
                pygame.draw.line(self.screen, 
                                (255, 255, 255), 
                                (self.username_input_rect.x + 5 + cursor_pos, self.username_input_rect.y + 5), 
                                (self.username_input_rect.x + 5 + cursor_pos, self.username_input_rect.y + 35), 
                                2)
        
        # 绘制按钮
        for button in self.all_buttons:
            button.draw()
        
        # 显示保存消息提示
        if self.save_message and self.message_timer > 0:
            message = self.label_font.render(self.save_message, True, (0, 255, 0))
            message_rect = message.get_rect(center=(self.screen_width // 2, self.screen_height - 150))
            self.screen.blit(message, message_rect)
            self.message_timer -= 1
        
        # 更新显示
        pygame.display.flip()

    def handle(self):
        # 要返回的状态
        next_page_id = None
        done = False
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查用户点击了用户名输入框
                if self.username_input_rect.collidepoint(mouse_pos):
                    self.username_active = True
                    self.username_cursor_visible = True
                    self.username_cursor_timer = 0
                else:
                    self.username_active = False
                
                # 检查行列数增减按钮
                if self.row_plus_button.collidepoint(mouse_pos):
                    self.rows = min(10, self.rows + 1)  # 设置上限为10行
                    
                elif self.row_minus_button.collidepoint(mouse_pos):
                    self.rows = max(4, self.rows - 1)  # 设置下限为4行
                    
                elif self.col_plus_button.collidepoint(mouse_pos):
                    self.columns = min(15, self.columns + 1)  # 设置上限为15列
                    
                elif self.col_minus_button.collidepoint(mouse_pos):
                    self.columns = max(4, self.columns - 1)  # 设置下限为4列
                
                # 检查返回按钮
                elif self.return_button.collidepoint(mouse_pos):
                    next_page_id = "main_menu"
                    pygame.display.set_caption('欢乐连连看')
                
                # 检查保存按钮
                elif self.save_button.collidepoint(mouse_pos):
                    if self.rows*self.columns%2 != 0:
                        self.save_message = "行列数乘积必须为偶数！"
                        self.message_timer = 60
                    else:
                        save_status = []
                        # 保存行数
                        save_status.append(update_config("rows", self.rows))
                        # 保存列数
                        save_status.append(update_config("columns", self.columns))
                        # 保存用户名
                        save_status.append(update_config("username", self.username))
                    
                        if save_status.count(True) == len(save_status):
                            # 显示保存成功提示
                            self.save_message = "设置已保存"
                            self.message_timer = 60  # 显示约2秒（假设游戏运行在30FPS）
                        else:
                            self.save_message = "保存失败"
                            self.message_timer = 60
            
            # 处理键盘事件（用于用户名输入）
            if event.type == pygame.KEYDOWN and self.username_active:
                if event.key == pygame.K_RETURN:
                    # 按回车完成输入
                    self.username_active = False
                elif event.key == pygame.K_BACKSPACE:
                    # 退格键删除字符
                    self.username = self.username[:-1]
                # 移除了直接使用KEYDOWN事件添加字符的代码
            
            # 使用TEXTINPUT事件处理文本输入，包括中文和其他语言
            elif event.type == pygame.TEXTINPUT and self.username_active:
                # 添加字符（仅添加有效字符且限制长度）
                if len(self.username) < 12:
                    print(f"文本输入: {event.text}")
                    self.username += event.text
        
        return next_page_id, done