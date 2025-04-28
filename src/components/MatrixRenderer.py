"""
矩阵渲染器组件，用于在游戏中绘制矩阵及其元素
"""
import pygame

class MatrixRenderer:
    """矩阵渲染器组件类，负责绘制游戏矩阵及其元素"""
    
    def __init__(self, screen, position=(0, 0), cell_size=(40, 40), row=6, col=6, fruit_images=None):
        """
        初始化矩阵渲染器
        
        Args:
            screen: Pygame屏幕对象
            position: 矩阵左上角位置 (x, y)
            cell_size: 单元格大小 (width, height)
            row: 矩阵行数
            col: 矩阵列数
            fruit_images: 水果图像列表
        """
        self.screen = screen
        self.x, self.y = position
        self.cell_width, self.cell_height = cell_size
        self.row = row
        self.col = col
        self.fruit_images = fruit_images if fruit_images else []
        
        # 矩阵数据
        self.matrix_data = None
        
        # 元素状态颜色定义
        self.colors = {
            "normal": {
                "bg": (255, 255, 255),   # 普通状态背景色
                "border": (200, 200, 200) # 普通状态边框色
            },
            "selected": {
                "bg": (255, 255, 200),   # 选中状态背景色
                "border": (255, 200, 0)   # 选中状态边框色
            },
            "eliminated": {
                "bg": (220, 220, 220),   # 消除状态背景色
                "border": (200, 200, 200) # 消除状态边框色
            }
        }
    
    def set_position(self, position):
        """
        设置矩阵位置
        
        Args:
            position: 新位置 (x, y)
        """
        self.x, self.y = position
    
    def set_size(self, row, col):
        """
        设置矩阵大小
        
        Args:
            row: 行数
            col: 列数
        """
        self.row = row
        self.col = col
    
    def set_cell_size(self, cell_size):
        """
        设置单元格大小
        
        Args:
            cell_size: 单元格大小 (width, height)
        """
        self.cell_width, self.cell_height = cell_size
    
    def set_fruit_images(self, fruit_images:list[pygame.Surface]):
        """
        设置水果图像列表
        
        Args:
            fruit_images: 水果图像列表
        """
        self.fruit_images = fruit_images
    
    def update_matrix_data(self, matrix_data:list[list[dict]]):
        """
        更新矩阵数据
        
        Args:
            matrix_data: 矩阵数据字典，包含 matrix, row, col 等信息
        """
        self.matrix_data = matrix_data
    
    def draw_empty_grid(self):
        """
        绘制空白网格（当没有矩阵数据时）
        """
        for r in range(self.row):
            for c in range(self.col):
                # 计算单元格位置
                x = self.x + c * self.cell_width
                y = self.y + r * self.cell_height
                
                # 绘制单元格边框
                rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
    
    def draw(self):
        """
        绘制矩阵
        """
        # 如果没有矩阵数据，绘制空白网格
        if not self.matrix_data:
            self.draw_empty_grid()
            return
        
        # 遍历矩阵，绘制每个元素
        for r in range(len(self.matrix_data)):
            for c in range(len(self.matrix_data[r])):
                # 计算单元格位置
                x = self.x + c * self.cell_width
                y = self.y + r * self.cell_height
                try:
                    # 获取当前元素
                    cell = self.matrix_data[r][c]
                    element_index = cell.get("index", 0)
                    status = cell.get("status", "normal")
                    
                    # 根据状态获取颜色
                    color_info = self.colors.get(status, self.colors["normal"])
                    border_color = color_info["border"]
                    border_width = 2 if status == "selected" else 1
                    
                    # 绘制单元格边框，不填充背景
                    rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
                    
                    # 只有选中状态才绘制浅黄色背景
                    if status == "selected":
                        pygame.draw.rect(self.screen, color_info["bg"], rect)
                    
                    # 绘制边框
                    pygame.draw.rect(self.screen, border_color, rect, border_width)
                    
                    # 如果元素未被消除且有可用图像，绘制元素图像
                    if status != "eliminated" and self.fruit_images:
                        # 验证索引有效性
                        if 0 <= element_index < len(self.fruit_images):
                            fruit_image = self.fruit_images[element_index]
                            
                            # 计算图像位置，居中显示
                            image_x = x + (self.cell_width - fruit_image.get_width()) // 2
                            image_y = y + (self.cell_height - fruit_image.get_height()) // 2
                            
                            # 绘制水果图像
                            self.screen.blit(fruit_image, (image_x, image_y))
                        elif len(self.fruit_images) > 0:
                            # 索引无效，使用第一张图片
                            fruit_image = self.fruit_images[0]
                            image_x = x + (self.cell_width - fruit_image.get_width()) // 2
                            image_y = y + (self.cell_height - fruit_image.get_height()) // 2
                            self.screen.blit(fruit_image, (image_x, image_y))
                except Exception as e:
                    # 绘制过程中出错，略过该单元格
                    print(f"绘制矩阵时出错: {e}")