"""
轮廓检测示例代码
- findContours API、轮廓检索模式、绘制轮廓、层级结构
"""

import cv2
import numpy as np


def detect_contours(edges, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE):
    """检测轮廓"""
    contours, hierarchy = cv2.findContours(edges, mode, method)
    return contours, hierarchy


def draw_contours(img, contours, color=(0, 255, 0), thickness=2):
    """绘制所有轮廓"""
    output = img.copy()
    cv2.drawContours(output, contours, -1, color, thickness)
    return output


def draw_single_contour(img, contours, index, color=(0, 0, 255), thickness=3):
    """绘制指定索引的单个轮廓"""
    output = img.copy()
    cv2.drawContours(output, contours, index, color, thickness)
    return output


def fill_contours(img, contours, color=(0, 255, 0)):
    """填充轮廓（线宽=-1）"""
    output = img.copy()
    cv2.drawContours(output, contours, -1, color, -1)
    return output


def compare_retrieval_modes(edges):
    """对比不同检索模式"""
    modes = {
        'RETR_EXTERNAL': cv2.RETR_EXTERNAL,
        'RETR_LIST': cv2.RETR_LIST,
        'RETR_CCOMP': cv2.RETR_CCOMP,
        'RETR_TREE': cv2.RETR_TREE,
    }

    results = {}
    for name, mode in modes.items():
        contours, hierarchy = cv2.findContours(
            edges, mode, cv2.CHAIN_APPROX_SIMPLE)
        results[name] = (contours, hierarchy)
        print(f'{name}: 检测到 {len(contours)} 个轮廓')

    return results


def filter_contours_by_area(contours, min_area=100, max_area=10000):
    """按面积筛选轮廓"""
    filtered = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area <= area <= max_area:
            filtered.append(contour)
    return filtered


def filter_contours_by_position(contours, img_shape, margin=50):
    """按位置筛选（排除图像边缘区域）"""
    h, w = img_shape[:2]
    filtered = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        if x > margin and y > margin and (x + cw) < (w - margin) and (y + ch) < (h - margin):
            filtered.append(contour)
    return filtered


def analyze_hierarchy(hierarchy):
    """分析轮廓层级结构"""
    if hierarchy is None:
        return

    hierarchy = hierarchy[0]
    for i, h in enumerate(hierarchy):
        next_c, prev_c, child_c, parent_c = h
        print(f"轮廓 {i}: next={next_c}, prev={prev_c}, child={child_c}, parent={parent_c}")


def contour_detection_pipeline(img_path, show_steps=True):
    """完整轮廓检测流程"""
    # 1. 加载图像
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 预处理
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. 边缘检测
    edges = cv2.Canny(blur, 50, 150)

    # 4. 轮廓检测
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 5. 筛选
    filtered = filter_contours_by_area(contours, min_area=500)

    # 6. 绘制
    output = img.copy()
    cv2.drawContours(output, filtered, -1, (0, 255, 0), 2)

    print(f"原始轮廓数: {len(contours)}")
    print(f"筛选后轮廓数: {len(filtered)}")

    if show_steps:
        cv2.imshow('Edges', edges)
        cv2.imshow('Contours', output)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return output, contours, filtered


if __name__ == "__main__":
    image_path = 'exam.jpg'

    try:
        output, contours, filtered = contour_detection_pipeline(image_path)

        # 对比不同检索模式
        blur = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(blur, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        results = compare_retrieval_modes(edges)

        cv2.destroyAllWindows()

    except FileNotFoundError:
        print("请准备一张试卷图像并命名为 exam.jpg")
