"""版面分析模块 -- 试卷版面结构化解析.

本模块实现了基于投影法与连通域分析的试卷版面解析功能，包括水平/垂直投影
计算、投影波形绘制、分隔线定位（波谷检测）、题目区域分割、连通域标记与
筛选、选择题气泡检测，以及完整的版面分析流水线。适用于将试卷图像自动
划分为独立的题目区域并定位填涂标记。

Usage::

    from layout_analysis import full_layout_pipeline

    regions, blobs = full_layout_pipeline("exam.jpg")

Requirements:
    - opencv-python >= 4.0
    - numpy >= 1.18
    - matplotlib >= 3.3
"""

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import matplotlib.pyplot as plt


def horizontal_projection(binary: np.ndarray) -> np.ndarray:
    """计算二值图像的水平投影（每行白色像素数）。

    将二值图像中值为 255 的像素视为前景（白色），统计每行的白色像素数量，
    得到一个一维投影数组。

    Args:
        binary: 二值图像，shape 为 (H, W)，前景像素值为 255。

    Returns:
        proj: 水平投影数组，shape 为 (H,)，dtype 为 int64，
              每个元素为对应行的白色像素数。
    """
    binary = binary // 255
    proj = np.sum(binary, axis=1)
    return proj


def vertical_projection(binary: np.ndarray) -> np.ndarray:
    """计算二值图像的垂直投影（每列白色像素数）。

    将二值图像中值为 255 的像素视为前景（白色），统计每列的白色像素数量，
    得到一个一维投影数组。

    Args:
        binary: 二值图像，shape 为 (H, W)，前景像素值为 255。

    Returns:
        proj: 垂直投影数组，shape 为 (W,)，dtype 为 int64，
              每个元素为对应列的白色像素数。
    """
    binary = binary // 255
    proj = np.sum(binary, axis=0)
    return proj


def plot_projection(proj: np.ndarray, direction: str = 'horizontal') -> None:
    """绘制投影波形图。

    Args:
        proj: 一维投影数组。
        direction: 投影方向，用于设置标题和 x 轴标签。
                   可选 'horizontal' 或 'vertical'。默认为 'horizontal'。

    Returns:
        None。结果通过 matplotlib 窗口展示。
    """
    plt.figure(figsize=(10, 4))
    plt.plot(proj, linewidth=1.5)
    plt.title(f'{direction} Projection')
    plt.xlabel('Row' if direction == 'horizontal' else 'Column')
    plt.ylabel('White Pixel Count')
    plt.grid(True, alpha=0.3)
    plt.show()


def find_divider_lines(
    proj: np.ndarray,
    threshold: float = 10,
    min_length: int = 5,
) -> List[Tuple[int, int]]:
    """在投影数组中找到分隔线（波谷：投影值低于阈值的连续区域）。

    扫描投影数组，定位连续低于阈值的区间，作为题目之间的分隔线位置。

    Args:
        proj: 一维投影数组。
        threshold: 波谷判定阈值，投影值低于此值视为空白行。默认为 10。
        min_length: 分隔线的最小连续长度（行/列数）。默认为 5。

    Returns:
        dividers: 分隔线位置列表，每个元素为 (start, end) 元组，
                  表示投影值低于阈值的连续区间。
    """
    dividers = []
    current_start = None

    for i, value in enumerate(proj):
        if value < threshold:
            if current_start is None:
                current_start = i
        else:
            if current_start is not None:
                length = i - current_start
                if length >= min_length:
                    dividers.append((current_start, i))
                current_start = None

    # 处理末尾
    if current_start is not None:
        length = len(proj) - current_start
        if length >= min_length:
            dividers.append((current_start, len(proj)))

    return dividers


def layout_analysis(
    binary: np.ndarray,
) -> Tuple[List[Tuple[int, int]], np.ndarray, List[Tuple[int, int]]]:
    """基于水平投影的版面分析：找到题目分隔线并计算各题目区域。

    使用自适应阈值（投影平均值的 10%）作为波谷判定标准，定位分隔线后
    将图像在垂直方向上划分为若干题目区域。

    Args:
        binary: 二值图像，shape 为 (H, W)，前景像素值为 255。

    Returns:
        包含三个元素的元组:
            - regions: 题目区域列表，每个元素为 (row_start, row_end) 元组。
            - h_proj: 水平投影数组，shape 为 (H,)。
            - dividers: 分隔线位置列表，每个元素为 (start, end) 元组。
    """
    # 水平投影
    h_proj = horizontal_projection(binary)

    # 自适应阈值：波谷阈值为平均值的10%
    threshold = np.mean(h_proj) * 0.1
    dividers = find_divider_lines(h_proj, threshold)

    # 计算题目区域
    regions = []
    prev_end = 0
    for start, end in dividers:
        if start > prev_end:
            regions.append((prev_end, start))
        prev_end = end

    # 最后一个区域
    if prev_end < binary.shape[0]:
        regions.append((prev_end, binary.shape[0]))

    return regions, h_proj, dividers


def connected_components_analysis(
    binary: np.ndarray,
    min_area: int = 100,
    max_area: int = 5000,
) -> List[Dict[str, Any]]:
    """连通域分析：标记并筛选二值图像中的连通区域。

    使用 8-连通性标记图像中的连通域，并按面积范围筛选出有效的连通区域。

    Args:
        binary: 二值图像，shape 为 (H, W)，前景像素值非零。
        min_area: 最小面积阈值（含）。默认为 100。
        max_area: 最大面积阈值（含）。默认为 5000。

    Returns:
        blobs: 筛选后的连通域列表，每个元素为字典，包含:
            - 'label': 连通域标签编号（int）。
            - 'bbox': 边界矩形 (x, y, w, h)。
            - 'area': 连通域面积（int）。
            - 'centroid': 质心坐标 (cx, cy)。
    """
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary, connectivity=8)

    # stats: [x, y, width, height, area]
    blobs = []
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        cx, cy = centroids[i]
        if min_area <= area <= max_area:
            blobs.append({'label': i, 'bbox': (x, y, w, h),
                          'area': area, 'centroid': (cx, cy)})
    return blobs


def detect_choice_bubbles(
    blobs: List[Dict[str, Any]],
    expected_count: int = 5,
) -> List[Dict[str, Any]]:
    """从连通域中检测选择题填涂气泡。

    根据面积范围（100~1000 像素）筛选可能是填涂气泡的连通域。

    Args:
        blobs: 连通域列表，每个元素为包含 'area' 键的字典。
        expected_count: 预期每题选项数量，当前未使用，保留接口。默认为 5。

    Returns:
        bubbles: 可能是填涂气泡的连通域列表。
    """
    bubbles = []

    for blob in blobs:
        area = blob['area']
        # 气泡面积一般在100-1000像素
        if 100 < area < 1000:
            bubbles.append(blob)

    return bubbles


def draw_layout_regions(
    img: np.ndarray,
    regions: List[Tuple[int, int]],
    color: Tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """在图像上绘制版面区域分割结果。

    用矩形框标注每个题目区域的垂直范围，并添加区域编号标签。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        regions: 题目区域列表，每个元素为 (row_start, row_end) 元组。
        color: 矩形框与标签颜色（B, G, R）。默认为绿色 (0, 255, 0)。

    Returns:
        output: 绘制了区域分割结果的 BGR 图像副本，shape 为 (H, W, 3)。
    """
    output = img.copy()
    for i, (start, end) in enumerate(regions):
        cv2.rectangle(output, (0, start), (img.shape[1], end),
                      color, 2)
        label = f'Region {i + 1}'
        cv2.putText(output, label, (5, start + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return output


def draw_connected_components(
    img: np.ndarray,
    blobs: List[Dict[str, Any]],
    color: Tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """在图像上绘制连通域的边界框与质心。

    Args:
        img: 输入 BGR 图像，shape 为 (H, W, 3)。
        blobs: 连通域列表，每个元素包含 'bbox' 和 'centroid' 键。
        color: 边界框颜色（B, G, R）。默认为绿色 (0, 255, 0)。

    Returns:
        output: 绘制了连通域的 BGR 图像副本，shape 为 (H, W, 3)。
    """
    output = img.copy()
    for blob in blobs:
        x, y, w, h = blob['bbox']
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        cx, cy = blob['centroid']
        cv2.circle(output, (int(cx), int(cy)), 3, (0, 0, 255), -1)
    return output


def full_layout_pipeline(
    img_path: str,
    show_debug: bool = True,
) -> Tuple[List[Tuple[int, int]], List[Dict[str, Any]]]:
    """完整的版面分析流水线。

    流程: 加载图像 -> 灰度转换 -> 自适应二值化 -> 水平投影版面分析 ->
    连通域分析 -> 气泡检测 -> 可视化。

    Args:
        img_path: 输入图像文件路径。
        show_debug: 是否显示中间结果（投影波形、区域分割、连通域）。默认为 True。

    Returns:
        包含两个元素的元组:
            - regions: 题目区域列表，每个元素为 (row_start, row_end) 元组。
            - blobs: 连通域列表，每个元素为包含标签、边界框、面积、质心的字典。
    """
    # 1. 加载图像
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 二值化
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2)

    # 3. 投影法版面分析
    regions, h_proj, dividers = layout_analysis(binary)
    print(f"检测到 {len(regions)} 个题目区域")

    # 4. 连通域分析
    blobs = connected_components_analysis(binary)
    bubbles = detect_choice_bubbles(blobs)
    print(f"检测到 {len(bubbles)} 个可能的气泡")

    if show_debug:
        # 显示投影波形
        plot_projection(h_proj, 'horizontal')

        # 显示区域分割结果
        region_img = draw_layout_regions(img, regions)
        cv2.imshow('Layout Regions', region_img)

        # 显示连通域
        blob_img = draw_connected_components(img, blobs)
        cv2.imshow('Connected Components', blob_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return regions, blobs


if __name__ == "__main__":
    image_path = 'exam.jpg'

    try:
        regions, blobs = full_layout_pipeline(image_path)

    except FileNotFoundError:
        print("请准备一张试卷图像并命名为 exam.jpg")
