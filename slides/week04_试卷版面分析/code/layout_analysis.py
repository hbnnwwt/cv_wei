"""
版面分析示例代码
- 水平/垂直投影、连通域分析、区域定位
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


def horizontal_projection(binary):
    """水平投影：统计每行白色像素数"""
    binary = binary // 255
    proj = np.sum(binary, axis=1)
    return proj


def vertical_projection(binary):
    """垂直投影：统计每列白色像素数"""
    binary = binary // 255
    proj = np.sum(binary, axis=0)
    return proj


def plot_projection(proj, direction='horizontal'):
    """绘制投影波形"""
    plt.figure(figsize=(10, 4))
    plt.plot(proj, linewidth=1.5)
    plt.title(f'{direction} Projection')
    plt.xlabel('Row' if direction == 'horizontal' else 'Column')
    plt.ylabel('White Pixel Count')
    plt.grid(True, alpha=0.3)
    plt.show()


def find_divider_lines(proj, threshold=10, min_length=5):
    """找到分隔线（波谷：投影值低于阈值的连续区域）"""
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


def layout_analysis(binary):
    """版面分析：找到题目分隔线"""
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


def connected_components_analysis(binary, min_area=100, max_area=5000):
    """连通域分析"""
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


def detect_choice_bubbles(blobs, expected_count=5):
    """检测选择题填涂气泡（根据面积和排列）"""
    bubbles = []

    for blob in blobs:
        area = blob['area']
        # 气泡面积一般在100-1000像素
        if 100 < area < 1000:
            bubbles.append(blob)

    return bubbles


def draw_layout_regions(img, regions, color=(0, 255, 0)):
    """在图像上绘制版面区域"""
    output = img.copy()
    for i, (start, end) in enumerate(regions):
        cv2.rectangle(output, (0, start), (img.shape[1], end),
                      color, 2)
        label = f'Region {i + 1}'
        cv2.putText(output, label, (5, start + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return output


def draw_connected_components(img, blobs, color=(0, 255, 0)):
    """绘制连通域"""
    output = img.copy()
    for blob in blobs:
        x, y, w, h = blob['bbox']
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        cx, cy = blob['centroid']
        cv2.circle(output, (int(cx), int(cy)), 3, (0, 0, 255), -1)
    return output


def full_layout_pipeline(img_path, show_debug=True):
    """完整版面分析流程"""
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
