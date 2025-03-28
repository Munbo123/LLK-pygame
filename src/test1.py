import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸和颜色
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption('游戏窗口')
font = pygame.font.Font(None, 36)
button_color = (0, 255, 0)
text_color = (255, 255, 255)
button_rect = pygame.Rect(150, 100, 100, 50)

def show_victory_message():
    """显示胜利消息"""
    message = font.render('you win！', True, text_color)
    message_rect = message.get_rect(center=(200, 150))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # 显示消息2秒

def main():
    running = True
    while running:
        screen.fill((0, 0, 0))  # 清屏
        pygame.draw.rect(screen, button_color, button_rect)
        text = font.render('push me', True, text_color)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    show_victory_message()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
