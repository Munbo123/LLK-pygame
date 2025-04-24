import pygame
import random
import time

from src.logic.matrix_logic import Matrix
from src.logic.graph_logic import Graph
from src.components.Button import Button
from src.components.ProgressBar import Progress_bar
from src.utils.image_processor import process_fruit_sheet  # 导入新的工具函数
from src.utils.config import load_config

game_background_path = r"./assets/fruit_bg.bmp"
sheet_path = r"./assets/fruit_element.bmp"
mask_path = r"./assets/fruit_mask.bmp"

class Basic_mode:
    def __init__(self,screen:pygame.Surface):
        # 读取配置信息
        config = load_config()
        self.row = config.get("rows", 10)  # 默认行数为10
        self.col = config.get("columns", 10)  # 默认列数为10

        # 屏幕对象及其宽高
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # 游戏背景
        self.background = pygame.image.load(game_background_path).convert_alpha()
        
        # 初始化按钮
        self.init_buttons()

        # 绘制进度条
        self.progress_bar = Progress_bar(screen=screen,total_time=300) # 总时间300秒

        # 加载水果图集和遮罩图像
        self.fruit_images = process_fruit_sheet(sheet_path, mask_path)  # 使用导入的工具函数
        # 根据水果图像创建游戏地图
        self.game_map = Graph(row=self.row, col=self.col, elements=self.fruit_images)

        # 设置所有元素为不可视状态
        self.set_all_status('unvisible')
        
        # 初始化已选水果集合
        self.choosen_fruit = set()
        
        # 初始化动画列表，用于存储消除动画的路径
        # 每个动画包含：path(路径点列表)、color(绘制颜色)、expire(存活时间)
        self.animations = []
        
        # 记录上一帧的时间，用于计算时间差
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        # 添加自动消除状态标志
        self.auto_eliminating = False

    def init_buttons(self):
        # 定义按钮尺寸
        main_button_size = (100, 50)
        other_button_size = (75, 35)
        self.all_buttons = []

        # 基本游戏功能按钮，包含开始游戏，暂停游戏，提示，重排，位于屏幕右侧位置，右边距约20像素，竖向排列，按钮之间间距约20像素
        # 右下角按钮，包含设置，帮助，按照竖向排列，紧靠右下角

        # 开始按钮
        self.start_button = Button(screen=self.screen,position=(800-100-20, 20), rect=main_button_size, text="开始游戏",font='fangsong')
        self.all_buttons.append(self.start_button)
        # 暂停按钮
        self.pause_button = Button(screen=self.screen,position=(800-100-20, 20+50+20), rect=main_button_size, text="暂停游戏",font='fangsong')
        self.all_buttons.append(self.pause_button)
        # 提示按钮
        self.promote_button = Button(screen=self.screen,position=(800-100-20, 20+50+20+50+20), rect=main_button_size, text="提示",font='fangsong')
        self.all_buttons.append(self.promote_button)
        # 重排按钮
        self.rearrange_button = Button(screen=self.screen,position=(800-100-20, 20+50+20+50+20+50+20), rect=main_button_size, text="重排",font='fangsong')
        self.all_buttons.append(self.rearrange_button)
        # 设置按钮
        self.setting_button = Button(screen=self.screen,position=(800-75, 600-35), rect=other_button_size, text="设置",font='fangsong')
        self.all_buttons.append(self.setting_button)
        # 自动按钮
        self.auto_eliminate_button = Button(screen=self.screen,position=(800-75, 600-35-35-20), rect=other_button_size, text="自动",font='fangsong')
        self.all_buttons.append(self.auto_eliminate_button)
        # 返回按钮，位于左下角
        self.return_button = Button(screen=self.screen,position=(20, 600-35), rect=other_button_size, text="返回",font='fangsong')
        self.all_buttons.append(self.return_button)


        self.pause_button.disable_button() # 暂停按钮默认禁用
        self.promote_button.disable_button() # 提示按钮默认禁用
        self.rearrange_button.disable_button() # 重排按钮默认禁用

    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(self.background, (0, 0))

        # 绘制按钮
        for button in self.all_buttons:
            button.draw()
        
        # 绘制进度条
        if self.progress_bar:
            self.progress_bar.draw()
        
        # 定义游戏矩阵的起始坐标
        self.game_matrix_x = 20
        self.game_matrix_y = 50
        
        #获取每个元素的长宽
        element_width, element_height = self.game_map.get_elements_width(), self.game_map.get_elements_height()

        if self.game_map is not None:
            # 绘制游戏界面时，使用水果图像
            for row in range(self.game_map.get_row()):
                for col in range(self.game_map.get_col()):
                    # 获取水果元素和其属性
                    fruit = self.game_map.get_cell(row,col)
                    index,status = fruit['index'],fruit['status']
                    fruit_suface = self.game_map.get_elements(index)
                    pos_x = self.game_matrix_x + col * element_width
                    pos_y = self.game_matrix_y + row * element_height

                    # 根据元素的status属性绘制水果图像
                    if status == 'normal':
                        self.screen.blit(fruit_suface, (pos_x, pos_y))
                    elif status in ['choosen','eliminating']:
                        # 绘制红色边框
                        selected_rect = pygame.Rect((pos_x, pos_y), (40, 40))
                        pygame.draw.rect(self.screen, (255, 0, 0), selected_rect, 2)
                        # 绘制水果图像
                        self.screen.blit(fruit_suface, (pos_x, pos_y))
                    elif status == 'promote':
                        # 绘制黄色边框
                        selected_rect = pygame.Rect((pos_x, pos_y), (40, 40))
                        pygame.draw.rect(self.screen, (255, 255, 0), selected_rect, 4)
                        # 绘制水果图像
                        self.screen.blit(fruit_suface, (pos_x, pos_y))
                    elif status == 'disabled':
                        # 绘制水果图像（和normal不同的是后续handle中不会对点击事件做出反应，但还是得渲染）
                        self.screen.blit(fruit_suface, (pos_x, pos_y))
                    elif status in ['unvisible','eliminated']:
                        # 不渲染
                        pass

        # 绘制所有当前动画效果
        for animation in self.animations:
            animation_type = animation.get('type', 'path')  # 默认为路径类型
            
            if animation_type == 'path':
                # 绘制路径动画
                path = animation['path']
                color = animation['color']
                
                # 只有至少有两个点的路径才能绘制
                if len(path) >= 2:
                    # 绘制路径连线
                    for i in range(len(path) - 1):
                        start_row, start_col = path[i]
                        end_row, end_col = path[i + 1]
                        
                        # 计算像素坐标
                        start_x = self.game_matrix_x + start_col * element_width + element_width // 2
                        start_y = self.game_matrix_y + start_row * element_height + element_height // 2
                        end_x = self.game_matrix_x + end_col * element_width + element_width // 2
                        end_y = self.game_matrix_y + end_row * element_height + element_height // 2
                        
                        # 绘制路径线
                        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 3)
                        
                        # 在路径点绘制小圆点
                        pygame.draw.circle(self.screen, (0, 0, 255), (start_x, start_y), 5)
                    
                    # 绘制最后一个点
                    last_row, last_col = path[-1]
                    last_x = self.game_matrix_x + last_col * element_width + element_width // 2
                    last_y = self.game_matrix_y + last_row * element_height + element_height // 2
                    pygame.draw.circle(self.screen, (0, 0, 255), (last_x, last_y), 5)
                    
            elif animation_type == 'victory_text':
                # 绘制胜利文字动画
                text = animation['text']
                color = animation['color']
                font_size = animation['font_size']
                
                # 创建字体对象
                font = pygame.font.SysFont('fangsong', font_size)
                text_surface = font.render(text, True, color)
                
                # 计算文字的位置（居中显示）
                text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                
                # 绘制文字
                self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def handle(self):
        next_page_id, done = None, False  # 修改变量名，使其更明确表示返回的是页面 ID,默认不切换

        # 计算时间增量
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # 更新所有动画的存活时间，移除过期的动画
        i = 0
        while i < len(self.animations):
            self.animations[i]['expire'] -= delta_time
            if self.animations[i]['expire'] <= 0:
                # 动画结束时，如果有回调函数，则执行
                animation = self.animations[i]
                if animation['callback'] is not None:
                    animation['callback'](*animation['callback_args'])
                # 移除过期动画
                self.animations.pop(i)
            else:
                i += 1
        
        # 如果所有动画已结束且处于自动消除状态，执行下一次自动消除
        if self.auto_eliminating and len(self.animations) == 0:
            self.perform_single_auto_elimination()

        # 从game_map中获取行列数，元素长宽，计算矩阵的范围
        rect = pygame.Rect(self.game_matrix_x, self.game_matrix_y, self.game_map.get_col()*self.game_map.get_elements_width(), self.game_map.get_row()*self.game_map.get_elements_height())
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 开始按钮
                if self.start_button.collidepoint(event.pos):
                    next_page_id, done = self.start_button_event()
                # 暂停按钮
                elif self.pause_button.collidepoint(event.pos):
                    next_page_id, done = self.pause_button_event()
                # 提示按钮
                elif self.promote_button.collidepoint(event.pos):
                    next_page_id, done = self.promote_button_event()
                # 重排按钮
                elif self.rearrange_button.collidepoint(event.pos):
                    next_page_id, done = self.rearrange_button_event()
                # 设置按钮
                elif self.setting_button.collidepoint(event.pos):
                    next_page_id, done = self.setting_button_event()
                # 自动按钮
                elif self.auto_eliminate_button.collidepoint(event.pos):
                    next_page_id, done = self.auto_eliminate_button_event()
                # 返回按钮
                elif self.return_button.collidepoint(event.pos):
                    next_page_id, done = self.return_button_event()
                # 判断鼠标点击位置是否是水果元素内
                elif rect.collidepoint(event.pos):
                    # print(f"现在点击了位置：{event.pos}")
                    row = int((event.pos[1]-self.game_matrix_y) / self.game_map.get_elements_height()) # 选中行数
                    col = int((event.pos[0]-self.game_matrix_x) / self.game_map.get_elements_width()) # 选中列数
                    print(f"现在点击了行：{row}，列：{col}")
                    # 获取矩阵元素
                    fruit = self.game_map.get_cell(row,col)
                    index,status = fruit['index'],fruit['status']
                    if status == 'normal':
                        # 如果当前元素是正常状态，则选中它
                        self.game_map.set_status(row,col,'choosen')
                        self.choosen_fruit.add((row,col))
                    elif status == 'choosen':
                        # 如果当前元素已经被选中，则取消选中
                        self.game_map.set_status(row,col,'normal')
                        self.choosen_fruit.remove((row,col))
                    elif status == 'promote':
                        # 如果当前元素是提示状态，则改成选中状态，并添加到选中集合
                        self.game_map.set_status(row,col,'choosen')
                        self.choosen_fruit.add((row,col))
                    elif status == 'eliminating':
                        # 如果当前元素正在消除状态，则不做任何操作
                        pass
                    else:
                        print(f"非法状态{status}")

                    # 如果选中元素数量为2，则判断是否可以消除
                    if len(self.choosen_fruit) == 2:
                        fruit1, fruit2 = list(self.choosen_fruit)
                        self.choosen_fruit.clear()  # 清空选中集合
                        # 获取消除路径
                        path = self.game_map.is_eliminable(fruit1[0], fruit1[1], fruit2[0], fruit2[1])
                        
                        if path:
                            # 停止自动消除状态
                            if self.auto_eliminating:
                                self.auto_eliminating = False
                                self.auto_eliminate_button.text = "自动"
                                self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
                                self.auto_eliminate_button.draw()
                            
                            # 移除所有提示动画
                            self.remove_promote_animations()
                            # 重置所有提示状态
                            self.reset_promote_status()
                            
                            # 创建一个消除回调函数用于动画结束后消除元素
                            def eliminate_callback(row1, col1, row2, col2):
                                self.game_map.eliminate_cell(row1, col1)
                                self.game_map.eliminate_cell(row2, col2)
                                
                                # 检查是否已经消除所有元素
                                if self.game_map.get_left_elements() == 0:
                                    # 游戏胜利，添加胜利动画
                                    self.show_victory_animation()
                                
                            # 添加消除动画，包含回调函数，持续时间为1秒
                            self.add_elimination_animation(
                                path, 
                                color=(0, 255, 0), 
                                expire_time=1.0,
                                callback=eliminate_callback,
                                callback_args=(fruit1[0], fruit1[1], fruit2[0], fruit2[1]),
                                animation_type='elimination'
                            )
                            
                            # 让元素在动画期间显示'eliminating'状态，以保持红框显示
                            self.game_map.set_status(fruit1[0], fruit1[1], 'eliminating')
                            self.game_map.set_status(fruit2[0], fruit2[1], 'eliminating')
                        else:
                            # 取消选中状态
                            self.game_map.set_status(fruit1[0], fruit1[1], 'normal')
                            self.game_map.set_status(fruit2[0], fruit2[1], 'normal')


        return next_page_id, done

    def start_button_event(self):
        if self.start_button.is_button_enabled():
            print("开始游戏按钮 clicked")
            self.start_button.disable_button()
            
            # 重新初始化游戏矩阵，生成新的地图
            if self.game_map.get_col()*self.game_map.get_row() != self.game_map.get_left_elements():
                self.game_map = Graph(row=self.row, col=self.col, elements=self.fruit_images)
            
            # 将所有元素设置为显示状态
            self.set_all_status('normal')
            
            # 清空选中水果集合和动画列表
            self.choosen_fruit.clear()
            self.animations.clear()
            
            if self.progress_bar:
                self.progress_bar.start()
                self.progress_bar.reset()
            # 启用提示按钮,启用暂停按钮,启用重排按钮
            self.pause_button.enable_button()
            self.promote_button.enable_button()
            self.rearrange_button.enable_button()
        else:
            print("开始游戏按钮 clicked, but it is disabled")
        
        # 返回next_page_id和done,由于没有页面切换，所以仍然是None和False
        return None, False

    def pause_button_event(self):
        if self.pause_button.is_button_enabled():
            print("暂停/继续游戏按钮 clicked")
            if self.progress_bar.progress_running:
                self.progress_bar.pause()
                self.pause_button.text = "继续游戏"
                self.pause_button.button_text = self.pause_button.button_font.render(self.pause_button.text, True, (0, 0, 0))
                self.pause_button.draw()
                self.set_all_status('unvisible')

                # 禁用提示按钮,禁用重排按钮
                self.promote_button.disable_button()
                self.rearrange_button.disable_button()
            else:
                self.progress_bar.start()
                self.pause_button.text = "暂停游戏"
                self.pause_button.button_text = self.pause_button.button_font.render(self.pause_button.text, True, (0, 0, 0))
                self.pause_button.draw()
                self.set_all_status('normal')

                # 启用提示按钮,启用重排按钮
                self.promote_button.enable_button()
                self.rearrange_button.enable_button()
        else:
            print("暂停/继续游戏按钮 clicked, but it is disabled")
        
        # 返回next_page_id和done,由于没有页面切换，所以仍然是None和False
        return None, False

    def promote_button_event(self):
        if self.promote_button.is_button_enabled():
            print("提示按钮 clicked")
            """使用game_map的promote函数寻找可消除的元素对，并标记为提示状态"""
            # 首先重置所有提示状态
            self.reset_promote_status()
            
            # 移除所有现有的提示动画
            self.remove_promote_animations()
            
            # 寻找可消除的元素对
            path = self.game_map.promote()
            
            if path and len(path) >= 2:
                # 获取起点和终点
                start_row, start_col = path[0]
                end_row, end_col = path[-1]
                
                # 将这两个元素设置为promote状态
                self.game_map.set_status(start_row, start_col, 'promote')
                self.game_map.set_status(end_row, end_col, 'promote')
                
                # 添加提示动画，过期时间设为无穷大（float('inf')）
                self.add_elimination_animation(
                    path, 
                    color=(255, 255, 0), 
                    expire_time=float('inf'),
                    animation_type='promote'  # 标记为提示动画类型
                )
            else:
                # 如果没有找到可消除的元素对，显示提示信息
                print("没有可以消除的元素对")
        else:
            print("提示按钮 clicked, but it is disabled")
        
        # 返回next_page_id和done,由于没有页面切换，所以仍然是None和False
        return None, False
    
    def rearrange_button_event(self):
        if self.rearrange_button.is_button_enabled(): 
            print("重排按钮 clicked")
            """重排矩阵中的元素"""
            # 调用game_map的rearrange_matrix方法
            self.game_map.rearrange_matrix()
            
            # 清空选中水果集合
            self.choosen_fruit.clear()
            
            # 清空动画列表
            self.animations.clear()
            self.set_all_status('normal')
        else:
            print("重排按钮 clicked, but it is disabled")
        
        # 返回next_page_id和done,由于没有页面切换，所以仍然是None和False
        return None, False

    def setting_button_event(self):
        print("设置按钮 clicked")

        return 'setting_page', False

    def auto_eliminate_button_event(self):
        print("自动按钮 clicked")
        
        # 检查是否处于游戏进行中的状态（只有游戏开始后才能使用帮助功能）
        if not self.pause_button.is_button_enabled():
            print("游戏未开始或已暂停，无法使用帮助功能")
            return None, False
            
        # 检查剩余元素数量，如果只剩下两个或更少的元素，则不执行自动消除
        if self.game_map.get_left_elements() <= 2:
            print("只剩下最后两个元素，无法继续自动消除")
            return None, False
            
        # 切换自动消除状态
        self.auto_eliminating = not self.auto_eliminating
        
        # 根据当前状态更新帮助按钮文本
        if self.auto_eliminating:
            self.auto_eliminate_button.text = "停止自动"
            self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
            self.auto_eliminate_button.draw()
            
            # 清空已选择的元素
            self.choosen_fruit.clear()
            
            # 开始一次自动消除，后续的自动消除会在handle方法中进行
            self.perform_single_auto_elimination()
        else:
            self.auto_eliminate_button.text = "自动"
            self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
            self.auto_eliminate_button.draw()
            print("已停止自动消除")
        
        return None, False
    
    def return_button_event(self):
        print("返回按钮 clicked")
        # 返回切换页面请求
        return 'main_menu', False

        
    def start_auto_elimination(self):
        """开始自动消除流程，会一直消除直到只剩下最后两个元素"""
        # 如果只剩下两个或者更少的元素，或者游戏暂停，则停止自动消除
        if self.game_map.get_left_elements() <= 2 or not self.pause_button.is_button_enabled():
            return
            
        # 找到一对可以消除的元素
        path = self.game_map.promote()
        
        # 如果找不到可消除的元素，尝试重排
        if not path or len(path) < 2:
            print("没有找到可消除的元素，尝试重排")
            self.game_map.rearrange_matrix()
            # 重排后再次尝试自动消除
            pygame.time.delay(100)  # 短暂延迟，使玩家能看到重排效果
            self.start_auto_elimination()
            return
            
        # 获取要消除的两个元素坐标
        start_row, start_col = path[0]
        end_row, end_col = path[-1]
        
        # 创建消除回调函数，在动画结束后继续消除下一对
        def auto_eliminate_callback(row1, col1, row2, col2):
            # 消除当前元素
            self.game_map.eliminate_cell(row1, col1)
            self.game_map.eliminate_cell(row2, col2)
            
            # 检查是否已经消除所有元素或只剩下最后两个元素
            if self.game_map.get_left_elements() <= 2:
                print("只剩下最后两个元素，自动消除停止")
                
                # 如果完全消除了所有元素，显示胜利动画
                if self.game_map.get_left_elements() == 0:
                    self.show_victory_animation()
            else:
                # 递归调用，继续消除下一对元素
                self.start_auto_elimination()
        
        # 设置元素为消除中状态
        self.game_map.set_status(start_row, start_col, 'eliminating')
        self.game_map.set_status(end_row, end_col, 'eliminating')
        
        # 添加消除动画，使用较短的动画时间
        self.add_elimination_animation(
            path,
            color=(0, 255, 0),
            expire_time=0.1,  # 动画时间设为0.1秒，快速显示
            callback=auto_eliminate_callback,
            callback_args=(start_row, start_col, end_row, end_col),
            animation_type='elimination'
        )

    def perform_single_auto_elimination(self):
        """执行一次自动消除操作"""
        # 如果已不再自动消除状态，或只剩下两个或更少的元素，或游戏暂停，则停止自动消除
        if not self.auto_eliminating or self.game_map.get_left_elements() <= 2 or not self.pause_button.is_button_enabled():
            # 如果不是自动消除状态，重置帮助按钮
            if not self.auto_eliminating:
                self.auto_eliminate_button.text = "自动"
                self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
                self.auto_eliminate_button.draw()
            return
            
        # 找到一对可以消除的元素
        path = self.game_map.promote()
        
        # 如果找不到可消除的元素，尝试重排
        if not path or len(path) < 2:
            print("没有找到可消除的元素，尝试重排")
            self.game_map.rearrange_matrix()
            self.set_all_status('normal')
            # 重排后稍后再次尝试自动消除
            return
            
        # 移除所有提示动画
        self.remove_promote_animations()
        
        # 获取要消除的两个元素坐标
        start_row, start_col = path[0]
        end_row, end_col = path[-1]
        
        # 创建消除回调函数，在动画结束后触发下一次自动消除
        def auto_eliminate_callback(row1, col1, row2, col2):
            # 消除当前元素
            self.game_map.eliminate_cell(row1, col1)
            self.game_map.eliminate_cell(row2, col2)
            
            # 检查是否已经消除所有元素
            if self.game_map.get_left_elements() == 0:
                # 游戏胜利，添加胜利动画
                self.show_victory_animation()
                # 关闭自动消除状态
                self.auto_eliminating = False
            elif self.game_map.get_left_elements() <= 2:
                # 只剩最后两个元素，停止自动消除
                print("只剩下最后两个元素，自动消除停止")
                self.auto_eliminating = False
                self.auto_eliminate_button.text = "自动"
                self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
                self.auto_eliminate_button.draw()
        
        # 设置元素为消除中状态
        self.game_map.set_status(start_row, start_col, 'eliminating')
        self.game_map.set_status(end_row, end_col, 'eliminating')
        
        # 添加消除动画，使用较短的动画时间
        self.add_elimination_animation(
            path,
            color=(0, 255, 0),
            expire_time=0.1,  # 动画时间设为0.1秒，快速显示
            callback=auto_eliminate_callback,
            callback_args=(start_row, start_col, end_row, end_col),
            animation_type='elimination'
        )

    def add_elimination_animation(self, path, color=(0, 255, 0), expire_time=1, callback=None, callback_args=None, animation_type='elimination'):
        """
        添加一个新的消除动画到动画列表中
        
        参数:
            path: 路径点列表，通常由 game_map.is_eliminable 方法返回
            color: 绘制路径的颜色，默认为绿色
            expire_time: 动画存活时间，单位为秒，默认为1秒
            callback: 动画结束时调用的回调函数，默认为None
            callback_args: 回调函数的参数，默认为None
            animation_type: 动画子类型，用于标识不同用途的路径动画，如消除、提示等
        """
        # 创建新的动画字典
        animation = {
            'path': path,
            'color': color,
            'expire': expire_time,
            'callback': callback,
            'callback_args': callback_args,
            'type': 'path',  # 基本类型为路径动画
            'animation_type': animation_type  # 动画子类型（elimination, promote等）
        }
        
        # 添加到动画列表
        self.animations.append(animation)
        
    def set_all_status(self, status):
        """重置所有元素的状态"""
        for row in range(self.game_map.get_row()):
            for col in range(self.game_map.get_col()):
                # 跳过已消除的元素
                if self.game_map.get_cell(row, col)['status'] != 'eliminated':
                    self.game_map.set_status(row, col, status)
                    

    def remove_promote_animations(self):
        """移除所有提示动画"""
        i = 0
        while i < len(self.animations):
            if self.animations[i].get('type') == 'path' and self.animations[i].get('animation_type') == 'promote':
                self.animations.pop(i)
            else:
                i += 1
    
    def reset_promote_status(self):
        """重置所有元素的promote状态为normal"""
        for row in range(self.game_map.get_row()):
            for col in range(self.game_map.get_col()):
                if self.game_map.get_cell(row, col)['status'] == 'promote':
                    self.game_map.set_status(row, col, 'normal')
                    

    def show_victory_animation(self):
        """显示胜利动画，在游戏界面中央显示胜利提示，并重置游戏状态"""
        
        # 创建一个胜利提示显示的回调，在显示3秒后执行
        def victory_callback():
            # 禁用游戏按钮
            self.pause_button.disable_button()
            self.promote_button.disable_button()
            self.rearrange_button.disable_button()
            
            # 禁用自动消除按钮
            if self.auto_eliminating:
                self.auto_eliminating = False
                self.auto_eliminate_button.text = "自动"
                self.auto_eliminate_button.button_text = self.auto_eliminate_button.button_font.render(self.auto_eliminate_button.text, True, (0, 0, 0))
                
            # 启用开始按钮，允许重新开始游戏
            self.start_button.enable_button()
            
            # 暂停计时器
            if self.progress_bar:
                self.progress_bar.pause()
        
        # 创建一个胜利动画，在3秒后自动消失
        self.add_victory_text_animation(3.0, victory_callback)
    
    def add_victory_text_animation(self, expire_time=3.0, callback=None):
        """添加胜利文字动画，在屏幕中央显示'胜利!'文字"""
        # 创建一个新的动画类型
        animation = {
            'type': 'victory_text',  # 胜利文字动画类型
            'expire': expire_time,
            'callback': callback,
            'callback_args': (),
            'text': '胜利!',
            'color': (255, 0, 0),  # 红色
            'font_size': 72
        }
        
        # 添加到动画列表
        self.animations.append(animation)
    

