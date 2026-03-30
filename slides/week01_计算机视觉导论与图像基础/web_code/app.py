# -*- coding: utf-8 -*-
"""
Week 01 计算机视觉 Web 演示系统
================================
Flask 后端主程序

依赖安装: pip install -r requirements.txt
运行: python app.py
访问: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import os
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 上传限制
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def imread_chinese(filepath):
    """读取中文路径图片"""
    try:
        img_array = np.fromfile(filepath, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def img_to_base64(img):
    """将OpenCV图像转换为base64编码"""
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')


def base64_to_img(base64_str):
    """将base64编码转换为OpenCV图像"""
    img_data = base64.b64decode(base64_str)
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')


# 路由：获取模块列表
@app.route('/api/modules')
def get_modules():
    """获取所有可用的演示模块"""
    modules = [
        {
            'id': 'basics',
            'name': 'OpenCV 基础操作',
            'description': '图像读取、滤镜、增强等基础操作',
            'apis': [
                {'name': 'grayscale', 'label': '灰度化', 'params': []},
                {'name': 'brightness', 'label': '亮度调整', 'params': [{'name': 'value', 'label': '亮度值', 'min': -100, 'max': 100, 'default': 0}]},
                {'name': 'contrast', 'label': '对比度调整', 'params': [{'name': 'alpha', 'label': '对比度系数', 'min': 0.5, 'max': 3.0, 'default': 1.0, 'step': 0.1}]},
                {'name': 'gaussian_blur', 'label': '高斯模糊', 'params': [{'name': 'kernel_size', 'label': '核大小', 'min': 1, 'max': 15, 'default': 5, 'step': 2}]},
                {'name': 'sharpen', 'label': '锐化', 'params': []},
                {'name': 'invert', 'label': '反色', 'params': []},
            ]
        },
        {
            'id': 'edge',
            'name': '边缘检测与形态学',
            'description': 'Canny边缘检测、形态学操作',
            'apis': [
                {'name': 'canny', 'label': 'Canny边缘检测', 'params': [
                    {'name': 'threshold1', 'label': '阈值1', 'min': 0, 'max': 500, 'default': 100},
                    {'name': 'threshold2', 'label': '阈值2', 'min': 0, 'max': 500, 'default': 200}
                ]},
                {'name': 'dilate', 'label': '膨胀', 'params': [{'name': 'kernel_size', 'label': '核大小', 'min': 1, 'max': 15, 'default': 3, 'step': 2}]},
                {'name': 'erode', 'label': '腐蚀', 'params': [{'name': 'kernel_size', 'label': '核大小', 'min': 1, 'max': 15, 'default': 3, 'step': 2}]},
                {'name': 'opening', 'label': '开运算', 'params': [{'name': 'kernel_size', 'label': '核大小', 'min': 1, 'max': 15, 'default': 3, 'step': 2}]},
                {'name': 'closing', 'label': '闭运算', 'params': [{'name': 'kernel_size', 'label': '核大小', 'min': 1, 'max': 15, 'default': 3, 'step': 2}]},
            ]
        },
        {
            'id': 'bubble',
            'name': '气泡检测',
            'description': '智能阅卷系统 - 气泡检测与填涂识别',
            'apis': [
                {'name': 'detect_bubbles', 'label': '快速气泡检测', 'params': [
                    {'name': 'fill_threshold', 'label': '填涂阈值(%)', 'min': 0, 'max': 100, 'default': 30}
                ]},
                {'name': 'detect_bubbles_steps', 'label': 'OMR算法流程演示(7步)', 'params': [
                    {'name': 'fill_threshold', 'label': '填涂阈值(%)', 'min': 0, 'max': 100, 'default': 30},
                    {'name': 'answer_key', 'label': '正确答案(如AABCD)', 'type': 'text', 'default': 'BBBBB'}
                ]},
            ]
        },
        {
            'id': 'quality',
            'name': '图像质量检测',
            'description': '调节参数实时查看质量检测结果',
            'apis': [
                {'name': 'add_noise', 'label': '添加高斯噪声', 'params': [
                    {'name': 'mean', 'label': '噪声均值', 'min': 0, 'max': 50, 'default': 0},
                    {'name': 'sigma', 'label': '噪声标准差', 'min': 0, 'max': 100, 'default': 25}
                ]},
                {'name': 'add_salt_pepper', 'label': '添加椒盐噪声', 'params': [
                    {'name': 'amount', 'label': '噪声密度(%)', 'min': 0, 'max': 10, 'default': 1, 'step': 0.1}
                ]},
                {'name': 'add_blur', 'label': '添加模糊', 'params': [
                    {'name': 'kernel_size', 'label': '模糊强度', 'min': 1, 'max': 21, 'default': 5, 'step': 2}
                ]},
                {'name': 'adjust_quality', 'label': '调整质量(亮度+对比度)', 'params': [
                    {'name': 'brightness', 'label': '亮度调整', 'min': -100, 'max': 100, 'default': 0},
                    {'name': 'contrast', 'label': '对比度系数', 'min': 0.1, 'max': 3.0, 'default': 1.0, 'step': 0.1}
                ]},
                {'name': 'add_motion_blur', 'label': '添加运动模糊', 'params': [
                    {'name': 'kernel_size', 'label': '模糊核大小', 'min': 3, 'max': 31, 'default': 15, 'step': 2},
                    {'name': 'angle', 'label': '运动角度', 'min': 0, 'max': 180, 'default': 0}
                ]},
                {'name': 'add_compression_artifacts', 'label': '添加压缩伪影', 'params': [
                    {'name': 'quality', 'label': 'JPEG质量(1-100)', 'min': 1, 'max': 100, 'default': 30}
                ]},
            ]
        },
        {
            'id': 'batch',
            'name': '批量处理',
            'description': '批量处理试卷、统计答案分布',
            'apis': [
                {'name': 'batch_process', 'label': '批量生成与统计', 'params': [
                    {'name': 'num_papers', 'label': '试卷数量', 'min': 1, 'max': 100, 'default': 10},
                    {'name': 'num_questions', 'label': '题目数量', 'min': 1, 'max': 50, 'default': 5},
                    {'name': 'confidence', 'label': '置信度阈值(%)', 'min': 0, 'max': 100, 'default': 80}
                ]},
            ]
        },
        {
            'id': 'roi',
            'name': 'ROI 裁剪',
            'description': 'NumPy数组操作 - 调整ROI区域',
            'apis': [
                {'name': 'crop_roi', 'label': 'ROI裁剪', 'params': [
                    {'name': 'x1', 'label': '左(%)', 'min': 0, 'max': 100, 'default': 0},
                    {'name': 'y1', 'label': '上(%)', 'min': 0, 'max': 100, 'default': 0},
                    {'name': 'x2', 'label': '右(%)', 'min': 0, 'max': 100, 'default': 100},
                    {'name': 'y2', 'label': '下(%)', 'min': 0, 'max': 100, 'default': 100},
                ]},
            ]
        },
    ]
    return jsonify(modules)


# 路由：加载默认图片
@app.route('/api/default_image')
def get_default_image():
    """获取默认测试图片"""
    default_path = os.path.join('static', 'images', 'lena.jpg')

    if os.path.exists(default_path):
        img = imread_chinese(default_path)
        if img is not None:
            return jsonify({'success': True, 'image': img_to_base64(img)})

    # 如果没有图片，生成一个随机测试图
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    return jsonify({'success': True, 'image': img_to_base64(img)})


# 路由：加载测试图片
@app.route('/api/test_image/<image_type>')
def get_test_image(image_type):
    """获取答题卡测试图片"""
    # 测试图片映射
    test_images = {
        'bubble_test_normal': 'bubble_test_normal.png',
        'bubble_test_diagonal': 'bubble_test_diagonal.png',
        'bubble_test_random': 'bubble_test_random.png',
        'bubble_test_partial': 'bubble_test_partial.png',
        'bubble_sheet_blank': 'bubble_sheet_blank.png',
        'omr_test_01': 'omr_test_01.png'
    }

    if image_type not in test_images:
        return jsonify({'success': False, 'error': '未知的测试图片类型'})

    image_path = os.path.join('static', 'images', test_images[image_type])

    if os.path.exists(image_path):
        img = imread_chinese(image_path)
        if img is not None:
            return jsonify({'success': True, 'image': img_to_base64(img)})

    return jsonify({'success': False, 'error': '图片文件不存在'})


# 路由：处理图片
@app.route('/api/process', methods=['POST'])
def process_image():
    """处理图片的统一接口"""
    data = request.json

    if 'image' not in data:
        return jsonify({'success': False, 'error': '没有提供图片数据'})

    if 'operation' not in data:
        return jsonify({'success': False, 'error': '没有指定操作类型'})

    try:
        # 解码图片
        img = base64_to_img(data['image'])
        if img is None:
            return jsonify({'success': False, 'error': '图片解码失败'})

        operation = data['operation']
        params = data.get('params', {})

        # 根据操作类型调用对应的处理函数
        result = apply_operation(img, operation, params)

        if isinstance(result, dict) and 'image' in result:
            # 字典返回（如气泡检测、ROI裁剪）
            result['success'] = True
            result['image'] = img_to_base64(result['image'])
        elif isinstance(result, np.ndarray):
            # numpy数组返回（简单的图像处理）
            result = {'success': True, 'image': img_to_base64(result)}
        else:
            # 其他数据返回（如质量检测、批量处理）
            result = {'success': True, 'data': result}

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def apply_operation(img, operation, params):
    """应用图像处理操作"""

    # ========== OpenCV 基础操作 ==========
    if operation == 'grayscale':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif operation == 'brightness':
        value = int(params.get('value', 0))
        return cv2.convertScaleAbs(img, alpha=1, beta=value)

    elif operation == 'contrast':
        alpha = float(params.get('alpha', 1.0))
        return cv2.convertScaleAbs(img, alpha=alpha, beta=0)

    elif operation == 'gaussian_blur':
        kernel_size = int(params.get('kernel_size', 5))
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    elif operation == 'sharpen':
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(img, -1, kernel)

    elif operation == 'invert':
        return cv2.bitwise_not(img)

    # ========== 边缘检测与形态学 ==========
    elif operation == 'canny':
        threshold1 = int(params.get('threshold1', 100))
        threshold2 = int(params.get('threshold2', 200))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    elif operation == 'dilate':
        kernel_size = int(params.get('kernel_size', 3))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.dilate(img, kernel, iterations=1)

    elif operation == 'erode':
        kernel_size = int(params.get('kernel_size', 3))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.erode(img, kernel, iterations=1)

    elif operation == 'opening':
        kernel_size = int(params.get('kernel_size', 3))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    elif operation == 'closing':
        kernel_size = int(params.get('kernel_size', 3))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    # ========== 气泡检测 ==========
    elif operation == 'detect_bubbles':
        fill_threshold = float(params.get('fill_threshold', 30)) / 100

        # 转灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 方法1：使用Otsu自适应阈值二值化
        _, binary_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        contours_otsu, _ = cv2.findContours(binary_otsu.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 方法2：使用自适应阈值（作为备选）
        binary_adapt = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 11, 2)
        # 对自适应阈值结果进行一些形态学操作，减少小噪声
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary_adapt = cv2.morphologyEx(binary_adapt, cv2.MORPH_OPEN, kernel)
        contours_adapt, _ = cv2.findContours(binary_adapt.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 选择效果更好的方法
        # 过滤并统计两种方法的结果
        def filter_bubbles(contours):
            filtered = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h if h > 0 else 0
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)

                if perimeter > 0:
                    circularity = (4 * np.pi * area) / (perimeter * perimeter)
                else:
                    circularity = 0

                if (15 <= w <= 100 and 15 <= h <= 100 and
                    0.6 <= aspect_ratio <= 1.67 and
                    area >= 100 and area <= 10000 and
                    circularity > 0.4):
                    filtered.append({
                        'contour': cnt,
                        'bbox': (x, y, w, h),
                        'center': (x + w // 2, y + h // 2)
                    })
            return filtered

        bubbles_otsu = filter_bubbles(contours_otsu)
        bubbles_adapt = filter_bubbles(contours_adapt)

        # 选择检测到更多合理气泡的方法
        if len(bubbles_otsu) >= 15:  # 至少能检测到3行
            bubble_contours = bubbles_otsu
            binary = binary_otsu
            method_used = "Otsu"
        elif len(bubbles_adapt) >= 15:
            bubble_contours = bubbles_adapt
            binary = binary_adapt
            method_used = "Adaptive"
        else:
            # 如果两种方法都检测不到足够多的气泡，尝试放宽条件
            bubble_contours = bubbles_otsu if len(bubbles_otsu) >= 5 else bubbles_adapt
            binary = binary_otsu if len(bubbles_otsu) >= 5 else binary_adapt
            method_used = "Relaxed"

        # 如果仍然没有检测到气泡，返回提示
        if not bubble_contours:
            return {
                'image': img,
                'results': [],
                'message': '未检测到气泡，请确保图片中有清晰的圆形气泡。建议使用生成的测试图片。'
            }

        # 对气泡进行排序：先按Y坐标（从上到下），再按X坐标（从左到右）
        bubble_contours.sort(key=lambda b: (b['center'][1], b['center'][0]))

        # 将气泡分组为题目（假设每行是一个题目，每题有4个选项ABCD）
        options = ['A', 'B', 'C', 'D']
        results = []

        # 简单的分组策略：按Y坐标聚类分成行
        if bubble_contours:
            # 获取所有Y坐标
            y_coords = [b['center'][1] for b in bubble_contours]

            # 使用简单的聚类算法将气泡分组为行
            rows = []
            current_row = [bubble_contours[0]]
            current_y = y_coords[0]

            for i in range(1, len(bubble_contours)):
                if abs(y_coords[i] - current_y) < 50:  # 同一行的阈值
                    current_row.append(bubble_contours[i])
                else:
                    # 新的一行
                    if current_row:
                        # 按X坐标排序当前行
                        current_row.sort(key=lambda b: b['center'][0])
                        rows.append(current_row)
                    current_row = [bubble_contours[i]]
                    current_y = y_coords[i]

            # 添加最后一行
            if current_row:
                current_row.sort(key=lambda b: b['center'][0])
                rows.append(current_row)

            # 处理每一行（每题）
            for row_idx, row in enumerate(rows):
                # 处理每个气泡（每个选项）
                for col_idx, bubble in enumerate(row):
                    if col_idx >= 4:  # 最多4个选项
                        break

                    x, y, w, h = bubble['bbox']
                    cnt = bubble['contour']

                    # 创建掩码并计算填充比例
                    mask = np.zeros(binary.shape, dtype=np.uint8)
                    cv2.drawContours(mask, [cnt], -1, 255, -1)
                    mask = cv2.bitwise_and(binary, binary, mask=mask)

                    # 计算非零像素（填涂部分）的比例
                    total_pixels = cv2.countNonZero(mask)
                    bubble_area = w * h

                    if bubble_area > 0:
                        ratio = total_pixels / bubble_area
                    else:
                        ratio = 0

                    status = 'filled' if ratio > fill_threshold else 'empty'

                    results.append({
                        'question': row_idx + 1,
                        'option': options[col_idx],
                        'ratio': round(ratio * 100, 1),
                        'status': status,
                        'position': (x, y, x + w, y + h)
                    })

        # 在原图上标记检测结果
        result_img = img.copy()
        for r in results:
            x1, y1, x2, y2 = r['position']

            # 根据状态选择颜色
            if r['status'] == 'filled':
                color = (0, 255, 0)  # 绿色表示已填涂
                thickness = 3
            else:
                color = (255, 0, 0)  # 红色表示未填涂
                thickness = 2

            # 绘制矩形框
            cv2.rectangle(result_img, (x1, y1), (x2, y2), color, thickness)

            # 绘制选项标签
            label = f"Q{r['question']}-{r['option']}"
            cv2.putText(result_img, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

            # 如果已填涂，显示填充比例
            if r['status'] == 'filled':
                cv2.putText(result_img, f"{r['ratio']}%", (x1, y2 + 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        return {'image': result_img, 'results': results}

    elif operation == 'detect_bubbles_steps':
        """PyImageSearch 7步OMR算法流程演示"""
        fill_threshold = float(params.get('fill_threshold', 30)) / 100
        answer_key_str = params.get('answer_key', 'BBBBB')  # 用户输入的答案字符串，如 "AABCD"

        # 将答案字符串转换为答案键字典
        # 例如: "AABCD" -> {0: 0, 1: 0, 2: 1, 3: 2, 4: 3} (A=0, B=1, C=2, D=3, E=4)
        ANSWER_KEY = {}
        for i, char in enumerate(answer_key_str):
            if char.upper() in 'ABCDE':
                ANSWER_KEY[i] = 'ABCDE'.index(char.upper())

        steps_results = {}

        # ===== 步骤1: 图像预处理（灰度化 + 高斯模糊） =====
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 保存步骤1结果（灰度图转彩色用于显示）
        step1_img = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
        cv2.putText(step1_img, "Step 1: Grayscale + Blur", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        steps_results['step1_preprocess'] = img_to_base64(step1_img)

        # ===== 步骤2: 边缘检测（Canny） =====
        edged = cv2.Canny(blurred, 75, 200)

        # 转换边缘图为彩色用于显示
        step2_img = cv2.cvtColor(edged, cv2.COLOR_GRAY2BGR)
        cv2.putText(step2_img, "Step 2: Canny Edge Detection", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        steps_results['step2_edged'] = img_to_base64(step2_img)

        # ===== 步骤3: 查找答题卡轮廓 =====
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 按面积排序，找到最大的轮廓（答题卡）
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        doc_cnt = None

        for cnt in contours_sorted:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:  # 四边形
                doc_cnt = approx
                break

        # 在原图上绘制答题卡轮廓
        step3_img = img.copy()
        if doc_cnt is not None:
            cv2.drawContours(step3_img, [doc_cnt], -1, (0, 255, 0), 3)
            cv2.putText(step3_img, "Step 3: Found Document", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(step3_img, "Step 3: Document NOT Found", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        steps_results['step3_contour'] = img_to_base64(step3_img)

        # ===== 步骤4: 透视变换矫正 =====
        if doc_cnt is not None and len(doc_cnt) == 4:
            # 获取四个角点
            pts = doc_cnt.reshape(4, 2).astype(np.float32)

            # 对点进行排序：左上、右上、右下、左下
            rect = np.zeros((4, 2), dtype=np.float32)
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]  # 左上（x+y最小）
            rect[2] = pts[np.argmax(s)]  # 右下（x+y最大）
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]  # 右上（x-y最小）
            rect[3] = pts[np.argmax(diff)]  # 左下（x-y最大）

            # 计算目标尺寸
            width_a = np.sqrt(((rect[2][0] - rect[3][0]) ** 2) + ((rect[2][1] - rect[3][1]) ** 2))
            width_b = np.sqrt(((rect[1][0] - rect[0][0]) ** 2) + ((rect[1][1] - rect[0][1]) ** 2))
            max_width = max(int(width_a), int(width_b))

            height_a = np.sqrt(((rect[1][0] - rect[2][0]) ** 2) + ((rect[1][1] - rect[2][1]) ** 2))
            height_b = np.sqrt(((rect[0][0] - rect[3][0]) ** 2) + ((rect[0][1] - rect[3][1]) ** 2))
            max_height = max(int(height_a), int(height_b))

            dst = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype=np.float32)

            # 计算变换矩阵并应用透视变换
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (max_width, max_height))
            warped_gray = cv2.warpPerspective(gray, M, (max_width, max_height))
        else:
            # 如果没找到四边形轮廓，使用原图
            warped = img.copy()
            warped_gray = gray.copy()

        # 绘制透视变换结果
        step4_img = warped.copy()
        cv2.putText(step4_img, "Step 4: Perspective Transform", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        steps_results['step4_warped'] = img_to_base64(step4_img)

        # ===== 步骤5: 二值化（Otsu阈值） =====
        _, thresh = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # 转换为彩色用于显示
        step5_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        cv2.putText(step5_img, "Step 5: Threshold (Otsu)", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        steps_results['step5_threshold'] = img_to_base64(step5_img)

        # ===== 步骤6: 查找并排序气泡轮廓 =====
        thresh_contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 过滤气泡轮廓
        question_contours = []
        for cnt in thresh_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            ar = w / float(h)

            # 气泡应该是圆形的，长宽比接近1
            if w >= 20 and h >= 20 and ar >= 0.7 and ar <= 1.3:
                question_contours.append(cnt)

        # 绘制检测到的所有轮廓
        step6_img = warped.copy()
        cv2.drawContours(step6_img, question_contours, -1, (0, 0, 255), 2)
        cv2.putText(step6_img, f"Step 6: Found {len(question_contours)} Bubbles", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        steps_results['step6_bubbles'] = img_to_base64(step6_img)

        # ===== 步骤7: 排序并填涂检测 + 评分 =====
        if question_contours:
            # 先按从上到下排序（y坐标）
            def sort_top_to_bottom(cnts):
                bounding_boxes = [cv2.boundingRect(c) for c in cnts]
                (cnts, bounding_boxes) = zip(*sorted(zip(cnts, bounding_boxes), key=lambda b: b[1][1]))
                return list(cnts), list(bounding_boxes)

            question_contours, bounding_boxes = sort_top_to_bottom(question_contours)

            # 每题5个选项，分组处理
            options_per_question = 5
            correct = 0
            results = []

            step7_img = warped.copy()

            # 计算实际题目数量
            num_questions = len(question_contours) // options_per_question

            # 按行处理：每行5个选项
            for row in range(num_questions):
                # 获取当前行的气泡（5个选项）
                start_idx = row * options_per_question
                end_idx = start_idx + options_per_question
                bubbles = question_contours[start_idx:end_idx]

                # 按从左到右排序当前行的气泡（按x坐标）
                bubbles_with_x = [(b, bounding_boxes[start_idx + i][0]) for i, b in enumerate(bubbles)]
                bubbles_sorted = [b for b, x in sorted(bubbles_with_x, key=lambda item: item[1])]

                bubbled = None
                max_pixel_count = 0

                # 对每个选项创建掩码并计算填涂像素
                for j, bubble in enumerate(bubbles_sorted):
                    mask = np.zeros(thresh.shape, dtype=np.uint8)
                    cv2.drawContours(mask, [bubble], -1, 255, -1)
                    mask = cv2.bitwise_and(thresh, thresh, mask=mask)

                    total = cv2.countNonZero(mask)

                    if total > max_pixel_count:
                        max_pixel_count = total
                        bubbled = (total, j)

                # 判断答案是否正确
                k = ANSWER_KEY.get(row, 0)
                color = (0, 0, 255)  # 默认红色（错误）

                if bubbled is not None and bubbled[1] == k:
                    correct += 1
                    color = (0, 255, 0)  # 绿色（正确）

                # 绘制正确答案
                if row < len(ANSWER_KEY) and k < len(bubbles_sorted):
                    cv2.drawContours(step7_img, [bubbles_sorted[k]], -1, color, 3)

                # 记录结果
                if bubbled:
                    results.append({
                        'question': row + 1,
                        'selected': ['A', 'B', 'C', 'D', 'E'][bubbled[1]],
                        'correct': ['A', 'B', 'C', 'D', 'E'][k],
                        'is_correct': bubbled[1] == k
                    })

            # 计算得分
            if num_questions > 0:
                score = (correct / num_questions) * 100
            else:
                score = 0
            cv2.putText(step7_img, f"Step 7: Score {score:.0f}%", (10, step7_img.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            steps_results['step7_graded'] = img_to_base64(step7_img)

        return {
            'image': img,
            'steps': steps_results,
            'results': results if results else [],
            'message': f'OMR算法演示完成，共{len(steps_results)}个步骤'
        }

    # ========== 图像质量检测 ==========

    # 质量检测辅助函数
    def calculate_quality(img):
        """计算图像质量指标"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 分辨率
        h, w = gray.shape
        resolution = f"{w}x{h}"

        # 亮度
        brightness = float(np.mean(gray))
        brightness_status = "正常" if 80 <= brightness <= 200 else ("过暗" if brightness < 80 else "过亮")

        # 对比度
        contrast = float(np.std(gray))
        contrast_status = "正常" if contrast > 50 else "偏低"

        # 清晰度 (Laplacian方差)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_status = "清晰" if laplacian_var > 100 else "模糊"

        # 噪声检测 (使用高频成分)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        noise_level = float(np.mean(sobel_magnitude))
        noise_status = "低噪声" if noise_level < 30 else ("中等噪声" if noise_level < 60 else "高噪声")

        # 噪声方差检测
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        diff = cv2.absdiff(gray, blurred)
        noise_variance = float(np.var(diff))
        noise_variance_status = "清晰" if noise_variance < 50 else ("有噪声" if noise_variance < 150 else "严重噪声")

        # 综合评估
        quality_score = 0
        quality_score += 1 if 80 <= brightness <= 200 else 0
        quality_score += 1 if contrast > 50 else 0
        quality_score += 1 if laplacian_var > 100 else 0
        quality_score += 1 if noise_variance < 100 else 0

        overall_status = ["差", "一般", "良好", "优秀", "完美"][quality_score]

        return {
            'resolution': resolution,
            'brightness': round(brightness, 1),
            'brightness_status': brightness_status,
            'contrast': round(contrast, 1),
            'contrast_status': contrast_status,
            'sharpness': round(laplacian_var, 1),
            'sharpness_status': sharpness_status,
            'noise_level': round(noise_level, 1),
            'noise_status': noise_status,
            'noise_variance': round(noise_variance, 1),
            'noise_variance_status': noise_variance_status,
            'quality_score': quality_score,
            'overall': overall_status
        }

    if operation == 'add_noise':
        # 添加高斯噪声
        mean = int(params.get('mean', 0))
        sigma = int(params.get('sigma', 25))
        noise = np.random.normal(mean, sigma, img.shape).astype(np.uint8)
        noisy_img = cv2.add(img, noise)
        quality_data = calculate_quality(noisy_img)
        return {'image': noisy_img, 'quality': quality_data}

    elif operation == 'add_salt_pepper':
        # 添加椒盐噪声
        amount = float(params.get('amount', 1)) / 100
        noisy_img = img.copy()
        h, w, c = img.shape
        # 计算噪声点数量
        num_salt = int(amount * h * w * 0.5)
        num_pepper = int(amount * h * w * 0.5)

        # 添加盐噪声（白点）
        coords = [np.random.randint(0, i, num_salt) for i in (h, w)]
        noisy_img[coords[0], coords[1], :] = 255

        # 添加椒噪声（黑点）
        coords = [np.random.randint(0, i, num_pepper) for i in (h, w)]
        noisy_img[coords[0], coords[1], :] = 0

        quality_data = calculate_quality(noisy_img)
        return {'image': noisy_img, 'quality': quality_data}

    elif operation == 'add_blur':
        # 添加高斯模糊
        kernel_size = int(params.get('kernel_size', 5))
        if kernel_size % 2 == 0:
            kernel_size += 1
        blurred_img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        quality_data = calculate_quality(blurred_img)
        return {'image': blurred_img, 'quality': quality_data}

    elif operation == 'adjust_quality':
        # 调整亮度和对比度
        brightness = int(params.get('brightness', 0))
        contrast = float(params.get('contrast', 1.0))
        adjusted_img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)
        quality_data = calculate_quality(adjusted_img)
        return {'image': adjusted_img, 'quality': quality_data}

    elif operation == 'add_motion_blur':
        # 添加运动模糊
        kernel_size = int(params.get('kernel_size', 15))
        if kernel_size % 2 == 0:
            kernel_size += 1
        angle = int(params.get('angle', 0))

        # 创建运动模糊核
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size

        # 旋转核以匹配角度
        if angle != 0:
            center = ((kernel_size - 1) / 2, (kernel_size - 1) / 2)
            M = cv2.getRotationMatrix2D(center, angle, 1)
            kernel = cv2.warpAffine(kernel, M, (kernel_size, kernel_size))

        blurred_img = cv2.filter2D(img, -1, kernel)
        quality_data = calculate_quality(blurred_img)
        return {'image': blurred_img, 'quality': quality_data}

    elif operation == 'add_compression_artifacts':
        # 添加JPEG压缩伪影
        quality = int(params.get('quality', 30))
        # 编码为JPEG
        _, encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        # 解码回来
        compressed_img = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        quality_data = calculate_quality(compressed_img)
        return {'image': compressed_img, 'quality': quality_data}

    elif operation == 'check_quality':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 分辨率
        h, w = gray.shape
        resolution = f"{w}x{h}"

        # 亮度
        brightness = float(np.mean(gray))
        brightness_status = "正常" if 80 <= brightness <= 200 else ("过暗" if brightness < 80 else "过亮")

        # 对比度
        contrast = float(np.std(gray))
        contrast_status = "正常" if contrast > 50 else "偏低"

        # 清晰度 (Laplacian方差)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_status = "清晰" if laplacian_var > 100 else "模糊"

        # 噪声检测 (使用高频成分)
        # 使用Sobel算子检测边缘，边缘数量多表示噪声多
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        noise_level = float(np.mean(sobel_magnitude))
        noise_status = "低噪声" if noise_level < 30 else ("中等噪声" if noise_level < 60 else "高噪声")

        # 另一种噪声检测方法：计算平滑后图像的差异
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        diff = cv2.absdiff(gray, blurred)
        noise_variance = float(np.var(diff))
        noise_variance_status = "清晰" if noise_variance < 50 else ("有噪声" if noise_variance < 150 else "严重噪声")

        # 综合评估
        quality_score = 0
        quality_score += 1 if 80 <= brightness <= 200 else 0
        quality_score += 1 if contrast > 50 else 0
        quality_score += 1 if laplacian_var > 100 else 0
        quality_score += 1 if noise_variance < 100 else 0

        overall_status = ["差", "一般", "良好", "优秀", "完美"][quality_score]

        return {
            'resolution': resolution,
            'brightness': round(brightness, 1),
            'brightness_status': brightness_status,
            'contrast': round(contrast, 1),
            'contrast_status': contrast_status,
            'sharpness': round(laplacian_var, 1),
            'sharpness_status': sharpness_status,
            'noise_level': round(noise_level, 1),
            'noise_status': noise_status,
            'noise_variance': round(noise_variance, 1),
            'noise_variance_status': noise_variance_status,
            'quality_score': quality_score,
            'overall': overall_status
        }

    # ========== 批量处理 ==========
    elif operation == 'batch_process':
        num_papers = int(params.get('num_papers', 10))
        num_questions = int(params.get('num_questions', 5))
        confidence = float(params.get('confidence', 80)) / 100

        results = []
        correct_answers = ['A'] * num_questions

        for i in range(num_papers):
            answers = []
            score = 0
            for _ in range(num_questions):
                choice = np.random.choice(['A', 'B', 'C', 'D'])
                answers.append(choice)
                if choice == correct_answers[len(answers) - 1]:
                    score += 1

            # 模拟置信度
            detected_score = int(score * (confidence + np.random.uniform(-0.05, 0.05)))
            detected_score = max(0, min(num_questions, detected_score))

            results.append({
                'paper_id': i + 1,
                'answers': answers,
                'score': score,
                'detected_score': detected_score,
                'accuracy': round(score / num_questions * 100, 1)
            })

        # 统计答案分布
        answer_distribution = {}
        for i in range(num_questions):
            distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            for r in results:
                distribution[r['answers'][i]] += 1
            answer_distribution[f'Q{i+1}'] = distribution

        return {
            'results': results,
            'answer_distribution': answer_distribution,
            'summary': {
                'total_papers': num_papers,
                'num_questions': num_questions,
                'avg_score': round(sum(r['score'] for r in results) / num_papers, 1),
                'max_score': max(r['score'] for r in results),
                'min_score': min(r['score'] for r in results)
            }
        }

    # ========== ROI 裁剪 ==========
    elif operation == 'crop_roi':
        x1 = int(params.get('x1', 0) / 100 * img.shape[1])
        y1 = int(params.get('y1', 0) / 100 * img.shape[0])
        x2 = int(params.get('x2', 100) / 100 * img.shape[1])
        y2 = int(params.get('y2', 100) / 100 * img.shape[0])

        # 确保坐标有效
        x1, x2 = max(0, x1), min(img.shape[1], x2)
        y1, y2 = max(0, y1), min(img.shape[0], y2)

        # 在原图上绘制ROI框
        result_img = img.copy()
        cv2.rectangle(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 裁剪ROI
        cropped = img[y1:y2, x1:x2]

        return {
            'image': result_img,
            'cropped': img_to_base64(cropped) if cropped.size > 0 else None,
            'roi_shape': cropped.shape if cropped.size > 0 else None
        }

    else:
        return {'success': False, 'error': f'未知操作: {operation}'}


if __name__ == '__main__':
    print("=" * 50)
    print("Week 01 计算机视觉 Web 演示系统")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
