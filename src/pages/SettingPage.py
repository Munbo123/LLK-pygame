import pygame

from src.components.Button import Button
from src.utils.config import load_config, update_game_size


main_menu_background_path = r"./assets/llk_main.bmp"

class Setting_page:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 加载背景图像 (使用和主界面相同的背景)
        self.background = pygame.image.load(main_menu_background_path).convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        # 加载配置
        self.config = load_config()
        self.rows = self.config.get("rows", 10)
        self.columns = self.config.get("columns", 10)
        
        # 初始化按钮
        self.init_buttons()
        
        # 创建字体
        self.title_font = pygame.font.SysFont("SimHei", 48)
        self.label_font = pygame.font.SysFont("SimHei", 30)
        self.value_font = pygame.font.SysFont("SimHei", 36)
        
        # 保存消息提示
        self.save_message = ""
        self.message_timer = 0
    
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

        # 绘制背景
        # self.screen.blit(self.background, (0, 0))
        
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
                
                # 检查行列数增减按钮
                if self.row_plus_button.collidepoint(mouse_pos):
                    self.rows = min(20, self.rows + 1)  # 设置上限为20行
                    
                elif self.row_minus_button.collidepoint(mouse_pos):
                    self.rows = max(4, self.rows - 1)  # 设置下限为4行
                    
                elif self.col_plus_button.collidepoint(mouse_pos):
                    self.columns = min(20, self.columns + 1)  # 设置上限为20列
                    
                elif self.col_minus_button.collidepoint(mouse_pos):
                    self.columns = max(4, self.columns - 1)  # 设置下限为4列
                
                # 检查返回按钮
                elif self.return_button.collidepoint(mouse_pos):
                    next_page_id = "main_menu"
                    pygame.display.set_caption('欢乐连连看')
                
                # 检查保存按钮
                elif self.save_button.collidepoint(mouse_pos):
                    # 保存设置
                    if update_game_size(self.rows, self.columns):
                        # 显示保存成功提示
                        self.save_message = "设置已保存"
                        self.message_timer = 60  # 显示约2秒（假设游戏运行在30FPS）
                    else:
                        self.save_message = "保存失败"
                        self.message_timer = 60
        
        return next_page_id, done