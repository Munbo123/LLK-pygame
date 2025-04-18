import pygame
import sys
import os


from components.Button import Button
from pages.BasicMode import Basic_mode
from pages.LeisureMode import Leisure_mode



icon_path = r"./assets/LLK.ico"
main_menu_background_path = r"./assets/llk_main.bmp"

# 设置窗口标题和图标
pygame.display.set_caption('欢乐连连看')
icon = pygame.image.load(icon_path)
pygame.display.set_icon(icon) # 可以填img



class Main_menu:
    def __init__(self,screen:pygame.Surface):
        # 屏幕对象
        self.screen = screen
        # 加载背景图片
        self.main_menu_background = pygame.image.load(main_menu_background_path)
        # 初始化按钮
        self.init_buttons()

    def init_buttons(self):
        mode_button_size = (100, 50)
        other_button_size = (75, 35)
        self.all_buttons = []

        # 模式按钮
        self.basic_mode_button = Button(screen=self.screen,position=(30, 215), rect=mode_button_size, text="基本模式",font='fangsong')  # 基本模式
        self.all_buttons.append(self.basic_mode_button)
        
        self.leisure_mode_button = Button(screen=self.screen,position=(30, 315), rect=mode_button_size, text="休闲模式",font='fangsong')    # 休闲模式
        self.all_buttons.append(self.leisure_mode_button)

        self.level_mode_button = Button(screen=self.screen,position=(30, 415), rect=mode_button_size, text="联机模式",font='fangsong')   # 联机模式
        self.all_buttons.append(self.level_mode_button)
        
        # 右下角按钮绘制
        self.chart_button = Button(screen=self.screen,position=(800-75*3, 600-35), rect=other_button_size, text="排行榜",font='fangsong')    # 排行榜
        self.all_buttons.append(self.chart_button)

        self.setting_button = Button(screen=self.screen,position=(800-75*2, 600-35), rect=other_button_size, text="设置",font='fangsong')    # 设置
        self.all_buttons.append(self.setting_button)

        self.help_button = Button(screen=self.screen,position=(800-75*1, 600-35), rect=other_button_size, text="帮助",font='fangsong')   # 帮助
        self.all_buttons.append(self.help_button)

    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(self.main_menu_background, (0, 0))

        # 绘制按钮
        for button in self.all_buttons:
            button.draw()

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
                if self.basic_mode_button.collidepoint(event.pos):
                    print("基本模式按钮 clicked")
                    next_page_id = 'basic_mode'
                    pygame.display.set_caption('欢乐连连看-基本模式')
                if self.leisure_mode_button.collidepoint(event.pos):
                    print("休闲模式按钮 clicked")
                    next_page_id = 'leisure_mode'
                    pygame.display.set_caption('欢乐连连看-休闲模式')
                if self.level_mode_button.collidepoint(event.pos):
                    print("关卡模式按钮 clicked")
                if self.chart_button.collidepoint(event.pos):
                    print("排行榜按钮 clicked")
                if self.setting_button.collidepoint(event.pos):
                    print("设置按钮 clicked")
                    next_page_id = 'setting_page'
                    pygame.display.set_caption('欢乐连连看-设置')
                if self.help_button.collidepoint(event.pos):
                    print("帮助按钮 clicked")
        
        return (next_page_id, done)

