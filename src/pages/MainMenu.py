import pygame
import sys
import os


from components.Button import Button
from pages.BasicMode import Basic_mode
from pages.LeisureMode import Leisure_mode


# 设置窗口标题和图标
pygame.display.set_caption('欢乐连连看')
icon = pygame.image.load(r"C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\res\连连看游戏综合实践\任务5-界面设计\实验素材\LLK.ico")
pygame.display.set_icon(icon) # 可以填img


# 加载背景图片
main_menu_background = pygame.image.load(r"C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\res\连连看游戏综合实践\任务5-界面设计\实验素材\llk_main.bmp")




class Main_menu:
    def __init__(self,screen:pygame.Surface):
        # 屏幕对象
        self.screen = screen

    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(main_menu_background, (0, 0))

        # 绘制模式按钮
        button_size = (100, 50)
        basic_mode_button = Button(screen=self.screen,position=(30, 215), rect=button_size, text="基本模式",font='fangsong').draw()
        leisure_mode_button = Button(screen=self.screen,position=(30, 315), rect=button_size, text="休闲模式",font='fangsong').draw()
        level_mode_button = Button(screen=self.screen,position=(30, 415), rect=button_size, text="联机模式",font='fangsong').draw()
        
        # 右下角按钮绘制
        button_size = (75, 35)
        chart_button = Button(screen=self.screen,position=(800-75*3, 600-35), rect=button_size, text="排行榜",font='fangsong').draw()
        setting_button = Button(screen=self.screen,position=(800-75*2, 600-35), rect=button_size, text="设置",font='fangsong').draw()
        help_button = Button(screen=self.screen,position=(800-75*1, 600-35), rect=button_size, text="帮助",font='fangsong').draw()

        pygame.display.flip()

        self.buttons = {
            'basic_mode_button': basic_mode_button,
            'leisure_mode_button': leisure_mode_button,
            'level_mode_button': level_mode_button,
            'chart_button': chart_button,
            'setting_button': setting_button,
            'help_button': help_button
        }

    def handle(self):
        # 要返回的状态
        current_page = None
        done = False
        basic_mode_button:Button = self.buttons['basic_mode_button']
        leisure_mode_button:Button = self.buttons['leisure_mode_button']
        level_mode_button:Button = self.buttons['level_mode_button']
        chart_button:Button = self.buttons['chart_button']
        setting_button:Button = self.buttons['setting_button']
        help_button:Button = self.buttons['help_button']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if basic_mode_button.collidepoint(event.pos):
                    print("基本模式按钮 clicked")
                    current_page = Basic_mode(screen=self.screen)
                    pygame.display.set_caption('欢乐连连看-基本模式')
                if leisure_mode_button.collidepoint(event.pos):
                    print("休闲模式按钮 clicked")
                    current_page = Leisure_mode(screen=self.screen)
                    pygame.display.set_caption('欢乐连连看-休闲模式')
                if level_mode_button.collidepoint(event.pos):
                    print("关卡模式按钮 clicked")
                if chart_button.collidepoint(event.pos):
                    print("排行榜按钮 clicked")
                if setting_button.collidepoint(event.pos):
                    print("设置按钮 clicked")
                if help_button.collidepoint(event.pos):
                    print("帮助按钮 clicked")
        
        return (current_page, done)

