# -*- coding: utf-8 -*-
import pygame
import os
import sys

# 初始化pygame
pygame.init()

def _initialize_video_mode_for_server():
    """
    为服务端环境初始化视频模式（使用虚拟显示）
    仅在需要时调用此函数
    """
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.display.set_mode((1, 1))
    print("已启用虚拟显示模式（服务端环境）")

def process_fruit_sheet(sheet_path:str=r"./assets/fruit_element.bmp", mask_path:str=r"./assets/fruit_mask.bmp") -> list[pygame.Surface]:
    '''
    将水果图集转换为透明的 Surface，并切分为10个水果图像
    
    参数:
        sheet_path: 水果图集的路径
        mask_path: 遮罩图像的路径
        
    返回:
        list[pygame.Surface]: 包含10个水果图像的列表
    '''
    try:
        # 尝试直接加载图像
        sheet = pygame.image.load(sheet_path).convert_alpha()
        mask = pygame.image.load(mask_path).convert_alpha()
    except pygame.error as e:
        # 如果出错且错误信息包含"No video mode has been set"，则尝试使用虚拟显示
        if "No video mode has been set" in str(e):
            _initialize_video_mode_for_server()
            # 重新尝试加载
            sheet = pygame.image.load(sheet_path).convert_alpha()
            mask = pygame.image.load(mask_path).convert_alpha()
        else:
            # 其他类型的错误，继续抛出
            raise

    # 创建一个透明的 Surface
    processed_sheet = pygame.Surface(sheet.get_size(), pygame.SRCALPHA)
    width,height = sheet.get_size()

    # 根据遮罩图像处理水果图集
    for x in range(width):
        for y in range(height):
            # 获取像素颜色
            pixel_color = sheet.get_at((x, y))
            mask_color = mask.get_at((x, y))
            # 如果 mask.bmp 中的像素颜色为白色，则设置为透明
            if mask_color != (255, 255, 255, 255):
                processed_sheet.set_at((x, y), (0, 0, 0, 0))
            else:
                processed_sheet.set_at((x, y), pixel_color)
        
    # 将处理后的水果图集切分为10个水果图像
    fruit_images = []
    for i in range(10):
        rect = pygame.Rect(0, i * 40, 40, 40)
        fruit_images.append(processed_sheet.subsurface(rect).copy())  # 注意用 copy() 得到独立的 Surface
    
    return fruit_images

def load_images():
    """
    加载游戏需要的图片资源
    
    返回:
        list[pygame.Surface]: 包含游戏图像的列表
    """
    try:
        return process_fruit_sheet()
    except Exception as e:
        print(f"加载图像时出错: {e}")
        # 如果无法加载图像，返回一些简单的彩色方块作为替代
        dummy_images = []
        colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), 
                  (255,0,255), (0,255,255), (128,0,0), (0,128,0),
                  (0,0,128), (128,128,0)]
        
        for color in colors:
            # 创建一个彩色方块
            img = pygame.Surface((40, 40), pygame.SRCALPHA)
            img.fill((*color, 255))
            dummy_images.append(img)
            
        return dummy_images