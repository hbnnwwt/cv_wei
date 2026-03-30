# -*- coding: utf-8 -*-
"""
Week03 教学图片生成脚本
=======================
生成图像预处理与增强相关的教学示意图

运行:
    python generate_figures.py

输出:
    - pipeline_overview.png    : 图像处理流水线
    - noise_types.png          : 四种噪声类型对比
    - convolution_process.png  : 卷积滑动过程示意
    - histogram_examples.png   : 直方图形态对比
    - binarization_comparison.png : 三种二值化方法对比
    - transform_types.png      : 仿射vs透视变换对比
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = 'white'

# 输出目录
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_pipeline_overview():
    """生成图像处理流水线流程图"""
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis('off')
    ax.set_title('图像处理流水线', fontsize=16, fontweight='bold', pad=20)

    # 5个步骤
    steps = [
        ('1. 图像获取', '相机/文件'),
        ('2. 预处理', '去噪/增强'),
        ('3. 特征提取', '边缘/纹理'),
        ('4. 目标检测', '分割/识别'),
        ('5. 后处理', '优化/输出')
    ]

    for i, (title, desc) in enumerate(steps):
        x = 1.2 + i * 2.2

        # 绘制圆角矩形
        rect = FancyBboxPatch((x, 1), 1.8, 1,
                               boxstyle="round,pad=0.05",
                               facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
        ax.add_patch(rect)

        # 标题
        ax.text(x + 0.9, 1.65, title, ha='center', va='center', fontsize=11, fontweight='bold')
        # 描述
        ax.text(x + 0.9, 1.35, desc, ha='center', va='center', fontsize=9, color='#666666')

        # 箭头（最后一个除外）
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + 1.9, 1.5), xytext=(x + 2, 1.5),
                        arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'pipeline_overview.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: pipeline_overview.png")


def create_noise_types():
    """生成四种噪声类型对比图"""
    np.random.seed(42)

    # 创建基础图像
    base_img = np.zeros((100, 100), dtype=np.uint8)
    for i in range(20):
        cv2.circle(base_img, (i * 5 + 5, 50), 3, 255, -1)

    # 添加不同噪声
    img_gaussian = base_img.copy().astype(np.float64) + np.random.normal(0, 30, base_img.shape)
    img_gaussian = np.clip(img_gaussian, 0, 255).astype(np.uint8)

    img_salt = base_img.copy()
    salt_coords = np.random.choice([True, False], base_img.shape, p=[0.05, 0.95])
    img_salt[salt_coords] = 255

    img_pepper = base_img.copy()
    pepper_coords = np.random.choice([True, False], base_img.shape, p=[0.05, 0.95])
    img_pepper[pepper_coords] = 0

    img_speckle = base_img.copy().astype(np.float64) + np.random.normal(0, 50, base_img.shape) * base_img / 255
    img_speckle = np.clip(img_speckle, 0, 255).astype(np.uint8)

    # 绘制2x2网格
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle('四种噪声类型对比', fontsize=16, fontweight='bold')

    images = [
        ('高斯噪声', img_gaussian),
        ('椒盐噪声', img_salt),
        ('胡椒噪声', img_pepper),
        (' speckle噪声', img_speckle)
    ]

    for idx, (title, img) in enumerate(images):
        row = idx // 2
        col = idx % 2
        axes[row, col].imshow(img, cmap='gray')
        axes[row, col].set_title(title, fontsize=12)
        axes[row, col].axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'noise_types.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: noise_types.png")


def create_convolution_process():
    """生成卷积滑动过程示意图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('卷积操作示意图', fontsize=16, fontweight='bold', pad=20)

    # 绘制输入图像（5x5网格）
    input_data = np.random.randint(0, 255, (5, 5))
    cell_size = 0.8
    start_x, start_y = 1, 3

    # 绘制输入图像网格
    for i in range(5):
        for j in range(5):
            color = plt.cm.YlOrRd(input_data[i, j] / 255)
            rect = plt.Rectangle((start_x + j * cell_size, start_y + (4-i) * cell_size),
                                  cell_size, cell_size, facecolor=color, edgecolor='black')
            ax.add_patch(rect)

    ax.text(start_x + 2.5 * cell_size, start_y - 0.3, '输入图像 (5×5)', ha='center', fontsize=10)

    # 绘制卷积核（3x3）
    kernel_size = 3
    kernel_x, kernel_y = 5.5, 3.5
    kernel_data = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])  # 简单的边缘检测核

    # 绘制高亮框（当前卷积位置）
    highlight = plt.Rectangle((start_x + cell_size, start_y + cell_size),
                               cell_size * 3, cell_size * 3,
                               facecolor='none', edgecolor='red', linewidth=3, linestyle='--')
    ax.add_patch(highlight)

    ax.text(kernel_x + 0.5, kernel_y + 2.8, '卷积核 (3×3)', ha='center', fontsize=10)

    # 绘制卷积核值
    for i in range(3):
        for j in range(3):
            ax.text(kernel_x + j * 0.4 + 0.2, kernel_y + (2-i) * 0.4 + 0.2,
                    str(kernel_data[i, j]), ha='center', va='center', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', edgecolor='orange'))

    # 绘制箭头
    ax.annotate('', xy=(4.8, 4), xytext=(3.2, 4),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.text(4, 4.3, '卷积', fontsize=10, color='blue', ha='center')

    # 绘制输出特征
    ax.text(7.5, 4.3, '输出特征', ha='center', fontsize=10)
    for i in range(3):
        for j in range(3):
            rect = plt.Rectangle((7 + j * 0.4, 3.8 + (2-i) * 0.4),
                                  0.4, 0.4, facecolor='lightblue', edgecolor='black')
            ax.add_patch(rect)
            ax.text(7.2 + j * 0.4, 4 - i * 0.4, '?', ha='center', va='center', fontsize=7)

    # 底部说明
    ax.text(5, 0.8, '卷积核在输入图像上滑动，每一步计算核与对应区域的点积', ha='center', fontsize=10, color='#666666')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'convolution_process.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: convolution_process.png")


def create_histogram_examples():
    """生成直方图形态对比"""
    # 生成三种不同亮度的图像
    img_dark = np.clip(np.random.normal(60, 20, (200, 200)), 0, 255).astype(np.uint8)
    img_normal = np.clip(np.random.normal(128, 40, (200, 200)), 0, 255).astype(np.uint8)
    img_bright = np.clip(np.random.normal(200, 20, (200, 200)), 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    fig.suptitle('直方图形态对比', fontsize=16, fontweight='bold')

    # 第一行：图像
    axes[0, 0].imshow(img_dark, cmap='gray')
    axes[0, 0].set_title('偏暗图像', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img_normal, cmap='gray')
    axes[0, 1].set_title('正常亮度图像', fontsize=12)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(img_bright, cmap='gray')
    axes[0, 2].set_title('偏亮图像', fontsize=12)
    axes[0, 2].axis('off')

    # 第二行：直方图
    axes[1, 0].hist(img_dark.flatten(), bins=50, color='darkblue', alpha=0.7)
    axes[1, 0].set_xlim(0, 255)
    axes[1, 0].set_title('直方图 - 偏暗', fontsize=11)
    axes[1, 0].set_xlabel('灰度值')
    axes[1, 0].set_ylabel('像素数')

    axes[1, 1].hist(img_normal.flatten(), bins=50, color='darkgreen', alpha=0.7)
    axes[1, 1].set_xlim(0, 255)
    axes[1, 1].set_title('直方图 - 正常', fontsize=11)
    axes[1, 1].set_xlabel('灰度值')
    axes[1, 1].set_ylabel('像素数')

    axes[1, 2].hist(img_bright.flatten(), bins=50, color='darkred', alpha=0.7)
    axes[1, 2].set_xlim(0, 255)
    axes[1, 2].set_title('直方图 - 偏亮', fontsize=11)
    axes[1, 2].set_xlabel('灰度值')
    axes[1, 2].set_ylabel('像素数')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'histogram_examples.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: histogram_examples.png")


def create_binarization_comparison():
    """生成三种二值化方法对比"""
    # 创建带渐变区域的测试图像
    test_img = np.zeros((200, 300), dtype=np.uint8)
    for i in range(200):
        for j in range(300):
            test_img[i, j] = int((i + j) * 255 / 500)  # 对角渐变

    # 添加一些噪声和特征
    cv2.rectangle(test_img, (50, 50), (100, 150), 180, -1)
    cv2.circle(test_img, (200, 100), 30, 80, -1)

    # 三种阈值方法
    _, img_binary = cv2.threshold(test_img, 127, 255, cv2.THRESH_BINARY)
    _, img_otsu = cv2.threshold(test_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_adaptive = cv2.adaptiveThreshold(test_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)

    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    fig.suptitle('三种二值化方法对比', fontsize=16, fontweight='bold')

    axes[0].imshow(test_img, cmap='gray')
    axes[0].set_title('原始图像', fontsize=12)
    axes[0].axis('off')

    axes[1].imshow(img_binary, cmap='gray')
    axes[1].set_title('固定阈值 (T=127)', fontsize=12)
    axes[1].axis('off')

    axes[2].imshow(img_otsu, cmap='gray')
    axes[2].set_title('Otsu自适应阈值', fontsize=12)
    axes[2].axis('off')

    axes[3].imshow(img_adaptive, cmap='gray')
    axes[3].set_title('高斯自适应阈值', fontsize=12)
    axes[3].axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'binarization_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: binarization_comparison.png")


def create_transform_types():
    """生成仿射变换与透视变换对比"""
    import cv2

    # 创建测试图像
    test_img = np.zeros((200, 300, 3), dtype=np.uint8)
    test_img[:, :] = (240, 240, 240)  # 浅灰色背景
    # 添加网格
    for i in range(0, 200, 20):
        cv2.line(test_img, (0, i), (300, i), (200, 200, 200), 1)
    for j in range(0, 300, 20):
        cv2.line(test_img, (j, 0), (j, 200), (200, 200, 200), 1)
    # 添加特征点
    cv2.circle(test_img, (50, 50), 15, (255, 0, 0), -1)  # 红色
    cv2.circle(test_img, (250, 50), 15, (0, 255, 0), -1)  # 绿色
    cv2.circle(test_img, (50, 150), 15, (0, 0, 255), -1)  # 蓝色
    cv2.circle(test_img, (250, 150), 15, (255, 255, 0), -1)  # 黄色

    # 原始四个角点
    pts_src = np.array([[50, 50], [250, 50], [50, 150], [250, 150]], dtype=np.float32)

    # 仿射变换：保持平行四边形
    pts_affine = np.array([[80, 30], [280, 30], [20, 170], [220, 170]], dtype=np.float32)
    M_affine = cv2.getAffineTransform(pts_src, pts_affine)
    img_affine = cv2.warpAffine(test_img, M_affine, (300, 200))

    # 透视变换：任意四边形
    pts_perspective = np.array([[30, 20], [290, 40], [10, 180], [270, 190]], dtype=np.float32)
    M_perspective = cv2.getPerspectiveTransform(pts_src, pts_perspective)
    img_perspective = cv2.warpPerspective(test_img, M_perspective, (300, 200))

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fig.suptitle('仿射变换 vs 透视变换', fontsize=16, fontweight='bold')

    axes[0].imshow(cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB))
    axes[0].set_title('原图', fontsize=12)
    axes[0].axis('off')

    axes[1].imshow(cv2.cvtColor(img_affine, cv2.COLOR_BGR2RGB))
    axes[1].set_title('仿射变换\n(保持平行性)', fontsize=12)
    axes[1].axis('off')

    axes[2].imshow(cv2.cvtColor(img_perspective, cv2.COLOR_BGR2RGB))
    axes[2].set_title('透视变换\n(近大远小)', fontsize=12)
    axes[2].axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'transform_types.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("已生成: transform_types.png")


def main():
    """主函数：生成所有教学图片"""
    print("开始生成Week03教学图片...")

    # 切换到images目录
    os.chdir(OUTPUT_DIR)

    create_pipeline_overview()
    create_noise_types()
    create_convolution_process()
    create_histogram_examples()
    create_binarization_comparison()
    create_transform_types()

    print("\n所有图片生成完成!")
    print(f"图片保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()