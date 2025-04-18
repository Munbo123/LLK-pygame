import pygame

from pages.MainMenu import Main_menu
from pages.BasicMode import Basic_mode
from pages.LeisureMode import Leisure_mode
from pages.SettingPage import Setting_page

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

# 创建页面字典，使用懒加载方式，加快启动速度，初始时只加载主菜单
pages = {
    'main_menu': Main_menu(screen=screen)
}

# 定义有效页面类型映射
page_classes = {
    'main_menu': Main_menu,
    'basic_mode': Basic_mode,
    'leisure_mode': Leisure_mode,
    'setting_page': Setting_page
}

# 当前页面的标识符
current_page_id = 'main_menu'
# 当前页面对象
current_page = pages[current_page_id]

# 主循环
while not done:
    current_page.draw()
    res = current_page.handle()
    
    next_page_id, done = res
    
    # 如果有页面切换请求，且页面标识符有效
    if next_page_id:
        # 检查页面标识符是否合法
        if next_page_id in page_classes:
            # 若页面不存在于字典中，则创建该页面并添加到字典中
            if next_page_id not in pages:
                pages[next_page_id] = page_classes[next_page_id](screen=screen)
                print(f"创建新页面: {next_page_id}")
                
            # 切换到请求的页面，并初始化该页面
            current_page_id = next_page_id
            current_page = pages[current_page_id]
            current_page.__init__(screen=screen)

            # 更新窗口标题
            if current_page_id == 'main_menu':
                pygame.display.set_caption('欢乐连连看')
            elif current_page_id == 'basic_mode':
                pygame.display.set_caption('欢乐连连看-基本模式')
            elif current_page_id == 'leisure_mode':
                pygame.display.set_caption('欢乐连连看-休闲模式')
        else:
            print(f"无效的页面标识符: {next_page_id}")
    
    clock.tick(60)


