#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化深度学习对比图 - AlexNet突破
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib
matplotlib.use('Agg')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_alexnet_comparison_v2():
    """创建更美观的AlexNet对比图"""
    fig = plt.figure(figsize=(14, 7))

    # 创建网格布局
    gs = fig.add_gridspec(2, 3, height_ratios=[2, 1], hspace=0.3, wspace=0.3)

    # 左侧：传统方法
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)

    # 传统方法背景
    ax1.add_patch(plt.Rectangle((0.5, 0.5), 9, 9, facecolor='#f5f5f5', edgecolor='#bdc3c7', lw=3, zorder=1))
    ax1.text(5, 8, '2011', ha='center', fontsize=28, fontweight='bold', color='#7f8c8d')
    ax1.text(5, 6.5, '传统方法', ha='center', fontsize=16, fontweight='bold')
    ax1.text(5, 4.5, 'SIFT/HOG特征\n+\nSVM/随机森林', ha='center', fontsize=11, color='#555', linespacing=1.5)

    # 准确率柱状图
    ax1.bar(3, 72, width=4, color='#95a5a6', edgecolor='#7f8c8d', lw=2)
    ax1.text(5, 75, '72%', ha='center', fontsize=14, fontweight='bold', color='#7f8c8d')
    ax1.set_ylim(0, 100)
    ax1.axis('off')

    # 中间：VS
    ax_mid = fig.add_subplot(gs[0, 1])
    ax_mid.text(5, 6, 'VS', ha='center', fontsize=30, fontweight='bold', color='#e74c3c')
    ax_mid.text(5, 3, '+12%', ha='center', fontsize=20, fontweight='bold', color='#27ae60')
    ax_mid.set_xlim(0, 10)
    ax_mid.set_ylim(0, 10)
    ax_mid.axis('off')

    # 右侧：AlexNet
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)

    # AlexNet背景 - 使用渐变效果
    ax2.add_patch(plt.Rectangle((0.5, 0.5), 9, 9, facecolor='#fff5f5', edgecolor='#e74c3c', lw=3, zorder=1))
    ax2.text(5, 8, '2012', ha='center', fontsize=28, fontweight='bold', color='#e74c3c')
    ax2.text(5, 6.5, 'AlexNet', ha='center', fontsize=16, fontweight='bold', color='#e74c3c')
    ax2.text(5, 4.5, '卷积神经网络\n(CNN)\n端到端学习', ha='center', fontsize=11, color='#c0392b', linespacing=1.5)

    # 准确率柱状图 - 更高
    ax2.bar(3, 84, width=4, color='#e74c3c', edgecolor='#c0392b', lw=2)
    ax2.text(5, 87, '84%', ha='center', fontsize=14, fontweight='bold', color='#e74c3c')
    ax2.set_ylim(0, 100)
    ax2.axis('off')

    # 底部：时间线和关键信息
    ax_bottom = fig.add_subplot(gs[1, :])
    ax_bottom.set_xlim(0, 14)
    ax_bottom.set_ylim(0, 3)

    # 绘制时间线
    ax_bottom.plot([1, 13], [1.5, 1.5], 'k-', linewidth=2, alpha=0.3)

    # 时间节点
    years = [(2, '2010', '72%'), (5, '2011', '72%'), (8, '2012', '84%'), (11, '2013', '88%')]
    for x, year, acc in years:
        ax_bottom.plot(x, 1.5, 'o', markersize=12, color='#3498db' if year != '2012' else '#e74c3c')
        ax_bottom.text(x, 2.5, year, ha='center', fontsize=11, fontweight='bold')
        ax_bottom.text(x, 0.8, acc, ha='center', fontsize=10, color='#7f8c8d')

    # 标注2012突破
    ax_bottom.annotate('', xy=(8, 1.5), xytext=(5, 1.5),
                      arrowprops=dict(arrowstyle='->', color='#27ae60', lw=2))
    ax_bottom.text(6.5, 2.1, '深度学习突破!', ha='center', fontsize=10, fontweight='bold', color='#27ae60')

    # 底部说明
    ax_bottom.text(7, 0.3, 'ImageNet Top-5 准确率', ha='center', fontsize=10, color='#7f8c8d')

    ax_bottom.axis('off')

    plt.suptitle('ImageNet 竞赛：深度学习的"AlphaGo时刻"', fontsize=18, fontweight='bold', y=0.98)

    plt.savefig('images/alexnet_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("[OK] Created: alexnet_comparison.png")


def create_imagenet_accuracy_chart():
    """创建ImageNet准确率发展趋势图"""
    fig, ax = plt.subplots(figsize=(12, 5))

    # 数据
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
    accuracies = [72, 72, 84, 88, 92, 95, 97, 98]

    # 绘制柱状图
    colors = ['#95a5a6' if y < 2012 else '#3498db' for y in years]
    bars = ax.bar(years, accuracies, color=colors, edgecolor='white', lw=2, width=0.6)

    # 标注关键节点
    ax.annotate('AlexNet\n深度学习突破!', xy=(2012, 84), xytext=(2012, 60),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                fontsize=11, fontweight='bold', color='#e74c3c',
                ha='center')

    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('Top-5 准确率 (%)', fontsize=12)
    ax.set_title('ImageNet 竞赛：深度学习带来的准确率飙升', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.set_xticks(years)
    ax.grid(axis='y', alpha=0.3)

    # 添加准确率标签
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{acc}%', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig('images/imagenet_trend.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("[OK] Created: imagenet_trend.png")


if __name__ == '__main__':
    import os
    os.makedirs('images', exist_ok=True)

    print("Optimizing AlexNet comparison chart...")
    create_alexnet_comparison_v2()
    create_imagenet_accuracy_chart()
    print("\nDone!")
