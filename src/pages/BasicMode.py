import pygame
import random
import time

from components.Button import Button
from components.ProgressBar import Progress_bar

game_background = pygame.image.load(r"C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\res\连连看游戏综合实践\任务5-界面设计\实验素材\fruit_bg.bmp")

class Basic_mode:
    def __init__(self,screen:pygame.Surface):
        # 屏幕对象
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        # 游戏背景
        self.matrix = None
        self.init_buttons()
        self.total_time = 300 # 总时间默认300秒
        # 绘制进度条
        self.progress_bar = Progress_bar(screen=screen)
        self.progress_bar.set_total_time(self.total_time)

        '''
        游戏地图区域
        (1) 游戏地图起始点 (50,50)，单位像素。
        (2) 游戏地图：10 行，16 列。
        (3) 每张图片大小：40*40，单位像素。
        (4) 游戏地图中包含 16 种图片。(先以不同颜色的背景代替)
        '''
        self.fruit_sheet = pygame.image.load(r"C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\res\连连看游戏综合实践\任务5-界面设计\实验素材\fruit_element.bmp").convert()
        self.fruit_mask = pygame.image.load(r"C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\res\连连看游戏综合实践\任务5-界面设计\实验素材\fruit_mask.bmp").convert()
        # 将 mask.bmp 转换为透明的 Surface
        self.processed_fruit_sheet = pygame.Surface(self.fruit_sheet.get_size(), pygame.SRCALPHA)  # 创建一个透明的 Surface
        width,height = self.fruit_sheet.get_size()
        for x in range(width):
            for y in range(height):
                # 获取像素颜色
                pixel_color = self.fruit_sheet.get_at((x, y))
                mask_color = self.fruit_mask.get_at((x, y))
                # 如果 mask.bmp 中的像素颜色为白色，则设置为透明
                if mask_color != (255, 255, 255, 255):
                    self.processed_fruit_sheet.set_at((x, y), (0, 0, 0, 0))
                else:
                    self.processed_fruit_sheet.set_at((x, y), pixel_color)
        # 将处理后的水果图集切分为10个水果图像
        self.fruit_images = []
        for i in range(10):
            rect = pygame.Rect(0, i * 40, 40, 40)
            self.fruit_images.append(self.processed_fruit_sheet.subsurface(rect).copy())  # 注意用 copy() 得到独立的 Surface

        # # 将切好的图片保存到当前目录
        # cnt = 0
        # for fruit_image in self.fruit_images:
        #     pygame.image.save(fruit_image, os.path.join(os.getcwd(), f"fruit_{cnt}.png"))
        #     cnt += 1

    def init_buttons(self):
        # 绘制按钮
        main_button_size = (100, 50)
        other_button_size = (75, 35)
        # 基本游戏功能按钮，包含开始游戏，暂停游戏，提示，重排，位于屏幕右侧位置，右边距约20像素，竖向排列，按钮之间间距约20像素
        start_button = Button(screen=self.screen,position=(800-100-20, 20), rect=main_button_size, text="开始游戏",font='fangsong')
        pause_button = Button(screen=self.screen,position=(800-100-20, 20+50+20), rect=main_button_size, text="暂停游戏",font='fangsong')
        hint_button = Button(screen=self.screen,position=(800-100-20, 20+50+20+50+20), rect=main_button_size, text="提示",font='fangsong')
        restart_button = Button(screen=self.screen,position=(800-100-20, 20+50+20+50+20+50+20), rect=main_button_size, text="重排",font='fangsong')
        # 右下角按钮绘制，包含设置，帮助，按照竖向排列，紧靠右下角
        setting_button = Button(screen=self.screen,position=(800-75, 600-35), rect=other_button_size, text="设置",font='fangsong')
        help_button = Button(screen=self.screen,position=(800-75, 600-35-35-20), rect=other_button_size, text="开挂",font='fangsong')


        pause_button.disable_button() # 暂停按钮默认禁用
        hint_button.disable_button() # 提示按钮默认禁用
        restart_button.disable_button() # 重排按钮默认禁用

        self.buttons = {
            'start_button': start_button,
            'pause_button': pause_button,
            'hint_button': hint_button,
            'restart_button': restart_button,
            'setting_button': setting_button,
            'help_button': help_button
        }
       
    def generate_game_matrix(self):
        # 随机生成游戏地图
        self.row = 10
        self.col = 16
        # self.row = 2
        # self.col = 4
        self.left_fruit = self.row*self.col # 剩余水果数量
        self.game_matrix_x = 20
        self.game_matrix_y = 50
        self.choosen_fruit = set() # 选中元素的坐标集合
        self.matrix = [[None]*self.col for _ in range(self.row)] # 10行16列的矩阵

        fruits_temp = [] # 临时存储水果图像索引
        for i in range(self.row*self.col//2):
            # 同时生成两个相同的水果图像索引
            add_fruit = random.randint(0,len(self.fruit_images)-1)
            fruits_temp.append(add_fruit)
            fruits_temp.append(add_fruit)
        # 打乱水果图像索引
        random.shuffle(fruits_temp)
  
        # 将水果图像索引填入矩阵
        cnt = 0
        for i in range(self.row):
            for j in range(self.col):
                # 随机选择水果图像
                fruit_image_index = fruits_temp[cnt]
                cnt += 1
                # 计算水果图像在屏幕上的位置
                pos_x = self.game_matrix_x + j * 40
                pos_y = self.game_matrix_y + i * 40
                # 水果图像rect
                rect = self.fruit_images[fruit_image_index]
                self.matrix[i][j] = {
                    'rect' : rect,
                    'pos' : (pos_x, pos_y),
                    'index' : fruit_image_index,
                    'status' : 'normal'       # 是否被选中
                }
        
    def draw(self):
        # 清屏
        self.screen.fill((255, 255, 255))

        # 绘制背景
        self.screen.blit(game_background, (0, 0))

        # 绘制按钮
        start_button:Button = self.buttons['start_button']
        pause_button:Button = self.buttons['pause_button']
        hint_button:Button = self.buttons['hint_button']
        restart_button:Button = self.buttons['restart_button']
        setting_button:Button = self.buttons['setting_button']
        help_button:Button = self.buttons['help_button']
        
        start_button.draw()
        pause_button.draw()
        hint_button.draw()
        restart_button.draw()
        setting_button.draw()
        help_button.draw()

        
        # 绘制进度条
        if self.progress_bar:
            self.progress_bar.draw()
        

        # 绘制游戏界面时，使用水果图像
        if self.matrix:
            # 绘制游戏界面时，使用水果图像
            for row in range(len(self.matrix)):
                for col in range(len(self.matrix[0])):
                    fruit = self.matrix[row][col]
                    # 如果水果元素不为空，则绘制水果图像
                    if fruit != None:
                        rect,pos,status = fruit['rect'],fruit['pos'],fruit['status']                     
                        if status == 'choosen':
                            # 绘制红色边框
                            selected_rect = pygame.Rect(pos, (40, 40))
                            pygame.draw.rect(self.screen, (255, 0, 0), selected_rect, 2)
                            # 绘制水果图像
                            self.screen.blit(rect, pos)
                        elif status == 'hint':
                            # 绘制黄色边框
                            selected_rect = pygame.Rect(pos, (40, 40))
                            pygame.draw.rect(self.screen, (255, 255, 0), selected_rect, 4)
                            # 绘制水果图像
                            self.screen.blit(rect, pos)
                        elif status == 'normal':
                            # 绘制水果图像
                            self.screen.blit(rect, pos)
                        elif status == 'disabled':
                            # 绘制水果图像（和normal不同的是后续handle中不会对点击事件做出反应，但还是得渲染）
                            self.screen.blit(rect, pos)
                        elif status == 'unvisible':
                            # 不渲染
                            pass
        
        pygame.display.flip()

    def handle(self):
        done,current_page = False,None
        start_button:Button = self.buttons['start_button'] 
        pause_button:Button = self.buttons['pause_button']
        hint_button:Button = self.buttons['hint_button']
        restart_button:Button = self.buttons['restart_button']
        setting_button:Button = self.buttons['setting_button']
        help_button:Button = self.buttons['help_button']
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 判断鼠标点击位置是否在按钮区域内
                if start_button.collidepoint(event.pos):
                    if start_button.is_button_enabled():
                        print("开始游戏按钮 clicked")
                        self.generate_game_matrix()
                        start_button.disable_button()
                        if self.progress_bar:
                            self.progress_bar.start()
                            self.progress_bar.reset()
                        # 启用提示按钮,启用暂停按钮,启用重排按钮
                        pause_button.enable_button()
                        hint_button.enable_button()
                        restart_button.enable_button()
                    else:
                        print("开始游戏按钮 clicked, but it is disabled")
                elif pause_button.collidepoint(event.pos):
                    if pause_button.is_button_enabled():
                        print("暂停/继续游戏按钮 clicked")
                        if self.progress_bar.progress_running:
                            self.progress_bar.pause()
                            pause_button.text = "继续游戏"
                            pause_button.button_text = pause_button.button_font.render(pause_button.text, True, (0, 0, 0))
                            pause_button.draw()
                            self.reset_status('unvisible')

                            # 禁用提示按钮,禁用重排按钮
                            hint_button.disable_button()
                            restart_button.disable_button()
                        else:
                            self.progress_bar.start()
                            pause_button.text = "暂停游戏"
                            pause_button.button_text = pause_button.button_font.render(pause_button.text, True, (0, 0, 0))
                            pause_button.draw()
                            self.reset_status('normal')

                            # 启用提示按钮,启用重排按钮
                            hint_button.enable_button()
                            restart_button.enable_button()
                    else:
                        print("暂停/继续游戏按钮 clicked, but it is disabled")
                elif hint_button.collidepoint(event.pos):
                    if hint_button.is_button_enabled():
                        print("提示按钮 clicked")
                        self.promot()
                    else:
                        print("提示按钮 clicked, but it is disabled")
                elif restart_button.collidepoint(event.pos):
                    if restart_button.is_button_enabled(): 
                        print("重排按钮 clicked")
                        self.rearrangement()
                        self.reset_status('normal')
                    else:
                        print("重排按钮 clicked, but it is disabled")
                elif setting_button.collidepoint(event.pos):
                    print("设置按钮 clicked")
                elif help_button.collidepoint(event.pos):
                    print("帮助按钮 clicked")
                    self._test()
                # 判断鼠标点击位置是否是水果元素内，如果是，将选中的元素周围加上红色边框
                else:
                    # print(f"现在点击了位置：{event.pos}")
                    i = int((event.pos[1]-self.game_matrix_y) / 40) # 选中行数
                    j = int((event.pos[0]-self.game_matrix_x) / 40) # 选中列数
                    # print(f"现在点击了行：{i}，列：{j}")
                    # 修改选中元素的status属性
                    if i >= 0 and i < self.row and j >= 0 and j < self.col and self.matrix[i][j]!=None:
                        if self.matrix[i][j]['status'] == 'choosen':
                            # 如果当前元素已经被选中，则取消选中
                            self.matrix[i][j]['status'] = 'normal'
                            self.choosen_fruit.remove((i,j))
                        elif self.matrix[i][j]['status'] in ['normal','hint']:
                            # 如果当前元素没有被选中，则选中它
                            self.matrix[i][j]['status'] = 'choosen'
                            self.choosen_fruit.add((i,j))
                        elif self.matrix[i][j]['status'] == 'disabled':
                            # 如果当前元素被禁用，则不做任何操作
                            pass
                        else:
                            print(f'非法的状态！')

                        if len(self.choosen_fruit) == 2:
                            fruit1_x, fruit1_y = self.choosen_fruit.pop()
                            fruit2_x, fruit2_y = self.choosen_fruit.pop()
                            fruit1 = self.matrix[fruit1_x][fruit1_y]
                            fruit2 = self.matrix[fruit2_x][fruit2_y]
                            # 判断两个水果元素是否可以消除，可以则返回路径点列表，不可以则返回空列表
                            if fruit1['index'] != fruit2['index']:
                                waypoints = []
                            else:
                                waypoints = self.is_eliminable((fruit1_x,fruit1_y),(fruit2_x,fruit2_y))
                            print(waypoints)
                            if waypoints:
                                print("可以消除")
                                # 消除水果元素
                                self.matrix[fruit1_x][fruit1_y] = None
                                self.matrix[fruit2_x][fruit2_y] = None
                                # 绘制消除界面
                                self.draw_clear_animation(waypoints)
                                self.left_fruit -= 2
                                # 判断游戏是否结束
                                if self.left_fruit == 0:
                                    print("游戏结束")
                                    # 重启游戏
                                    start_button.enable_button()  
                                    # 显示胜利消息
                                    self.show_victory_message()
                                    self.progress_bar.pause()
                            else:
                                print("不可以消除")
                                # 取消选中状态
                                fruit1['status'] = 'normal'
                                fruit2['status'] = 'normal'

                            # 无论是否消除，都要重置元素状态，目前等价于消除所有的hint状态
                            self.reset_status('normal')
        
        return current_page, done

    def reset_status(self,status):
        '''重置所有元素的状态为status'''
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[0])):
                fruit = self.matrix[row][col]
                if fruit != None:
                    fruit['status'] = f'{status}'

    def _test(self):
        '''调试专用函数，用于各种开挂功能'''
        # # 输出整个矩阵
        # for i in range(len(self.matrix)):
        #     for j in range(len(self.matrix[0])):
        #         fruit = self.matrix[i][j]
        #         if fruit == None:
        #             print('None',end=' ')
        #         else:
        #             print(fruit['index'],end=' ')
        #     print()

        # # 显示开始按钮的状态
        # start_button:Button = self.buttons['start_button']
        # print(start_button.is_button_enabled())

        # 自动完成游戏
        while self.left_fruit > 2:
            temp =self.promot()
            if temp:
                fruit1,fruit2 = temp
                waypoints = self.is_eliminable(fruit1,fruit2)
                if waypoints:
                    self.draw_clear_animation(waypoints,0.05)
                    self.matrix[fruit1[0]][fruit1[1]] = None
                    self.matrix[fruit2[0]][fruit2[1]] = None
                    self.left_fruit -= 2
                    self.draw()
                    self.handle()
            else:
                print("没有可以消除的元素了")
                break


    def is_eliminable(self, fruit1:tuple[int,int],fruit2:tuple[int,int],turns:int=2):
        '''
        判断两个水果元素是否可以消除,如果可以消除，返回True和消除路线的途径转折点（按顺序，包括起点和终点）
        '''
        waypoints = []   
        if turns == 0:
            # 不能有转折，直接判断是否在同一行或者同一列，且没有障碍物
            if fruit1[0] == fruit2[0] or fruit1[1] == fruit2[1]:
                if self.is_clear_path(fruit1, fruit2):
                    waypoints.append(fruit1)
                    waypoints.append(fruit2)
                    return waypoints

        elif turns == 1:
            # 只能有一个转折,遍历转折点，判断（fruit1,转折点）和（转折点,fruit2）是否有障碍物
            # 转折点只有两个选项
            turn1 = (fruit1[0], fruit2[1])
            turn2 = (fruit2[0], fruit1[1])
            if self.matrix[turn1[0]][turn1[1]]==None and self.is_clear_path(fruit1, turn1) and self.is_clear_path(turn1, fruit2):
                waypoints.append(fruit1)
                waypoints.append(turn1)
                waypoints.append(fruit2)
                return waypoints
            if self.matrix[turn2[0]][turn2[1]]==None and self.is_clear_path(fruit1, turn2) and self.is_clear_path(turn2, fruit2):
                waypoints.append(fruit1)
                waypoints.append(turn2)
                waypoints.append(fruit2)
                return waypoints
        elif turns == 2:
            # 先从起点开始，往四个方向遍历第一个转折点，然后递归调用自己，判断从第一个转折点到终点是否存在路径
            # 向上
            ans_0 = self.is_eliminable(fruit1,fruit2,0)
            if ans_0:
                return ans_0
            
            ans_1 = self.is_eliminable(fruit1,fruit2,1)
            if ans_1:
                return ans_1

            # 向上
            x,y = fruit1
            x-=1
            while x>=0:
                turn1 = (x,y)
                if self.matrix[x][y] != None:
                    break
                else:
                    temp = self.is_eliminable(turn1, fruit2, 1)
                    if temp:
                        waypoints.append(fruit1)
                        waypoints.extend(temp)
                        return waypoints
                x -= 1

            # 向下
            x,y = fruit1
            x+=1
            while x<self.row:
                turn1 = (x,y)
                if self.matrix[x][y] != None:
                    break
                else:
                    temp = self.is_eliminable(turn1, fruit2, 1)
                    if temp:
                        waypoints.append(fruit1)
                        waypoints.extend(temp)
                        return waypoints
                x += 1
            
            # 向左
            x,y = fruit1
            y-=1
            while y>=0:
                turn1 = (x,y)
                if self.matrix[x][y] != None:
                    break
                else:
                    temp = self.is_eliminable(turn1, fruit2, 1)
                    if temp:
                        waypoints.append(fruit1)
                        waypoints.extend(temp)
                        return waypoints
                y -= 1
            
            # 向右
            x,y = fruit1
            y+=1
            while y<self.col:
                turn1 = (x,y)
                if self.matrix[x][y] != None:
                    break
                else:
                    temp = self.is_eliminable(turn1, fruit2, 1)
                    if temp:
                        waypoints.append(fruit1)
                        waypoints.extend(temp)
                        return waypoints
                y += 1
        return waypoints
                
    def is_clear_path(self,start:tuple[int,int],end:tuple[int,int]):
        '''判断两个点之间是否有障碍物，两个点必须有一个坐标相同,不包含起点和终点'''
        if (start[0] != end[0]) and (start[1] != end[1]):
            return False
        elif start[0] == end[0]:
            for i in range(min(start[1], end[1])+1, max(start[1], end[1])):
                # 需要排除起点和终点
                if self.matrix[start[0]][i] != None:
                    return False
        elif start[1] == end[1]:
            for i in range(min(start[0], end[0])+1, max(start[0], end[0])):
                # 需要排除起点和终点
                if self.matrix[i][start[1]] != None:
                    return False
        return True

    def draw_clear_animation(self,waypoints:list[tuple[int,int]],animation_time:int=0.5):
        '''绘制消除动画，消除动画为起点和终点添加红色边框，途径转折点添加绿色线'''
        # 绘制起点和终点红色边框
        start = waypoints[0]
        end = waypoints[-1]
        start_rect = pygame.Rect((start[1]*40+20, start[0]*40+50), (40, 40))
        end_rect = pygame.Rect((end[1]*40+20, end[0]*40+50), (40, 40))
        pygame.draw.rect(self.screen, (255, 0, 0), start_rect, 2)
        pygame.draw.rect(self.screen, (255, 0, 0), end_rect, 2)
        # 绘制途径转折点绿色线
        for i in range(len(waypoints)-1):
            pygame.draw.line(self.screen, (0, 255, 0), (waypoints[i][1]*40+20+20, waypoints[i][0]*40+50+20), (waypoints[i+1][1]*40+20+20, waypoints[i+1][0]*40+50+20), 5)
        # 更新屏幕
        pygame.display.flip()
        # 暂停1秒钟
        time.sleep(animation_time)
        self.draw()
        # 清除事件队列
        # pygame.event.clear() 

    def rearrangement(self):
        '''重排游戏地图（不是重新生成）'''
        if self.matrix == None:
            return
        # 将矩阵展平为一维数组并打乱元素顺序：
        row = len(self.matrix)
        col = len(self.matrix[0])
        flat_list = []        
        for i in range(row):
            flat_list.extend(self.matrix[i])
        random.shuffle(flat_list)
        # 将打乱后的元素重新填入矩阵
        cnt = 0
        # 防止选中元素没更新导致错误
        self.choosen_fruit.clear()
        for i in range(row):
            for j in range(col):
                pos_x = self.game_matrix_x + j * 40
                pos_y = self.game_matrix_y + i * 40
                if flat_list[cnt] != None:
                    self.matrix[i][j] = flat_list[cnt]
                    self.matrix[i][j]['pos'] = (pos_x, pos_y)
                    if self.matrix[i][j]['status'] == 'choosen':
                        self.choosen_fruit.add((i,j))
                else:
                    self.matrix[i][j] = None
                cnt += 1
    
    def promot(self):
        '''遍历矩阵，寻找两个可以消除的元素,并且标黄'''
        for i in range(len(self.matrix)):
            if self.matrix[i] == None:
                continue
            for j in range(len(self.matrix[0])):
                if self.matrix[i][j] == None:
                    continue
                fruit1 = self.matrix[i][j]
                # 遍历剩余元素
                for m in range(len(self.matrix)):
                    for n in range(len(self.matrix[0])):
                        if m==i and n==j or self.matrix[m][n] == None:
                            continue
                        fruit2 = self.matrix[m][n]
                        # 先要确保两个水果的种类相同
                        if fruit2['index'] != fruit1['index']:
                            continue
                        else:
                            waypoints = self.is_eliminable((i,j),(m,n))
                            if waypoints:
                                fruit1['status'] = 'hint'
                                fruit2['status'] = 'hint'
                                return [(i,j),(m,n)]
        # 如果没有找到可以消除的元素，则提示没有提示信息
        print("没有可以消除的元素")
        # 提示信息显示2秒
        text_color = (255, 255, 255)
        font = pygame.font.SysFont('fangsong', 40)
        message = font.render('没有可以消除的元素', True, text_color)
        message_rect = message.get_rect(center=(self.screen_width/2, self.screen_height/2-50))
        self.screen.blit(message, message_rect)
        pygame.display.flip()
        pygame.time.wait(2000)
        return []

    def show_victory_message(self):
        """显示胜利消息"""
        text_color = (255, 0, 0)
        font = pygame.font.SysFont('fangsong', 60)
        message = font.render('你赢了！', True, text_color)
        message_rect = message.get_rect(center=(self.screen_width/2, self.screen_height/2))
        self.screen.blit(message, message_rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # 显示消息2秒

