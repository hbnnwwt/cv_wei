"""
形状特征与试卷定位示例代码
- 面积、周长、边界矩形、多边形逼近、凸包、形状匹配
"""

import cv2
import numpy as np


def compute_contour_features(contour):
    """计算轮廓的常用几何特征"""
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


def polygon_approximation(contour, epsilon_multiplier=0.02):
    """多边形逼近"""
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon_multiplier * peri, True)
    return approx, len(approx)


def is_quadrilateral(contour, tolerance=0.05):
    """判断轮廓是否为四边形（试卷）"""
    approx, num_vertices = polygon_approximation(contour, tolerance)
    return num_vertices == 4


def compute_convex_hull(contour):
    """计算凸包"""
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    contour_area = cv2.contourArea(contour)
    solidity = contour_area / hull_area if hull_area > 0 else 0
    return hull, solidity


def compute_convexity_defects(contour):
    """计算凸缺陷（需要先获取凸包索引）"""
    hull = cv2.convexHull(contour, returnPoints=False)
    if hull is None or len(hull) < 3:
        return None
    defects = cv2.convexityDefects(contour, hull)
    return defects


def compute_hu_moments(contour):
    """计算Hu矩（旋转、缩放、平移不变）"""
    moments = cv2.moments(contour)
    hu_moments = cv2.HuMoments(moments)
    return hu_moments


def match_shapes(contour1, contour2):
    """形状匹配（返回值越小越相似）"""
    match = cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I1, 0.0)
    return match


def find_paper_contour(contours, image_area):
    """从轮廓中找到试卷（四边形 + 面积大）"""
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


def four_point_transform(img, pts):
    """四点透视变换（矫正倾斜试卷）"""
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


def extract_paper(img_path, show_debug=True):
    """提取并矫正试卷"""
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
