import pygame

class Progress_bar:
    def __init__(self,screen:pygame.Surface):
        # 屏幕对象
        self.screen = screen
        # 屏幕宽高
        screen_width, screen_height = screen.get_size()
        # 用于计时的变量
        self.total_time = 300 # 总时间默认300秒
        self.pre_time = 0 # 上次计时的时间
        self.remaining_time = self.total_time # 剩余时间
        self.progress_running = False
        self.enable = True       # 进度条是否启用
        # 进度条参数
        self.bar_width = 500  # 进度条总宽度
        self.bar_height = 20
        self.bar_x = (screen_width-self.bar_width)/2-50  # 进度条绘制起始坐标
        self.bar_y = 500
        self.font = pygame.font.SysFont('fangsong', 24)
        self.bar_border_radius = 20

    def draw(self):
        if not self.enable:
            return
        if self.progress_running:
            # 更新剩余时间
            self.remaining_time -= (pygame.time.get_ticks() - self.pre_time) / 1000
            self.remaining_time = max(0, self.remaining_time)

        self.pre_time = pygame.time.get_ticks() # 更新上次计时的时间

        '''绘制进度条背景'''
        # 计算进度条宽度
        ratio = self.remaining_time / self.total_time
        current_width = self.bar_width * ratio

        # 绘制进度条
        pygame.draw.rect(self.screen, (200, 200, 200), (self.bar_x+current_width, self.bar_y, self.bar_width-current_width, self.bar_height),border_top_right_radius=self.bar_border_radius,border_bottom_right_radius=self.bar_border_radius)
        pygame.draw.rect(self.screen, (0, 255, 0), (self.bar_x, self.bar_y, current_width, self.bar_height),border_top_left_radius=self.bar_border_radius,border_bottom_left_radius=self.bar_border_radius)

        # 绘制倒计时文本
        text = self.font.render(f"倒计时: {int(self.remaining_time)}秒", True, (0, 0, 0))
        # 在进度条上方绘制倒计时文本
        self.screen.blit(text, (self.bar_x + self.bar_width // 3, self.bar_y - 40))

        # 判断是否结束
        if self.remaining_time <= 0:
            print("倒计时结束")
        
        
    
    def start(self):
        '''开始计时'''
        self.progress_running = True         

    def pause(self):
        '''暂停计时'''
        self.progress_running = False

    def set_total_time(self,total_time:int):
        self.total_time = total_time

    def reset(self):
        '''重置计时器'''
        self.remaining_time = self.total_time

    def set_time(self,current_time:int):
        pass

    def add_time(self,add_time:int):
        pass

    def reduce_time(self,reduce_time:int):
        pass

    def disable(self):
        '''禁用进度条'''
        self.enable = False
        
