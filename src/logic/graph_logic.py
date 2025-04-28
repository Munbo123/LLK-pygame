import random
import pygame
from collections import deque

class Graph:
    """
    使用真正的图数据结构实现连连看游戏逻辑
    
    图结构表示：
    - 每个游戏元素(水果)是一个节点
    - 节点之间通过边相连
    - 使用邻接列表表示图结构
    """
    def __init__(self, row: int, col: int, elements: list[pygame.Surface]):
        """初始化图结构
        
        Parameters:
            row: 游戏网格的行数
            col: 游戏网格的列数
            elements: 游戏元素(水果)的Surface对象列表
        """
        if row <= 0 or col <= 0:
            raise ValueError("行列数必须大于0")
        if row * col % 2 == 1:
            raise ValueError("行列数乘积必须为偶数")
        
        self.row = row
        self.col = col
        self.elements = elements
        self.left_elements = row * col  # 剩余元素数目
        
        # 图数据结构 - 邻接列表表示
        self.graph = {}  # 键: 节点坐标 (row, col), 值: 相邻节点列表
        
        # 节点属性存储
        self.nodes_data = {}  # 键: 节点坐标 (row, col), 值: {'index': 水果类型索引, 'status': 节点状态}
        
        # 初始化图结构
        self.init_graph()

    def init_graph(self):
        """初始化图结构，创建节点和边"""
        # 准备水果类型索引列表，确保每种水果都有偶数个
        fruit_indices = []
        for _ in range(self.row * self.col // 2):
            index = random.randint(0, len(self.elements) - 1)
            fruit_indices.append(index)
            fruit_indices.append(index)  # 添加两次以确保成对出现
        
        # 随机打乱
        random.shuffle(fruit_indices)
        
        # 创建节点
        idx = 0
        for i in range(self.row):
            for j in range(self.col):
                node = (i, j)
                self.nodes_data[node] = {
                    'index': fruit_indices[idx],  # 水果类型索引
                    'status': 'normal',  # 初始状态为normal
                }
                idx += 1
                
                # 为每个节点初始化邻接列表
                self.graph[node] = []
        
        # 创建边 - 每个节点与其上下左右节点相连
        for i in range(self.row):
            for j in range(self.col):
                node = (i, j)
                
                # 上节点 (如果存在)
                if i > 0:
                    self.graph[node].append((i-1, j))
                
                # 下节点 (如果存在)
                if i < self.row - 1:
                    self.graph[node].append((i+1, j))
                
                # 左节点 (如果存在)
                if j > 0:
                    self.graph[node].append((i, j-1))
                
                # 右节点 (如果存在)
                if j < self.col - 1:
                    self.graph[node].append((i, j+1))
    
    def get_matrix(self):
        """返回节点矩阵表示，兼容矩阵实现的接口"""
        matrix = [[None for j in range(self.col)] for _ in range(self.row)]
        for i in range(self.row):
            for j in range(self.col):
                matrix[i][j] = self.nodes_data[(i, j)]
        return matrix
    
    def get_cell(self, row: int, col: int):
        """获取指定位置的节点信息"""
        if row < 0 or row >= self.row or col < 0 or col >= self.col:
            raise ValueError("行列数越界")
        return self.nodes_data[(row, col)]
    
    def eliminate_cell(self, row: int, col: int):
        """消除指定位置的元素"""
        if row < 0 or row >= self.row or col < 0 or col >= self.col:
            raise ValueError("行列数越界")
        self.nodes_data[(row, col)]['status'] = 'eliminated'
        self.left_elements -= 1
    
    def is_eliminable(self, row1: int, col1: int, row2: int, col2: int):
        """判断两个节点是否可以消除
        
        使用广度优先搜索(BFS)算法，找到两点之间至多包含两次转折的路径
        
        Parameters:
            row1, col1: 第一个节点的行列坐标
            row2, col2: 第二个节点的行列坐标
            
        Returns:
            list: 如果可以消除，返回连接路径点列表 [(row1,col1), ..., (row2,col2)]
                 否则返回空列表 []
        """
        # 检查边界条件
        if (row1 < 0 or row1 >= self.row or col1 < 0 or col1 >= self.col or
            row2 < 0 or row2 >= self.row or col2 < 0 or col2 >= self.col):
            return []
        
        # 检查元素是否已被消除
        if (self.nodes_data[(row1, col1)]['status'] == 'eliminated' or
            self.nodes_data[(row2, col2)]['status'] == 'eliminated'):
            return []
        
        # 检查是否是相同类型的水果
        if self.nodes_data[(row1, col1)]['index'] != self.nodes_data[(row2, col2)]['index']:
            return []
        
        # 检查是否是同一个位置
        if row1 == row2 and col1 == col2:
            return []
        
        # 使用BFS寻找路径，限制最多两次转折
        return self.find_path_with_bfs(row1, col1, row2, col2)
    
    def find_path_with_bfs(self, row1, col1, row2, col2):
        """使用BFS寻找两点之间的路径，最多允许两次转折"""
        start = (row1, col1)
        end = (row2, col2)
        
        # 队列中的元素: (当前节点, 路径, 已转折次数, 当前方向)
        # 方向: 0=初始, 1=水平向右, 2=水平向左, 3=垂直向下, 4=垂直向上
        queue = deque([(start, [start], 0, 0)])
        
        # 访问记录: (节点, 方向, 转折次数) -> 已访问
        # 这样同一个节点在不同方向和转折次数下可以被多次访问
        visited = set()
        
        while queue:
            node, path, turns, direction = queue.popleft()
            row, col = node
            
            # 如果到达目标节点，返回路径
            if node == end:
                return self.simplify_path(path)
            
            # 如果转弯次数超过2，不继续探索
            if turns > 2:
                continue
            
            # 尝试四个方向移动
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                new_node = (new_row, new_col)
                
                # 检查边界
                if new_row < 0 or new_row >= self.row or new_col < 0 or new_col >= self.col:
                    continue
                
                # 确定新的移动方向
                if dc == 1:
                    new_direction = 1  # 向右
                elif dc == -1:
                    new_direction = 2  # 向左
                elif dr == 1:
                    new_direction = 3  # 向下
                else:
                    new_direction = 4  # 向上
                
                # 计算转折次数
                new_turns = turns
                if direction != 0 and direction != new_direction:
                    new_turns += 1
                
                # 如果转折次数超过2，不继续探索
                if new_turns > 2:
                    continue
                
                # 检查新节点是否可通行
                is_end = new_node == end
                is_eliminated = self.nodes_data[new_node]['status'] == 'eliminated'
                
                # 只有终点或已消除的节点可以通行
                if not (is_end or is_eliminated):
                    continue
                
                # 避免重复访问相同的(节点,方向,转折次数)组合
                visit_key = (new_node, new_direction, new_turns)
                if visit_key in visited:
                    continue
                
                # 将新节点加入队列并标记为已访问
                visited.add(visit_key)
                new_path = path + [new_node]
                queue.append((new_node, new_path, new_turns, new_direction))
        
        # 未找到有效路径
        return []
    
    def get_left_elements(self) -> int:
        """返回剩余未消除的元素数量"""
        return self.left_elements
    
    def get_row(self):
        """返回行数"""
        return self.row
    
    def get_col(self):
        """返回列数"""
        return self.col
    
    def get_elements(self, index: int) -> pygame.Surface:
        """返回指定索引的元素图像"""
        if index < 0 or index >= len(self.elements):
            raise ValueError("元素序号越界")
        return self.elements[index]
    
    def get_elements_width(self) -> int:
        """返回元素宽度"""
        return self.elements[0].get_width()
    
    def get_elements_height(self) -> int:
        """返回元素高度"""
        return self.elements[0].get_height()
    
    def set_status(self, row: int, col: int, status: str):
        """设置元素状态"""
        if row < 0 or row >= self.row or col < 0 or col >= self.col:
            raise ValueError("行列数越界")
        self.nodes_data[(row, col)]['status'] = status

    def promote(self):
        """寻找一对可消除的元素
        
        在图中找到第一对可消除的元素，返回连接路径
        
        Returns:
            list: 连接路径坐标列表 [(row1,col1), ..., (row2,col2)]，如果没找到则返回空列表
        """
        # 找出所有未消除的节点
        active_nodes = [(r, c) for r in range(self.row) for c in range(self.col) 
                        if self.nodes_data[(r, c)]['status'] != 'eliminated']
        
        # 按水果类型对节点进行分组
        nodes_by_type = {}
        for node in active_nodes:
            fruit_index = self.nodes_data[node]['index']
            if fruit_index not in nodes_by_type:
                nodes_by_type[fruit_index] = []
            nodes_by_type[fruit_index].append(node)
        
        # 检查每种类型的水果
        for fruit_type, nodes in nodes_by_type.items():
            # 检查同类型水果组合是否可消除
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    path = self.is_eliminable(node1[0], node1[1], node2[0], node2[1])
                    if path:
                        return path
        
        # 没找到可消除的元素对
        return []

    def rearrange_matrix(self):
        """重排未消除的元素
        
        将图中所有未被消除的元素重新随机排列
        """
        # 收集所有未消除的元素索引
        active_indices = []
        active_positions = []
        
        for r in range(self.row):
            for c in range(self.col):
                if self.nodes_data[(r, c)]['status'] != 'eliminated':
                    active_indices.append(self.nodes_data[(r, c)]['index'])
                    active_positions.append((r, c))
        
        # 随机打乱索引
        random.shuffle(active_indices)
        
        # 重新分配到各个位置
        for i, pos in enumerate(active_positions):
            self.nodes_data[pos]['index'] = active_indices[i]

    def simplify_path(self, path):
        """简化路径，只保留起点、拐点和终点
        
        BFS搜索返回的路径包含路径上的每一个点，而我们只需要保留关键点：
        1. 起始点
        2. 终点
        3. 拐点（路径方向发生变化的点）
        
        Parameters:
            path: 完整路径列表 [(row1, col1), (row2, col2), ...]
            
        Returns:
            list: 简化后的路径列表，只包含关键点
        """
        if not path or len(path) <= 2:
            return path  # 路径为空或只有起点终点，直接返回
        
        simplified = [path[0]]  # 始终保留起点
        
        # 遍历路径中间的点，判断是否为拐点
        for i in range(1, len(path) - 1):
            prev = path[i-1]
            curr = path[i]
            next_point = path[i+1]
            
            # 判断是否为拐点：拐点的特征是方向发生变化
            # 如果从prev到curr和从curr到next的方向不同，则curr是拐点
            prev_dir = self.get_direction(prev, curr)
            next_dir = self.get_direction(curr, next_point)
            
            if prev_dir != next_dir:
                simplified.append(curr)  # 添加拐点
        
        simplified.append(path[-1])  # 始终保留终点
        return simplified
    
    def get_direction(self, point1, point2):
        """获取从point1到point2的方向
        
        Returns:
            str: 'horizontal' 水平方向或 'vertical' 垂直方向
        """
        row1, col1 = point1
        row2, col2 = point2
        
        if row1 == row2:  # 同一行
            return 'horizontal'
        elif col1 == col2:  # 同一列
            return 'vertical'
        else:
            # 这种情况不应该出现在连连看的有效路径中
            # 一个点到下一个点的移动应该是水平或垂直的
            return 'diagonal'