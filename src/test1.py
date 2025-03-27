import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口大小和标题
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("游戏暂停功能示例")

# 定义颜色
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# 定义字体
font = pygame.font.Font(None, 36)

# 定义按钮类
class Button:
    def __init__(self, text, pos, size):
        self.rect = pygame.Rect(pos, size)
        self.text = text
        self.color = GRAY

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 创建“暂停”和“继续游戏”按钮
pause_button = Button("暂停", (700, 50), (80, 40))
resume_button = Button("继续游戏", (350, 250), (100, 50))

# 游戏状态变量
game_paused = False

# 主循环
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if not game_paused:
                if pause_button.is_clicked(mouse_pos):
                    game_paused = True
            else:
                if resume_button.is_clicked(mouse_pos):
                    game_paused = False

    if game_paused:
        # 绘制“继续游戏”按钮
        resume_button.draw(screen)
        # 在暂停状态下，不处理其他游戏元素的事件
    else:
        # 绘制“暂停”按钮
        pause_button.draw(screen)
        # 更新和绘制其他游戏元素
        # ...

    pygame.display.flip()

pygame.quit()
sys.exit()
