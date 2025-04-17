# -*- coding: utf-8 -*-
import pygame
import sys
import os
import random
import time

# 添加父级目录到系统路径，以便导入src中的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logic.matrix_logic import Matrix

class PathVisualization:
    """用于可视化展示连连看游戏中的连接路径"""
    def __init__(self, rows=8, cols=8):
        pygame.init()
        
        # 设置窗口大小与标题
        self.cell_size = 60
        self.margin = 50
        self.screen_width = cols * self.cell_size + 2 * self.margin
        self.screen_height = rows * self.cell_size + 2 * self.margin
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("连连看路径可视化测试")
        
        # 创建元素图像
        self.elements = self.create_elements(10)
        
        # 创建矩阵
        self.matrix = Matrix(rows, cols, self.elements)
        
        # 设置一些元素为eliminated，用于测试
        self.setup_test_matrix()
        
        # 记录选中的单元格
        self.selected_cells = []
        
        # 显示的路径
        self.path = []
        
        # 主循环控制
        self.running = True
        
    def create_elements(self, count):
        """创建带数字的彩色方块作为元素"""
        elements = []
        font = pygame.font.SysFont('Arial', 24)
        
        for i in range(count):
            # 创建不同颜色的方块
            color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            surface = pygame.Surface((self.cell_size, self.cell_size))
            surface.fill(color)
            
            # 添加数字
            number = font.render(str(i), True, (255, 255, 255))
            number_rect = number.get_rect(center=(self.cell_size//2, self.cell_size//2))
            surface.blit(number, number_rect)
            
            elements.append(surface)
        
        return elements
    
    def setup_test_matrix(self):
        """设置测试用的矩阵，将一些元素标记为eliminated以创建路径"""
        rows = len(self.matrix.matrix)
        cols = len(self.matrix.matrix[0])
        
        # 随机设置一些元素为eliminated
        eliminated_count = rows * cols // 4
        for _ in range(eliminated_count):
            row = random.randint(0, rows-1)
            col = random.randint(0, cols-1)
            self.matrix.matrix[row][col]['status'] = 'eliminated'
    
    def draw(self):
        """绘制游戏界面"""
        # 填充背景
        self.screen.fill((240, 240, 240))
        
        # 绘制矩阵
        for row in range(len(self.matrix.matrix)):
            for col in range(len(self.matrix.matrix[0])):
                cell = self.matrix.matrix[row][col]
                x = col * self.cell_size + self.margin
                y = row * self.cell_size + self.margin
                
                # 绘制单元格
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                if cell['status'] == 'eliminated':
                    # 已消除的单元格绘制为浅灰色
                    pygame.draw.rect(self.screen, (200, 200, 200), rect)
                    pygame.draw.rect(self.screen, (180, 180, 180), rect, 1)
                else:
                    # 未消除的单元格显示对应的元素图像
                    self.screen.blit(self.elements[cell['index']], (x, y))
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                
                # 如果单元格被选中，绘制红色边框
                if (row, col) in self.selected_cells:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)
        
        # 绘制路径
        if len(self.path) >= 2:
            for i in range(len(self.path) - 1):
                start_row, start_col = self.path[i]
                end_row, end_col = self.path[i + 1]
                
                start_x = start_col * self.cell_size + self.margin + self.cell_size // 2
                start_y = start_row * self.cell_size + self.margin + self.cell_size // 2
                end_x = end_col * self.cell_size + self.margin + self.cell_size // 2
                end_y = end_row * self.cell_size + self.margin + self.cell_size // 2
                
                # 绘制连接线
                pygame.draw.line(self.screen, (0, 255, 0), (start_x, start_y), (end_x, end_y), 4)
                
                # 绘制路径点
                pygame.draw.circle(self.screen, (0, 0, 255), (start_x, start_y), 6)
            
            # 绘制最后一个路径点
            last_row, last_col = self.path[-1]
            last_x = last_col * self.cell_size + self.margin + self.cell_size // 2
            last_y = last_row * self.cell_size + self.margin + self.cell_size // 2
            pygame.draw.circle(self.screen, (0, 0, 255), (last_x, last_y), 6)
        
        # 显示提示文本
        font = pygame.font.SysFont('Arial', 16)
        hint_text = font.render("点击选择两个相同元素测试消除路径", True, (0, 0, 0))
        restart_text = font.render("按R键重置测试", True, (0, 0, 0))
        
        self.screen.blit(hint_text, (10, 10))
        self.screen.blit(restart_text, (10, 30))
        
        pygame.display.flip()
    
    def handle_events(self):
        """处理用户输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 获取点击的单元格
                col = (event.pos[0] - self.margin) // self.cell_size
                row = (event.pos[1] - self.margin) // self.cell_size
                
                # 检查是否在矩阵范围内
                if 0 <= row < len(self.matrix.matrix) and 0 <= col < len(self.matrix.matrix[0]):
                    # 检查单元格是否已被消除
                    if self.matrix.matrix[row][col]['status'] != 'eliminated':
                        self.handle_cell_click(row, col)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # 重置测试
                    self.reset_test()
    
    def handle_cell_click(self, row, col):
        """处理单元格点击事件"""
        # 如果已经选择了两个单元格，清除之前的选择
        if len(self.selected_cells) >= 2:
            self.selected_cells = []
            self.path = []
        
        # 添加新选择的单元格
        self.selected_cells.append((row, col))
        
        # 如果已经选择了两个单元格，检查是否可以消除
        if len(self.selected_cells) == 2:
            row1, col1 = self.selected_cells[0]
            row2, col2 = self.selected_cells[1]
            
            # 检查两个元素是否相同
            if self.matrix.matrix[row1][col1]['index'] == self.matrix.matrix[row2][col2]['index']:
                # 检查是否可消除
                self.path = self.matrix.is_eliminable(row1, col1, row2, col2)
                
                if self.path:
                    # 消除成功，展示路径动画
                    self.draw()
                    pygame.display.flip()
                    time.sleep(1)  # 展示路径1秒钟
                    
                    # 执行消除
                    self.matrix.matrix[row1][col1]['status'] = 'eliminated'
                    self.matrix.matrix[row2][col2]['status'] = 'eliminated'
                else:
                    print("这两个元素不能被连接")
            else:
                print("选择的元素不相同")
    
    def reset_test(self):
        """重置测试状态"""
        # 重新创建矩阵
        rows = len(self.matrix.matrix)
        cols = len(self.matrix.matrix[0])
        self.matrix = Matrix(rows, cols, self.elements)
        
        # 设置测试环境
        self.setup_test_matrix()
        
        # 清除选择和路径
        self.selected_cells = []
        self.path = []
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.draw()
            pygame.time.delay(30)
        
        pygame.quit()

if __name__ == "__main__":
    app = PathVisualization()
    app.run()

