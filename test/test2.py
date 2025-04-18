import pygame

# 初始化 Pygame
pygame.init()

# 创建主窗口
main_window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Main Window")

# 创建第二个窗口
second_window = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Second Window")

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            second_window = pygame.display.toggle_fullscreen()

# 退出 Pygame
pygame.quit()
