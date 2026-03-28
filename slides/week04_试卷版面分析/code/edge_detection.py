"""
边缘检测示例代码
- 灰度转换、高斯模糊、Sobel算子、Canny边缘检测
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_and_preprocess(image_path):
    """加载图像并预处理"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"找不到图像: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return img, gray, blur


def sobel_edge_detection(gray):
    """Sobel边缘检测"""
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel = np.uint8(sobel / sobel.max() * 255)
    return sobel


def canny_edge_detection(blur, threshold1=50, threshold2=150):
    """Canny边缘检测"""
    edges = cv2.Canny(blur, threshold1, threshold2)
    return edges


def auto_canny(gray, sigma=0.33):
    """自动计算Canny阈值（基于图像中值）"""
    v = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(gray, lower, upper)


def compare_thresholds(blur):
    """对比不同阈值的Canny效果"""
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


def visualize_sobel_components(gray):
    """可视化Sobel X和Y分量"""
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
