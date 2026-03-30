#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为计算机视觉课件创建教学图片
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 创建输出目录
import os
output_dir = "images"
os.makedirs(output_dir, exist_ok=True)

# =============================================================================
# 图片1：语义 vs 矩阵对比图
# =============================================================================
def create_semantic_vs_matrix():
    """创建人类视觉vs计算机视觉的对比图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # 左侧：人类看到的（语义）
    ax1.imshow(np.array([[255, 255, 255], [255, 255, 255], [0, 0, 0]]), cmap='gray')
    ax1.set_title('人类视觉：看到"试卷上的字"', fontsize=14, fontproperties='SimHei')
    ax1.axis('off')

    # 右侧：计算机看到的（矩阵）
    matrix_data = np.array([
        [255, 255, 255],
        [255, 255, 255],
        [0, 0, 0]
    ])
    ax2.imshow(matrix_data, cmap='gray')
    ax2.set_title('计算机视觉：数字矩阵', fontsize=14, fontproperties='SimHei')
    ax2.axis('off')

    # 添加矩阵数值标注
    for i in range(3):
        for j in range(3):
            val = matrix_data[i, j]
            color = 'white' if val > 128 else 'white'
            ax2.text(j, i, str(val), ha='center', va='center',
                    color=color, fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/semantic_vs_matrix.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[OK] Created: semantic_vs_matrix.png")

# =============================================================================
# 图片2：数字矩阵示例（更大的矩阵）
# =============================================================================
def create_matrix_example():
    """创建一个展示图像即矩阵的示例"""
    # 创建一个简单的"试卷"样式图像
    img_array = np.ones((100, 150), dtype=np.uint8) * 255  # 白纸

    # 添加一些"文字"（黑色区域）
    img_array[30:40, 20:60] = 0  # 横线
    img_array[50:60, 20:80] = 0  # 横线
    img_array[30:60, 100:105] = 0  # 竖线（类似答题框）

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 左侧：图像显示
    ax1.imshow(img_array, cmap='gray', vmin=0, vmax=255)
    ax1.set_title('图像显示', fontsize=14, fontproperties='SimHei')
    ax1.axis('off')

    # 右侧：矩阵数值（显示部分区域）
    subset = img_array[25:45, 15:35]
    im = ax2.imshow(subset, cmap='gray', vmin=0, vmax=255)
    ax2.set_title('矩阵数值（部分区域）', fontsize=14, fontproperties='SimHei')

    # 添加数值标注
    for i in range(subset.shape[0]):
        for j in range(subset.shape[1]):
            val = subset[i, j]
            color = 'black' if val > 200 else 'white'
            ax2.text(j, i, str(val), ha='center', va='center',
                    color=color, fontsize=6)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/matrix_example.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[OK] 创建：matrix_example.png")

# =============================================================================
# 图片3：彩色图像RGB通道分离
# =============================================================================
def create_rgb_channels():
    """创建RGB三通道分离示意图"""
    # 创建一个简单的彩色图像
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [100, 150, 200]  # 蓝灰色背景

    # 添加一个红色方块
    img[20:40, 20:40] = [255, 0, 0]
    # 添加一个绿色方块
    img[20:40, 60:80] = [0, 255, 0]
    # 添加一个蓝色方块
    img[60:80, 40:60] = [0, 0, 255]

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # 原图
    axes[0, 0].imshow(cv2_bgr_to_rgb(img))
    axes[0, 0].set_title('原始彩色图像', fontproperties='SimHei')
    axes[0, 0].axis('off')

    # R通道
    axes[0, 1].imshow(img[:, :, 2], cmap='Reds', vmin=0, vmax=255)
    axes[0, 1].set_title('R通道（红色）', fontproperties='SimHei')
    axes[0, 1].axis('off')

    # G通道
    axes[1, 0].imshow(img[:, :, 1], cmap='Greens', vmin=0, vmax=255)
    axes[1, 0].set_title('G通道（绿色）', fontproperties='SimHei')
    axes[1, 0].axis('off')

    # B通道
    axes[1, 1].imshow(img[:, :, 0], cmap='Blues', vmin=0, vmax=255)
    axes[1, 1].set_title('B通道（蓝色）', fontproperties='SimHei')
    axes[1, 1].axis('off')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/rgb_channels.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[OK] 创建：rgb_channels.png")

def cv2_bgr_to_rgb(bgr_img):
    """BGR转RGB"""
    return bgr_img[:, :, [2, 1, 0]]

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    print("开始创建课件图片...")
    print()

    create_semantic_vs_matrix()
    create_matrix_example()
    create_rgb_channels()

    print()
    print(f"所有图片已保存到 {output_dir}/ 目录")
    print("请将图片复制到课件目录并更新LaTeX文件中的引用")
