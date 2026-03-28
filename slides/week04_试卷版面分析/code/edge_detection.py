"""边缘检测模块 -- 试卷版面分析预处理步骤.

本模块实现了试卷图像边缘检测的核心算法，包括灰度转换、高斯模糊预处理、
Sobel 算子梯度计算以及 Canny 边缘检测。同时提供自动阈值计算与多阈值
对比可视化功能，用于在试卷版面分析流程中提取清晰的页面边缘。

Usage::

    from edge_detection import load_and_preprocess, canny_edge_detection, auto_canny

    img, gray, blur = load_and_preprocess("exam.jpg")
    edges = canny_edge_detection(blur)
    auto_edges = auto_canny(blur)

Requirements:
    - opencv-python >= 4.0
    - numpy >= 1.18
    - matplotlib >= 3.3
"""

from typing import List, Optional, Tuple

import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_and_preprocess(image_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """加载图像并执行预处理（灰度转换 + 高斯模糊）。

    Args:
        image_path: 输入图像文件路径。

    Returns:
        包含三个元素的元组:
            - img: 原始 BGR 彩色图像，shape 为 (H, W, 3)。
            - gray: 灰度图像，shape 为 (H, W)。
            - blur: 高斯模糊后的灰度图像，shape 为 (H, W)。

    Raises:
        FileNotFoundError: 当图像文件不存在或无法读取时抛出。
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"找不到图像: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return img, gray, blur


def sobel_edge_detection(gray: np.ndarray) -> np.ndarray:
    """Sobel 边缘检测，计算水平与垂直梯度的合成幅值。

    Args:
        gray: 灰度图像，shape 为 (H, W)，dtype 通常为 uint8。

    Returns:
        sobel: Sobel 梯度幅值图像，dtype 为 uint8，shape 为 (H, W)。
    """
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel = np.uint8(sobel / sobel.max() * 255)
    return sobel


def canny_edge_detection(blur: np.ndarray, threshold1: int = 50, threshold2: int = 150) -> np.ndarray:
    """Canny 边缘检测。

    Args:
        blur: 高斯模糊后的灰度图像，shape 为 (H, W)。
        threshold1: Canny 算法的低阈值，用于弱边缘链接。默认为 50。
        threshold2: Canny 算法的高阈值，用于强边缘检测。默认为 150。

    Returns:
        edges: 二值边缘图像，dtype 为 uint8，shape 为 (H, W)。
    """
    edges = cv2.Canny(blur, threshold1, threshold2)
    return edges


def auto_canny(gray: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """基于图像中值自动计算 Canny 阈值并执行边缘检测。

    利用图像像素中值作为基准，乘以 (1-sigma) 和 (1+sigma) 分别得到
    低阈值和高阈值，自适应地适应不同亮度的图像。

    Args:
        gray: 灰度图像，shape 为 (H, W)。
        sigma: 阈值偏移比例因子。默认为 0.33。

    Returns:
        edges: 二值边缘图像，dtype 为 uint8，shape 为 (H, W)。
    """
    v = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(gray, lower, upper)


def compare_thresholds(blur: np.ndarray) -> None:
    """对比不同 Canny 阈值组合的边缘检测效果。

    使用 2x2 子图展示四组阈值组合的检测结果，并弹出窗口显示。

    Args:
        blur: 高斯模糊后的灰度图像，shape 为 (H, W)。

    Returns:
        None。结果通过 matplotlib 窗口展示。
    """
    thresholds = [(30, 100), (50, 150), (80, 200), (100, 250)]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, (t1, t2) in zip(axes, thresholds):
        edges = cv2.Canny(blur, t1, t2)
        ax.imshow(edges, cmap='gray')
        ax.set_title(f'Canny: ({t1}, {t2})')
        ax.axis('off')

    plt.tight_layout()
    plt.show()


def visualize_sobel_components(gray: np.ndarray) -> None:
    """可视化 Sobel X、Y 分量及合成幅值。

    使用 1x3 子图分别展示垂直边缘（Sobel X）、水平边缘（Sobel Y）
    以及合成梯度幅值，并弹出窗口显示。

    Args:
        gray: 灰度图像，shape 为 (H, W)。

    Returns:
        None。结果通过 matplotlib 窗口展示。
    """
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(np.abs(sobel_x), cmap='gray')
    axes[0].set_title('Sobel X (垂直边缘)')
    axes[0].axis('off')

    axes[1].imshow(np.abs(sobel_y), cmap='gray')
    axes[1].set_title('Sobel Y (水平边缘)')
    axes[1].axis('off')

    sobel = np.sqrt(sobel_x**2 + sobel_y**2)
    axes[2].imshow(sobel, cmap='gray')
    axes[2].set_title('Sobel 幅值')
    axes[2].axis('off')

    plt.show()


if __name__ == "__main__":
    # 示例用法（将 'exam.jpg' 替换为实际图像路径）
    image_path = 'exam.jpg'

    try:
        img, gray, blur = load_and_preprocess(image_path)

        # Canny边缘检测
        edges = canny_edge_detection(blur)
        cv2.imshow('Canny Edges', edges)
        cv2.waitKey(0)

        # 自动阈值
        auto_edges = auto_canny(blur)
        cv2.imshow('Auto Canny', auto_edges)
        cv2.waitKey(0)

        # 对比不同阈值
        compare_thresholds(blur)

        # Sobel分量可视化
        visualize_sobel_components(gray)

        cv2.destroyAllWindows()

    except FileNotFoundError as e:
        print(e)
        print("请准备一张试卷图像并命名为 exam.jpg")
