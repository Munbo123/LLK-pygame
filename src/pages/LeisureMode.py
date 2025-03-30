from pages.BasicMode import Basic_mode
import pygame

class Leisure_mode(Basic_mode):
    def __init__(self,screen:pygame.Surface):
        super().__init__(screen=screen)
        # 休闲模式不需要计时器
        self.progress_bar.disable()