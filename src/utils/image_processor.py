# -*- coding: utf-8 -*-
import pygame

def process_fruit_sheet(sheet_path:str, mask_path:str):
    '''
    将水果图集转换为透明的 Surface，并切分为10个水果图像
    
    参数:
        sheet_path: 水果图集的路径
        mask_path: 遮罩图像的路径
        
    返回:
        list[pygame.Surface]: 包含10个水果图像的列表
    '''
    # 加载水果图集和遮罩图像
    sheet = pygame.image.load(sheet_path).convert_alpha()
    mask = pygame.image.load(mask_path).convert_alpha()

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