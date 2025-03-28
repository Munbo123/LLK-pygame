import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("倒计时进度条")

# 总倒计时时间（秒）
total_time = 10  
# 记录开始时间（单位：毫秒）
start_time = pygame.time.get_ticks()

# 进度条参数
bar_width = 300  # 进度条总宽度
bar_height = 40
bar_x = 250  # 进度条绘制起始坐标
bar_y = 280

font = pygame.font.SysFont(None, 36)

running = True
while running:
    # 计算已过时间（秒）
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  
    # 计算剩余时间
    remaining_time = max(0, total_time - elapsed_time)
    # 计算剩余比例，并据此计算当前进度条宽度
    ratio = remaining_time / total_time
    current_width = int(bar_width * ratio)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    
    # 绘制进度条背景
    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
    # 绘制剩余时间进度条
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))
    
    # 绘制倒计时文本
    text = font.render(f"倒计时: {int(remaining_time)}秒", True, (0, 0, 0))
    screen.blit(text, (bar_x + bar_width // 3, bar_y - 40))
    
    pygame.display.flip()
    
    if remaining_time <= 0:
        running = False
    pygame.time.delay(30)

pygame.quit()
