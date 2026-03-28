"""轮廓检测模块 -- 试卷版面分析核心组件.

本模块封装了 OpenCV findContours API 的常用操作，包括轮廓检测、绘制、
填充、按面积与位置筛选，以及不同检索模式（RETR_EXTERNAL / RETR_LIST /
RETR_CCOMP / RETR_TREE）的对比分析。层级结构解析功能用于理解嵌套轮廓
之间的父子关系，适用于试卷中答题区域与定位标记的分层提取。

Usage::

    from contour_detection import detect_contours, filter_contours_by_area

    contours, hierarchy = detect_contours(edges)
    filtered = filter_contours_by_area(contours, min_area=500)

Requirements:
    - opencv-python >= 4.0
    - numpy >= 1.18
"""

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


def detect_contours(
    edges: np.ndarray,
    mode: int = cv2.RETR_EXTERNAL,
    method: int = cv2.CHAIN_APPROX_SIMPLE,
) -> Tuple[List[np.ndarray], Optional[np.ndarray]]:
    """在二值图像中检测轮廓。

    Args:
        edges: 二值边缘图像，shape 为 (H, W)，非零像素视为边缘。
        mode: 轮廓检索模式，支持 cv2.RETR_EXTERNAL、RETR_LIST、
              RETR_CCOMP、RETR_TREE 等。默认为 RETR_EXTERNAL。
        method: 轮廓逼近方法，支持 cv2.CHAIN_APPROX_SIMPLE、
                CHAIN_APPROX_NONE 等。默认为 CHAIN_APPROX_SIMPLE。

    Returns:
        包含两个元素的元组:
            - contours: 检测到的轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
            - hierarchy: 轮廓层级信息，shape 为 (1, N, 4) 的 ndarray；
                        若无层级信息则为 None。
    """
    contours, hierarchy = cv2.findContours(edges, mode, method)
    return contours, hierarchy


def draw_contours(
    img: np.ndarray,
    contours: List[np.ndarray],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """在图像副本上绘制所有轮廓。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        color: 轮廓绘制颜色（B, G, R）。默认为绿色 (0, 255, 0)。
        thickness: 轮廓线宽（像素）。默认为 2。

    Returns:
        output: 绘制了轮廓的 BGR 图像副本，shape 为 (H, W, 3)。
    """
    output = img.copy()
    cv2.drawContours(output, contours, -1, color, thickness)
    return output


def draw_single_contour(
    img: np.ndarray,
    contours: List[np.ndarray],
    index: int,
    color: Tuple[int, int, int] = (0, 0, 255),
    thickness: int = 3,
) -> np.ndarray:
    """在图像副本上绘制指定索引的单个轮廓。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        index: 要绘制的轮廓索引，若为 -1 则绘制所有轮廓。
        color: 轮廓绘制颜色（B, G, R）。默认为红色 (0, 0, 255)。
        thickness: 轮廓线宽（像素）。默认为 3。

    Returns:
        output: 绘制了指定轮廓的 BGR 图像副本，shape 为 (H, W, 3)。
    """
    output = img.copy()
    cv2.drawContours(output, contours, index, color, thickness)
    return output


def fill_contours(
    img: np.ndarray,
    contours: List[np.ndarray],
    color: Tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """在图像副本上填充所有轮廓内部区域。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        color: 填充颜色（B, G, R）。默认为绿色 (0, 255, 0)。

    Returns:
        output: 填充了轮廓区域的 BGR 图像副本，shape 为 (H, W, 3)。
    """
    output = img.copy()
    cv2.drawContours(output, contours, -1, color, -1)
    return output


def compare_retrieval_modes(edges: np.ndarray) -> Dict[str, Tuple[List[np.ndarray], Optional[np.ndarray]]]:
    """对比不同轮廓检索模式的检测结果。

    依次使用 RETR_EXTERNAL、RETR_LIST、RETR_CCOMP、RETR_TREE 四种
    模式检测轮廓，并将结果汇总返回，同时在控制台输出各模式检测到的轮廓数。

    Args:
        edges: 二值边缘图像，shape 为 (H, W)。

    Returns:
        results: 字典，键为模式名称字符串，值为 (contours, hierarchy) 元组。
    """
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


def filter_contours_by_area(
    contours: List[np.ndarray],
    min_area: float = 100,
    max_area: float = 10000,
) -> List[np.ndarray]:
    """按面积范围筛选轮廓。

    Args:
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        min_area: 最小面积阈值（含）。默认为 100。
        max_area: 最大面积阈值（含）。默认为 10000。

    Returns:
        filtered: 面积在 [min_area, max_area] 范围内的轮廓列表。
    """
    filtered = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area <= area <= max_area:
            filtered.append(contour)
    return filtered


def filter_contours_by_position(
    contours: List[np.ndarray],
    img_shape: Tuple[int, ...],
    margin: int = 50,
) -> List[np.ndarray]:
    """按位置筛选轮廓，排除靠近图像边缘的轮廓。

    Args:
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        img_shape: 图像形状，通常为 (H, W) 或 (H, W, C)。
        margin: 边缘排除边距（像素）。轮廓边界框在图像四周 margin 像素
                范围内将被过滤。默认为 50。

    Returns:
        filtered: 边界框完全位于图像内部（距边缘 >= margin）的轮廓列表。
    """
    h, w = img_shape[:2]
    filtered = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        if x > margin and y > margin and (x + cw) < (w - margin) and (y + ch) < (h - margin):
            filtered.append(contour)
    return filtered


def analyze_hierarchy(hierarchy: Optional[np.ndarray]) -> None:
    """分析并打印轮廓层级结构信息。

    对每个轮廓输出其 next、prev、child、parent 索引，
    用于理解嵌套轮廓之间的拓扑关系。

    Args:
        hierarchy: findContours 返回的层级数组，shape 为 (1, N, 4)；
                   若为 None 则直接返回，不输出任何内容。

    Returns:
        None。结果通过 print 输出到控制台。
    """
    if hierarchy is None:
        return

    hierarchy = hierarchy[0]
    for i, h in enumerate(hierarchy):
        next_c, prev_c, child_c, parent_c = h
        print(f"轮廓 {i}: next={next_c}, prev={prev_c}, child={child_c}, parent={parent_c}")


def contour_detection_pipeline(
    img_path: str,
    show_steps: bool = True,
) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
    """完整的轮廓检测流程：加载 -> 模糊 -> Canny -> 检测 -> 筛选 -> 绘制。

    Args:
        img_path: 输入图像文件路径。
        show_steps: 是否在窗口中显示中间步骤（边缘图与轮廓图）。默认为 True。

    Returns:
        包含三个元素的元组:
            - output: 绘制了筛选后轮廓的 BGR 图像，shape 为 (H, W, 3)。
            - contours: 原始检测到的所有轮廓列表。
            - filtered: 按面积筛选后的轮廓列表。
    """
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
