import requests
import pygame

from pages.MainMenu import Main_menu

# 初始化游戏引擎
pygame.init()

# 设置窗口尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode([screen_width, screen_height])





# 游戏主循环
done = False

# 控制游戏循环每秒帧数
clock = pygame.time.Clock()

# 目前界面状态
current_page = Main_menu(screen=screen)


# 主循环
while not done:
    current_page.draw()
    res = current_page.handle()
    if res[0] != None:
        current_page = res[0]
    done = res[1]
    clock.tick(60)