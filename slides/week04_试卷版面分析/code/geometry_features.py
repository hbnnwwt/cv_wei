"""形状特征与试卷定位模块 -- 试卷版面分析几何特征提取.

本模块实现了轮廓的几何特征计算与试卷定位功能，包括面积、周长、边界矩形、
多边形逼近、凸包、凸缺陷、Hu 矩、形状匹配等。在此基础上提供了试卷轮廓
检测与四点透视变换矫正功能，用于从倾斜拍摄的试卷图像中提取正视的试卷区域。

Usage::

    from geometry_features import compute_contour_features, find_paper_contour, extract_paper

    warped = extract_paper("exam.jpg")

Requirements:
    - opencv-python >= 4.0
    - numpy >= 1.18
"""

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np


def compute_contour_features(contour: np.ndarray) -> Dict[str, Any]:
    """计算轮廓的常用几何特征。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。

    Returns:
        features: 包含以下键的字典:
            - 'area': 轮廓面积（float）。
            - 'perimeter': 轮廓周长（float）。
            - 'bbox': 直立边界矩形 (x, y, w, h)。
            - 'aspect_ratio': 宽高比（float），高为 0 时返回 0。
            - 'min_rect': 最小外接旋转矩形，cv2.RotatedRect 对象。
            - 'circle_center': 最小外接圆圆心 (cx, cy)。
            - 'circle_radius': 最小外接圆半径（float）。
    """
    features = {}

    # 面积
    features['area'] = cv2.contourArea(contour)

    # 周长
    features['perimeter'] = cv2.arcLength(contour, True)

    # 边界矩形（直立）
    x, y, w, h = cv2.boundingRect(contour)
    features['bbox'] = (x, y, w, h)
    features['aspect_ratio'] = w / h if h > 0 else 0

    # 最小外接矩形（旋转）
    rect = cv2.minAreaRect(contour)
    features['min_rect'] = rect

    # 最小外接圆
    (cx, cy), radius = cv2.minEnclosingCircle(contour)
    features['circle_center'] = (cx, cy)
    features['circle_radius'] = radius

    return features


def polygon_approximation(
    contour: np.ndarray,
    epsilon_multiplier: float = 0.02,
) -> Tuple[np.ndarray, int]:
    """使用 Douglas-Peucker 算法对轮廓进行多边形逼近。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。
        epsilon_multiplier: 逼近精度系数，实际 epsilon 为该系数乘以轮廓周长。
                           值越大逼近越粗略，顶点越少。默认为 0.02。

    Returns:
        包含两个元素的元组:
            - approx: 逼近后的多边形轮廓，shape 为 (M, 1, 2) 的 ndarray。
            - num_vertices: 逼近后多边形的顶点数（int）。
    """
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon_multiplier * peri, True)
    return approx, len(approx)


def is_quadrilateral(contour: np.ndarray, tolerance: float = 0.05) -> bool:
    """判断轮廓是否为四边形。

    通过多边形逼近检测顶点数是否为 4，可用于判断试卷轮廓是否为矩形。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。
        tolerance: 多边形逼近的精度系数。默认为 0.05。

    Returns:
        True 如果轮廓为四边形，否则 False。
    """
    approx, num_vertices = polygon_approximation(contour, tolerance)
    return num_vertices == 4


def compute_convex_hull(contour: np.ndarray) -> Tuple[np.ndarray, float]:
    """计算轮廓的凸包及实心度。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。

    Returns:
        包含两个元素的元组:
            - hull: 凸包轮廓，shape 为 (M, 1, 2) 的 ndarray。
            - solidity: 实心度（float），即轮廓面积与凸包面积之比；
                       凸包面积为 0 时返回 0。
    """
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    contour_area = cv2.contourArea(contour)
    solidity = contour_area / hull_area if hull_area > 0 else 0
    return hull, solidity


def compute_convexity_defects(contour: np.ndarray) -> Optional[np.ndarray]:
    """计算轮廓的凸缺陷。

    凸缺陷描述了轮廓相对于其凸包的凹陷区域，返回每个缺陷的起点、终点、
    最远点索引及深度。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。

    Returns:
        defects: 凸缺陷数组，shape 为 (K, 1, 4)，每行包含
                 [起点索引, 终点索引, 最远点索引, 深度（固定点数表示）]；
                 若凸包顶点不足 3 个则返回 None。
    """
    hull = cv2.convexHull(contour, returnPoints=False)
    if hull is None or len(hull) < 3:
        return None
    defects = cv2.convexityDefects(contour, hull)
    return defects


def compute_hu_moments(contour: np.ndarray) -> np.ndarray:
    """计算轮廓的 Hu 矩（七个不变矩）。

    Hu 矩具有旋转、缩放和平移不变性，可用于形状匹配与识别。

    Args:
        contour: 输入轮廓，shape 为 (N, 1, 2) 的 ndarray。

    Returns:
        hu_moments: 七个 Hu 矩组成的数组，shape 为 (7, 1)，dtype 为 float32。
    """
    moments = cv2.moments(contour)
    hu_moments = cv2.HuMoments(moments)
    return hu_moments


def match_shapes(contour1: np.ndarray, contour2: np.ndarray) -> float:
    """计算两个轮廓之间的形状相似度。

    使用 cv2.CONTOURS_MATCH_I1 方法（基于 Hu 矩），返回值越小表示
    两个轮廓形状越相似。

    Args:
        contour1: 第一个轮廓，shape 为 (N1, 1, 2) 的 ndarray。
        contour2: 第二个轮廓，shape 为 (N2, 1, 2) 的 ndarray。

    Returns:
        match: 匹配距离（float），值越接近 0 表示越相似。
    """
    match = cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I1, 0.0)
    return match


def find_paper_contour(
    contours: List[np.ndarray],
    image_area: int,
) -> Optional[np.ndarray]:
    """从轮廓列表中查找试卷轮廓（四边形且面积占图像 50% 以上）。

    遍历所有轮廓，筛选面积超过图像总面积 50% 且多边形逼近后为四边形的
    轮廓，返回第一个匹配的逼近结果。

    Args:
        contours: 轮廓列表，每个轮廓为 shape (N, 1, 2) 的 ndarray。
        image_area: 图像总面积（像素数），通常为 H * W。

    Returns:
        paper_contour: 匹配到的四边形逼近轮廓，shape 为 (4, 1, 2)；
                      若未找到则返回 None。
    """
    for contour in contours:
        area = cv2.contourArea(contour)

        # 面积筛选：试卷应该占图像的50%以上
        if area > image_area * 0.5:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # 如果是四边形（可能是试卷）
            if len(approx) == 4:
                return approx

    return None


def four_point_transform(
    img: np.ndarray,
    pts: np.ndarray,
) -> np.ndarray:
    """四点透视变换，将倾斜的试卷区域矫正为正视矩形。

    根据四个角点计算透视变换矩阵，将试卷区域映射到标准的轴对齐矩形。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        pts: 四个角点坐标，shape 为 (4, 2) 或 (4, 1, 2) 的 ndarray。

    Returns:
        warped: 透视变换矫正后的 BGR 图像。
    """
    rect = np.array(pts, dtype=np.float32)
    rect = rect.reshape(4, 2)

    # 按左上、右上、右下、左下排序
    rect = sorted(rect, key=lambda x: x[1])  # 按y排序
    top_pts = sorted(rect[:2], key=lambda x: x[0])  # y小的两个按x排序
    bottom_pts = sorted(rect[2:], key=lambda x: x[0], reverse=True)  # y大的两个按x排序

    pts_sorted = np.array(top_pts + bottom_pts, dtype=np.float32)

    # 计算目标宽高
    width = int(max(np.linalg.norm(pts_sorted[0] - pts_sorted[1]),
                     np.linalg.norm(pts_sorted[2] - pts_sorted[3])))
    height = int(max(np.linalg.norm(pts_sorted[0] - pts_sorted[3]),
                     np.linalg.norm(pts_sorted[1] - pts_sorted[2])))

    dst = np.array([[0, 0], [width - 1, 0],
                    [width - 1, height - 1], [0, height - 1]], dtype=np.float32)

    M = cv2.getPerspectiveTransform(pts_sorted, dst)
    warped = cv2.warpPerspective(img, M, (width, height))
    return warped


def extract_paper(
    img_path: str,
    show_debug: bool = True,
) -> Optional[np.ndarray]:
    """从图像中提取并矫正试卷区域。

    完整流程：加载图像 -> 灰度转换 -> 高斯模糊 -> Canny 边缘检测 ->
    轮廓检测 -> 试卷轮廓匹配 -> 四点透视变换矫正。

    Args:
        img_path: 输入图像文件路径。
        show_debug: 是否显示检测到的试卷轮廓与矫正结果。默认为 True。

    Returns:
        warped: 矫正后的试卷 BGR 图像；若未找到试卷轮廓则返回 None。
    """
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    image_area = gray.shape[0] * gray.shape[1]
    paper_contour = find_paper_contour(contours, image_area)

    if paper_contour is None:
        print("未找到试卷轮廓")
        return None

    # 透视变换矫正
    warped = four_point_transform(img, paper_contour)

    if show_debug:
        debug_img = img.copy()
        cv2.drawContours(debug_img, [paper_contour], -1, (0, 255, 0), 3)
        cv2.imshow('Detected Paper', debug_img)
        cv2.imshow('Warped Paper', warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return warped


if __name__ == "__main__":
    image_path = 'exam.jpg'

    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        print(f"检测到 {len(contours)} 个轮廓")

        for i, contour in enumerate(contours):
            features = compute_contour_features(contour)
            print(f"\n轮廓 {i}:")
            print(f"  面积: {features['area']:.1f}")
            print(f"  周长: {features['perimeter']:.1f}")
            print(f"  宽高比: {features['aspect_ratio']:.2f}")

            approx, n_vertices = polygon_approximation(contour)
            print(f"  顶点数: {n_vertices} -> {['三角形', '四边形', '多边形'][min(n_vertices - 3, 2)] if n_vertices <= 5 else '多边形'}")

        # 提取试卷
        warped = extract_paper(image_path, show_debug=True)

    except FileNotFoundError:
        print("请准备一张试卷图像并命名为 exam.jpg")
