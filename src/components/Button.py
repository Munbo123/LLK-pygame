import pygame

class Button:
    def __init__(self,screen,position,rect,color=(255, 255, 255),text_color=(0, 0, 0),font=None,font_size=20,text="Button"):
        # 屏幕对象
        self.screen = screen
        # 位置，大小属性
        self.x, self.y = position
        self.width, self.height = rect
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # 按钮颜色，字体颜色，字体属性
        self.default_button_color = color
        self.default_text_color = text_color
        self.button_color = color
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.text = text
        # 创建字体对象
        self.button_font = pygame.font.SysFont(font, font_size)
        self.button_text = self.button_font.render(text, True, text_color)

        # 禁用状态的颜色
        self.disabled_button_color = (200, 200, 200)  # 灰色背景
        self.disabled_text_color = (100, 100, 100)    # 深灰色文字

        # 圆角
        self.radius = 10

        # 按钮状态属性
        self.enable = True

    def draw(self):
        pygame.draw.rect(surface=self.screen, color=self.button_color, rect=self.button_rect, border_radius=self.radius)
        self.screen.blit(self.button_text, (self.button_rect.centerx - self.button_text.get_width() / 2, self.button_rect.centery - self.button_text.get_height() / 2))
        return self.button_rect

    def enable_button(self):
        self.enable = True
        # 恢复默认颜色
        self.button_color = self.default_button_color
        self.text_color = self.default_text_color
        # 重新渲染文本
        self.button_text = self.button_font.render(self.text, True, self.text_color)
        # 不需要立即调用draw()，因为会在下一个游戏循环中绘制
    
    def disable_button(self):
        self.enable = False
        # 设置为禁用状态的颜色
        self.button_color = self.disabled_button_color
        self.text_color = self.disabled_text_color
        # 重新渲染文本
        self.button_text = self.button_font.render(self.text, True, self.text_color)
        # 不需要立即调用draw()，因为会在下一个游戏循环中绘制
    
    def is_button_enabled(self):
        return self.enable

    def collidepoint(self, pos):
        '''判断鼠标点击位置是否在按钮区域内'''
        if self.button_rect.collidepoint(pos):
            return True
        return False
    
    def set_text(self, text):
        '''设置按钮文本'''
        self.text = text
        self.button_text = self.button_font.render(text, True, self.text_color)
        # 不需要立即调用draw()，因为会在下一个游戏循环中绘制

