#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为计算机视觉课件创建CV历史时间线图片
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib
matplotlib.use('Agg')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_cv_history_timeline():
    """创建CV历史时间线图片"""
    fig, ax = plt.subplots(figsize=(14, 6))

    # 定义时间线数据
    events = [
        {'year': '1966', 'title': 'CV诞生', 'desc': 'Larry Roberts\nBlock World\n(CV之父)', 'color': '#3498db'},
        {'year': '1980s', 'title': '理论奠基', 'desc': 'David Marr\n视觉计算理论\n边缘检测算法', 'color': '#2ecc71'},
        {'year': '1999', 'title': '特征提取', 'desc': 'David Lowe\nSIFT算法\n(尺度不变特征)', 'color': '#f39c12'},
        {'year': '2012', 'title': '深度学习爆发', 'desc': 'AlexNet\nImageNet夺冠\nCNN时代开启', 'color': '#e74c3c'},
        {'year': '2020s', 'title': 'AIGC时代', 'desc': 'DALL-E/Midjourney\n图像生成\n多模态大模型', 'color': '#9b59b6'},
    ]

    # 绘制时间线
    x_positions = np.linspace(1, 12, len(events))
    y_level = 0.5

    # 绘制主时间线
    ax.plot([0.5, 12.5], [y_level, y_level], 'k-', linewidth=3, alpha=0.3)

    # 添加事件节点
    for i, (x, event) in enumerate(zip(x_positions, events)):
        # 节点圆圈
        circle = plt.Circle((x, y_level), 0.3, color=event['color'], zorder=10)
        ax.add_patch(circle)

        # 年份标签（上方）
        ax.text(x, y_level + 0.6, event['year'], ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=event['color'])

        # 标题（下方）
        ax.text(x, y_level - 0.5, event['title'], ha='center', va='top',
                fontsize=13, fontweight='bold')

        # 描述（更下方）
        ax.text(x, y_level - 1.2, event['desc'], ha='center', va='top',
                fontsize=9, color='#555')

    # 添加标题
    ax.text(6.5, 1.5, '计算机视觉发展历程', ha='center', va='center',
            fontsize=18, fontweight='bold')

    # 设置坐标轴
    ax.set_xlim(0, 13)
    ax.set_ylim(-2, 2)
    ax.axis('off')

    # 添加核心任务演变箭头
    ax.annotate('', xy=(2, -1.8), xytext=(5, -1.8),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=2))
    ax.text(3.5, -1.7, '分类', ha='center', fontsize=10, color='#34495e')

    ax.annotate('', xy=(5, -1.8), xytext=(8, -1.8),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=2))
    ax.text(6.5, -1.7, '检测', ha='center', fontsize=10, color='#34495e')

    ax.annotate('', xy=(8, -1.8), xytext=(11, -1.8),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=2))
    ax.text(9.5, -1.7, '分割→生成', ha='center', fontsize=10, color='#34495e')

    plt.tight_layout()
    plt.savefig('images/cv_history_timeline.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("[OK] Created: cv_history_timeline.png")

def create_cv_apps_collage():
    """创建CV应用场景拼图"""
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    fig.suptitle('计算机视觉应用领域', fontsize=18, fontweight='bold', y=0.98)

    # 定义应用场景
    apps = [
        {'name': '自动驾驶', 'desc': '车道检测/行人识别/交通标志', 'color': '#e74c3c', 'icon': '🚗'},
        {'name': '人脸识别', 'desc': '身份验证/门禁/支付', 'color': '#3498db', 'icon': '👤'},
        {'name': '医疗影像', 'desc': 'CT/MRI诊断/肿瘤检测', 'color': '#2ecc71', 'icon': '🏥'},
        {'name': '工业检测', 'desc': '缺陷识别/质量控制', 'color': '#f39c12', 'icon': '🏭'},
        {'name': 'OCR文字识别', 'desc': '文档数字化/车牌识别', 'color': '#9b59b6', 'icon': '📄'},
        {'name': 'AR/VR', 'desc': '虚拟试衣/游戏交互', 'color': '#1abc9c', 'icon': '🥽'},
    ]

    for idx, (ax, app) in enumerate(zip(axes.flat, apps)):
        # 创建背景色块
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=app['color'], alpha=0.2))
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor=app['color'], lw=3))

        # 添加图标和文字
        ax.text(0.5, 0.55, app['icon'], ha='center', va='center', fontsize=50)
        ax.text(0.5, 0.35, app['name'], ha='center', va='center',
                fontsize=14, fontweight='bold')
        ax.text(0.5, 0.15, app['desc'], ha='center', va='center',
                fontsize=9, color='#555')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    plt.tight_layout()
    plt.savefig('images/cv_applications.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("[OK] Created: cv_applications.png")

def create_alexnet_comparison():
    """创建ImageNet/AlexNet对比图片"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 左侧：传统方法
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.text(5, 7, '传统方法', ha='center', fontsize=14, fontweight='bold')
    ax1.text(5, 5, '手工设计特征\n+SVM/随机森林', ha='center', fontsize=11, color='#555')
    ax1.text(5, 2.5, '准确率: ~72%\n(2011年ImageNet)', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#ffebee', edgecolor='#ef5350'))
    ax1.axis('off')

    # 右侧：深度学习
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.text(5, 7, 'AlexNet (2012)', ha='center', fontsize=14, fontweight='bold', color='#e74c3c')
    ax2.text(5, 5, '卷积神经网络(CNN)\n端到端学习', ha='center', fontsize=11, color='#555')
    ax2.text(5, 2.5, '准确率: ~84%\n(top-5: 63.3%)', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#e8f5e8', edgecolor='#2ecc71'))

    # 添加提升箭头
    arrow = FancyArrowPatch((6, 3), (4, 3), arrowstyle='->,head_length=8,head_width=5',
                           mutation_scale=20, color='#27ae60', linewidth=3, zorder=10)
    ax1.add_patch(arrow)
    ax1.text(5, 3.8, '+12%', ha='center', fontsize=12, fontweight='bold', color='#27ae60')

    ax2.axis('off')

    plt.suptitle('ImageNet竞赛：深度学习的突破', fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout()
    plt.savefig('images/alexnet_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("[OK] Created: alexnet_comparison.png")

if __name__ == '__main__':
    import os
    os.makedirs('images', exist_ok=True)

    print("Creating CV history timeline images...")
    create_cv_history_timeline()
    create_cv_apps_collage()
    create_alexnet_comparison()
    print("\nAll images saved to 'images/' directory")
