import pygame
import sys
import os

# 添加正确的导入路径
# 这种方式可以同时支持开发环境和PyInstaller打包后的环境
if getattr(sys, 'frozen', False):
    # 如果是打包后的环境
    application_path = os.path.dirname(sys.executable)
    # 将打包后的路径添加到sys.path
    if os.path.exists(os.path.join(application_path, 'src')):
        sys.path.insert(0, application_path)
    else:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
else:
    # 开发环境
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 现在可以正确导入模块
from src.pages.MainMenu import Main_menu
from src.pages.BasicMode import Basic_mode
from src.pages.LeisureMode import Leisure_mode
from src.pages.SettingPage import Setting_page
from src.pages.NetworkMode import Network_mode
from src.utils import config
# 导入网络通信相关模块
from src.network.network_client import NetworkClient
from src.network.game_session import GameSession



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
    'setting_page': Setting_page,
    'network_mode': Network_mode
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
            # 对于联机模式，每次都创建新的实例
            if next_page_id == 'network_mode':
                # 每次进入联机模式时，都创建新的网络客户端和游戏会话实例
                game_config = config.load_config()
                network_client = NetworkClient(server_url=game_config.get('server_url'))
                game_session = GameSession(network_client)
                
                # 从页面字典中移除旧的联机模式页面(如果存在)
                if 'network_mode' in pages:
                    del pages['network_mode']
                    
                # 创建新的联机模式页面
                pages[next_page_id] = Network_mode(
                    screen=screen, 
                    network_client=network_client,
                    game_session=game_session
                )
                print("创建新的联机模式页面实例")
            # 若其他页面不存在于字典中，则创建该页面并添加到字典中
            elif next_page_id not in pages:
                pages[next_page_id] = page_classes[next_page_id](screen=screen)
                print(f"创建新页面: {next_page_id}")
            else:
                print(f"页面 {next_page_id} 已存在，使用现有实例,并重新初始化")
                # 重新初始化页面
                pages[next_page_id].__init__(screen=screen)
                
            # 切换到请求的页面
            current_page_id = next_page_id
            current_page = pages[current_page_id]
            
            # 更新窗口标题
            if current_page_id == 'main_menu':
                pygame.display.set_caption('欢乐连连看')
            elif current_page_id == 'basic_mode':
                pygame.display.set_caption('欢乐连连看-基本模式')
            elif current_page_id == 'leisure_mode':
                pygame.display.set_caption('欢乐连连看-休闲模式')
            elif current_page_id == 'setting_page':
                pygame.display.set_caption('欢乐连连看-设置')
            elif current_page_id == 'network_mode':
                pygame.display.set_caption('欢乐连连看-联机模式')
        else:
            print(f"无效的页面标识符: {next_page_id}")
    
    clock.tick(60)

# 在程序退出前关闭所有可能存在的网络连接
if 'network_mode' in pages:
    # 获取联机模式页面中的网络客户端
    network_mode:Network_mode = pages['network_mode']
    if hasattr(network_mode, 'network_client') and network_mode.network_client.is_connected():
        network_mode.network_client.stop()


