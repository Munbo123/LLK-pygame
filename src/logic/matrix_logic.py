import random
import pygame


class Matrix():
    def __init__(self, row, col, elements=None, element_pairs=None):
        """
        初始化矩阵
        
        Args:
            row: 行数
            col: 列数
            elements: 元素集合
            element_pairs: 预定义的元素对索引
        """
        self.row = row
        self.col = col
        self.matrix = []
        self.selected_pos = None
        self.path = None
        self.left_elements = row * col
        self.elements = elements
        
        # 初始化矩阵
        for i in range(row):
            self.matrix.append([])
            for j in range(col):
                # 初始化每个格子，包含元素索引和状态
                element_index = 0
                if element_pairs and len(element_pairs) > i * col + j:
                    element_index = element_pairs[i * col + j]
                self.matrix[i].append({"index": element_index, "status": "normal"})
    
    def get_row(self):
        """
        获取矩阵行数
        
        Returns:
            int: 行数
        """
        return self.row
    
    def get_col(self):
        """
        获取矩阵列数
        
        Returns:
            int: 列数
        """
        return self.col
        
    def get_left_elements(self):
        """
        获取剩余元素数量
        
        Returns:
            int: 剩余元素数量
        """
        return self.left_elements
        
    def get_cell(self, row, col):
        """
        获取指定位置的格子信息
        
        Args:
            row: 行索引
            col: 列索引
            
        Returns:
            dict: 格子信息
        """
        if 0 <= row < self.row and 0 <= col < self.col:
            return self.matrix[row][col]
        return None
        
    def set_status(self, row, col, status):
        """
        设置指定位置的状态
        
        Args:
            row: 行索引
            col: 列索引
            status: 新状态
            
        Returns:
            bool: 是否设置成功
        """
        if 0 <= row < self.row and 0 <= col < self.col:
            self.matrix[row][col]["status"] = status
            
            # 如果状态为消除，更新剩余元素数量
            if status == "eliminated":
                self.decrease_elements()
                
            return True
        return False
    
    def get_matrix(self):
        """
        获取整个矩阵
        
        Returns:
            list: 矩阵数据
        """
        return self.matrix
    
    def eliminate_cell(self,row:int,col:int):
        '''消除指定位置的元素'''
        if row < 0 or row >= self.row or col < 0 or col >= self.col:
            raise ValueError("行列数越界")
        self.matrix[row][col]['status'] = 'eliminated'  # 将元素状态改为eliminated
        self.decrease_elements()  # 使用decrease_elements方法减少元素计数

    def is_eliminable(self, row1:int, col1:int, row2:int, col2:int):
        '''判断两个元素是否可以消除
        
        输入两个元素的行列坐标，如果两个元素可以消除，返回连接路径点的列表。
        否则返回空列表。路径点列表格式为: [(x1,y1), (x2,y2), ...]
        
        消除条件:
        - 两个元素相同
        - 两者之间存在一条路径，能以最多两次转折到达另一个点
        - 0次转折（在一条直线上，且中间无阻碍）是合法的
        - 1次转折和2次转折也是合法的
        '''
        # 检查边界
        if (row1 < 0 or row1 >= self.row or col1 < 0 or col1 >= self.col or 
            row2 < 0 or row2 >= self.row or col2 < 0 or col2 >= self.col):
            return []
        
        # 检查元素是否已被消除
        if (self.matrix[row1][col1]['status'] == 'eliminated' or 
            self.matrix[row2][col2]['status'] == 'eliminated'):
            return []
        
        # 检查两个元素是否相同
        if self.matrix[row1][col1]['index'] != self.matrix[row2][col2]['index']:
            return []
        
        # 如果是同一个位置，不能消除
        if row1 == row2 and col1 == col2:
            return []
        
        # 检查0次转折（直线连接）
        path = self.check_direct_path(row1, col1, row2, col2)
        if path:
            return path
        
        # 检查1次转折
        path = self.check_one_turn_path(row1, col1, row2, col2)
        if path:
            return path
        
        # 检查2次转折
        path = self.check_two_turn_path(row1, col1, row2, col2)
        if path:
            return path
        
        return []
    
    def check_direct_path(self, row1, col1, row2, col2):
        '''检查两点之间是否可以直线连接（无转折）
        
        如果可以连接，返回路径点列表，否则返回空列表
        '''
        # 如果两点不在同一行也不在同一列，不能直线连接
        if row1 != row2 and col1 != col2:
            return []
        
        path = [(row1, col1), (row2, col2)]
        
        # 在同一行上
        if row1 == row2:
            start_col = min(col1, col2)
            end_col = max(col1, col2)
            # 检查两点之间是否有障碍物
            for col in range(start_col + 1, end_col):
                if self.matrix[row1][col]['status'] != 'eliminated':
                    return []
            return path
        
        # 在同一列上
        if col1 == col2:
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            # 检查两点之间是否有障碍物
            for row in range(start_row + 1, end_row):
                if self.matrix[row][col1]['status'] != 'eliminated':
                    return []
            return path
        
        return []
    
    def check_one_turn_path(self, row1, col1, row2, col2):
        '''检查两点之间是否存在一次转折的路径
        
        如果可以连接，返回路径点列表，否则返回空列表
        '''
        # 尝试通过拐点(row1, col2)连接
        corner1 = (row1, col2)
        if (self.matrix[corner1[0]][corner1[1]]['status'] == 'eliminated'):
            direct_path1 = self.check_direct_path(row1, col1, corner1[0], corner1[1])
            direct_path2 = self.check_direct_path(corner1[0], corner1[1], row2, col2)
            if direct_path1 and direct_path2:
                # 组合路径，但要移除重复的拐点
                return [direct_path1[0], corner1, direct_path2[1]]
        
        # 尝试通过拐点(row2, col1)连接
        corner2 = (row2, col1)
        if (self.matrix[corner2[0]][corner2[1]]['status'] == 'eliminated'):
            direct_path1 = self.check_direct_path(row1, col1, corner2[0], corner2[1])
            direct_path2 = self.check_direct_path(corner2[0], corner2[1], row2, col2)
            if direct_path1 and direct_path2:
                # 组合路径，但要移除重复的拐点
                return [direct_path1[0], corner2, direct_path2[1]]
        
        return []
    
    def check_two_turn_path(self, row1, col1, row2, col2):
        '''检查两点之间是否存在两次转折的路径
        
        如果可以连接，返回路径点列表，否则返回空列表
        '''
        # 尝试所有可能的中间点
        for i in range(self.row):
            # 检查路径: (row1,col1) -> (i,col1) -> (i,col2) -> (row2,col2)
            if (i != row1 and i != row2 and 
                self.matrix[i][col1]['status'] == 'eliminated' and 
                self.matrix[i][col2]['status'] == 'eliminated'):
                path1 = self.check_direct_path(row1, col1, i, col1)
                path2 = self.check_direct_path(i, col1, i, col2)
                path3 = self.check_direct_path(i, col2, row2, col2)
                if path1 and path2 and path3:
                    # 组合完整路径，避免重复点
                    return [path1[0], (i, col1), (i, col2), path3[1]]
        
        for j in range(self.col):
            # 检查路径: (row1,col1) -> (row1,j) -> (row2,j) -> (row2,col2)
            if (j != col1 and j != col2 and 
                self.matrix[row1][j]['status'] == 'eliminated' and 
                self.matrix[row2][j]['status'] == 'eliminated'):
                path1 = self.check_direct_path(row1, col1, row1, j)
                path2 = self.check_direct_path(row1, j, row2, j)
                path3 = self.check_direct_path(row2, j, row2, col2)
                if path1 and path2 and path3:
                    # 组合完整路径，避免重复点
                    return [path1[0], (row1, j), (row2, j), path3[1]]
        
        return []

    def get_elements(self,index:int) -> pygame.Surface:
        '''返回元素'''
        if index < 0 or index >= len(self.elements):
            raise ValueError("元素序号越界")
        return self.elements[index]
    
    def get_elements_width(self) -> int:
        '''返回元素宽度'''
        return self.elements[0].get_width()
    
    def get_elements_height(self) -> int:
        '''返回元素高度'''
        return self.elements[0].get_height()
    
    def promote(self):
        '''寻找矩阵中可以消除的一对元素
        
        遍历整个矩阵，找到第一对可以消除的元素，并返回它们的连接路径
        如果没有可以消除的元素对，则返回空列表
        
        返回值:
            - 找到时: [(row1, col1), (row2, col2), ...] 连接路径的坐标点列表（包含起点和终点）
            - 未找到时: [] 空列表
        '''
        # 遍历矩阵中的所有元素对
        for row1 in range(self.row):
            for col1 in range(self.col):
                # 跳过已消除的元素
                if self.matrix[row1][col1]['status'] == 'eliminated':
                    continue
                
                # 遍历其他元素，寻找可能的匹配
                for row2 in range(self.row):
                    for col2 in range(self.col):
                        # 跳过相同位置或已消除的元素
                        if (row1 == row2 and col1 == col2) or self.matrix[row2][col2]['status'] == 'eliminated':
                            continue
                        
                        # 只检查相同类型的元素
                        if self.matrix[row1][col1]['index'] == self.matrix[row2][col2]['index']:
                            # 检查这两个元素是否可以消除
                            path = self.is_eliminable(row1, col1, row2, col2)
                            if path:
                                return path
        
        # 如果没有找到可以消除的元素对，返回空列表
        return []

    def rearrange_matrix(self):
        '''重排矩阵中的元素
        
        将矩阵中所有未被消除的元素（状态不是'eliminated'的元素）重新排列。
        该函数不需要任何输入参数，也没有返回值。
        '''
        # 收集所有未被消除的元素
        active_elements = []
        for row in range(self.row):
            for col in range(self.col):
                if self.matrix[row][col]['status'] != 'eliminated':
                    # 保存元素的信息
                    active_elements.append(self.matrix[row][col])
                    
        # 打乱这些元素的顺序
        random.shuffle(active_elements)
        
        # 将打乱后的元素重新放回矩阵中
        element_index = 0
        for row in range(self.row):
            for col in range(self.col):
                if self.matrix[row][col]['status'] != 'eliminated':
                    # 只替换未消除的元素位置
                    self.matrix[row][col] = active_elements[element_index]
                    element_index += 1

    def decrease_elements(self, count=1):
        """
        减少剩余元素计数
        
        Args:
            count: 要减少的元素数量，默认为1
            
        Returns:
            int: 更新后的剩余元素数量
        """
        self.left_elements -= count
        if self.left_elements < 0:
            self.left_elements = 0
        return self.left_elements