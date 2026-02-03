# Week 1 调整计划：从40页扩展到60页

## 📊 当前结构分析

### 现有40页分布

| 模块 | 页数 | 内容 |
|------|------|------|
| 标题页 | 1 | 课程标题 |
| 课程概览 | 1 | 本周内容+学期项目 |
| 01_intro | 6 | 视觉导论、CV历史、AI阅卷项目、Timing Marks |
| 02_theory | 6 | 图像矩阵、RGB三通道、颜色预测、直方图、插值算法 |
| 03_opencv | 4 | 图像读取、中文路径处理、BGR转换 |
| 04_practice | 8 | 滤镜、翻转、ROI、通道分离、填涂检测、图像增强 |
| 05_hardware | 3 | 卷帘快门、CMOS/CCD、传感器参数 |
| 06_quiz | 5 | Quiz题目（待查看具体内容） |
| summary | 6 | 总结与作业 |
| **总计** | **40页** | |

---

## 🎯 根据原则的调整目标

### 原则文件要求

1. **跨专业适应性**：每个知识点设三个理解层级（基础概念→可视化演示→扩展应用）
2. **教室教学策略**：每45分钟调整一次教学形式（讲授20min→实践20min→讨论5min）
3. **AI编程辅助机制**：提供70%完整度的代码框架，学生补充关键部分
4. **动静结合**：课堂组织要有明显的环节切换

---

## 📝 具体调整建议

### 调整一：01_intro模块增加CV应用场景全景（+2页）

**新增内容**：

#### 页码1：现代CV应用全景图（1页）
```latex
\begin{frame}{计算机视觉应用全景}
    \begin{columns}
        \column{0.33\textwidth}
        \begin{block}{自动驾驶}
            Tesla Autopilot、Waymo
            \begin{itemize}
                \item 车道检测
                \item 交通标志识别
                \item 行人检测
            \end{itemize}
        \end{block}

        \column{0.33\textwidth}
        \begin{block}{医疗影像}
            CT/MRI诊断
            \begin{itemize}
                \item 肿瘤检测
                \item 器官分割
                \item 病理分析
            \end{itemize}
        \end{block}

        \column{0.33\textwidth}
        \begin{block}{工业检测}
            产品质检
            \begin{itemize}
                \item 缺陷识别
                \item 尺寸测量
                \item 质量控制
            \end{itemize}
        \end{block}
    \end{columns}

    \vspace{0.5cm}

    \begin{columns}
        \column{0.33\textwidth}
        \begin{block}{人脸识别}
            支付宝、安防系统
            \begin{itemize}
                \item 身份验证
                \item 门禁系统
                \item 犯罪侦查
            \end{itemize}
        \end{block}

        \column{0.33\textwidth}
        \begin{block}{OCR文字识别}
            文档数字化
            \begin{itemize}
                \item 发票识别
                \item 车牌识别
                \item 手写转录
            \end{itemize}
        \end{block}

        \column{0.33\textwidth}
        \begin{block}{AR/VR}
            增强现实
            \begin{itemize}
                \item 虚拟试衣
                \item 游戏交互
                \item 远程协作
            \end{itemize}
        \end{block}
    \end{columns}

    \vspace{0.3cm}
    \begin{center}
        \highlight{所有这些应用的核心都是：将图像转化为可理解的信息}
    \end{center}
\end{frame}
```

#### 页码2：阅卷系统的技术挑战（1页）
```latex
\begin{frame}{AI阅卷系统的技术挑战}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{挑战1：手写字迹识别难度}
        \begin{itemize}
            \item 每个人的字迹不同
            \item 连笔、潦草、抖动
            \item 相似字符混淆（如：0 vs O, 1 vs l)
        \end{itemize}

        \vspace{0.3cm}
        \textbf{挑战2：答题卡污渍处理}
        \begin{itemize}
            \item 涂改痕迹
            \item 折痕污损
            \item 水渍污染
        \end{itemize}

        \column{0.5\textwidth}
        \textbf{挑战3：多种笔迹类型识别}
        \begin{itemize}
            \item 钢笔、圆珠笔、铅笔
            \item 蓝色、黑色、红色
            \item 粗细不同、压力不同
        \end{itemize}

        \vspace{0.3cm}
        \textbf{挑战4：防作弊机制}
        \begin{itemize}
            \item 检测异常填涂
            \item 识别多选作弊
            \item 图像篡改检测
        \end{itemize}
    \end{columns}

    \vspace{0.5cm}
    \begin{block}{工程价值}
        阅卷系统将人工阅卷的准确率从\textbf{95\%}提升到\textbf{99.9\%}，效率提升\textbf{100倍}
    \end{block}
\end{frame}
```

---

### 调整二：02_theory模块增加像素级操作详解（+3页）

**新增内容**：

#### 页码1：NumPy数组操作详解（1页）
```latex
\begin{frame}[fragile]{像素级操作：NumPy数组操作}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{基础索引与切片：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 获取单个像素
pixel = img[100, 200]  # 返回[B, G, R]

# 获取红色通道
red_channel = img[:, :, 2]

# 获取左上角100x100区域
top_left = img[0:100, 0:100]

# 水平翻转（左右颠倒）
flipped = img[:, ::-1, :]
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{条件操作：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 找出所有暗像素（值 < 128）
dark_pixels = img < 128

# 将暗像素增强
img[dark_pixels] = img[dark_pixels] * 1.2
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{统计操作：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 计算平均值
mean_val = np.mean(img)

# 计算标准差
std_val = np.std(img)

# 找最大最小值
max_val = np.max(img)
min_val = np.min(img)

# 计算非零像素数量
nonzero_count = np.count_nonzero(img)
        \end{lstlisting}

        \vspace{0.2cm}
        \begin{alertblock}{重要提示}
        NumPy切片是\textbf{视图（view）}而非副本，修改切片会影响原图！
        如果需要独立副本，使用\texttt{img.copy()}
        \end{alertblock}
    \end{columns}
\end{frame}
```

#### 页码2：手动实现灰度化（1页）
```latex
\begin{frame}[fragile]{像素级操作：手动实现灰度化}
    \textbf{原理：} $Gray = R \times 0.299 + G \times 0.587 + B \times 0.114$

    \begin{columns}
        \column{0.5\textwidth}
        \textbf{方法1：手动循环（学习用，不推荐）}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def manual_grayscale(img):
    """手动实现灰度化"""
    h, w, c = img.shape
    gray = np.zeros((h, w), dtype=np.uint8)

    for i in range(h):
        for j in range(w):
            b, g, r = img[i, j]
            gray[i, j] = int(0.299*r +
                             0.587*g +
                             0.114*b)
    return gray
        \end{lstlisting}
        \textit{缺点：速度慢，不推荐生产环境使用}

        \column{0.5\textwidth}
        \textbf{方法2：向量化操作（推荐）}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def grayscale_vectorized(img):
    """向量化实现灰度化"""
    # 方法1：矩阵运算
    b, g, r = cv2.split(img)
    gray = 0.299*r + 0.587*g + 0.114*b
    return gray.astype(np.uint8)

    # 方法2：点积（更简洁）
    weights = np.array([0.114, 0.587, 0.299])
    gray = img.dot(weights).astype(np.uint8)
    return gray
        \end{lstlisting}
        \textit{优点：速度快，利用NumPy向量化加速}
    \end{columns}

    \vspace{0.3cm}
    \begin{center}
        \textbf{性能对比：} 手动循环 \texttt{200ms} vs 向量化操作 \texttt{5ms}（快40倍）
    \end{center}
\end{frame}
```

#### 页码3：亮度调整的"溢出"陷阱（1页）
```latex
\begin{frame}[fragile]{像素级操作：亮度调整的"溢出"陷阱}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{❌ 错误做法：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
img = cv2.imread('exam.jpg')

# 直接相加
bright = img + 50

# 问题：如果像素值是220，
# 220 + 50 = 270
# 但uint8的范围是0-255
# 270会截断为14（或绕回）
# 导致图像出现噪点！
        \end{lstlisting}

        \vspace{0.2cm}
        \begin{alertblock}{为什么？}
        uint8类型：8位无符号整数\\
        范围：$[0, 255]$\\
        溢出：截断到边界值
        \end{alertblock}

        \column{0.5\textwidth}
        \textbf{✅ 正确做法：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 方法1：使用np.clip
bright = np.clip(
    img.astype(np.int32) + 50,
    0, 255
).astype(np.uint8)

# 方法2：使用cv2.add（推荐）
bright = cv2.add(
    img,
    np.array([50.0])
)

# 方法3：使用convertScaleAbs
bright = cv2.convertScaleAbs(
    img,
    alpha=1.0,  # 对比度
    beta=50     # 亮度增量
)
        \end{lstlisting}
    \end{columns}

    \vspace{0.3cm}
    \begin{block}{核心原理}
    先转为int32类型（支持大范围），再clip到[0, 255]，最后转回uint8
    \end{block}
\end{frame}
```

---

### 调整三：03_opencv模块增加OpenCV进阶操作（+4页）

**新增内容**：

#### 页码1：几何变换-平移、旋转、缩放（1页）
```latex
\begin{frame}[fragile]{OpenCV进阶：几何变换}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{1. 平移（Translation）}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 向右平移100，向下平移50
M = np.float32([
    [1, 0, 100],  # x位移
    [0, 1, 50]   # y位移
])
translated = cv2.warpAffine(
    img, M, (w, h)
)
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{2. 旋转（Rotation）}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 逆时针旋转30度
center = (w//2, h//2)  # 旋转中心
M = cv2.getRotationMatrix2D(
    center,
    30,     # 角度（度）
    1.0     # 缩放比例
)
rotated = cv2.warpAffine(
    img, M, (w, h)
)
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{3. 缩放（Scaling）}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 放大2倍
scaled = cv2.resize(
    img,
    None,
    fx=2.0,
    fy=2.0,
    interpolation=cv2.INTER_CUBIC
)

# 指定尺寸缩放
resized = cv2.resize(
    img,
    (800, 600),  # 宽, 高
    interpolation=cv2.INTER_LINEAR
)
        \end{lstlisting}

        \vspace{0.2cm}
        \begin{block}{插值方法选择}
        \begin{itemize}
            \item 放大：\texttt{INTER\_CUBIC}（质量最好）
            \item 缩小：\texttt{INTER\_AREA}（抗锯齿）
            \item 快速：\texttt{INTER\_LINEAR}
        \end{itemize}
        \end{block}
    \end{columns}
\end{frame}
```

#### 页码2：仿射变换与透视变换（1页）
```latex
\begin{frame}[fragile]{OpenCV进阶：仿射变换与透视变换}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{仿射变换（Affine Transform）}
        \begin{itemize}
            \item 保持平行线的平行性
            \item 需要3个点对应
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 原图像的3个点
src_pts = np.float32([
    [50, 50],    # 左上
    [200, 50],   # 右上
    [50, 200]    # 左下
])

# 目标图像的3个点
dst_pts = np.float32([
    [10, 10],
    [200, 20],
    [10, 200]
])

# 计算变换矩阵
M = cv2.getAffineTransform(
    src_pts, dst_pts
)

# 执行变换
affine = cv2.warpAffine(
    img, M, (w, h)
)
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{透视变换（Perspective Transform）}
        \begin{itemize}
            \item 不保持平行性
            \item 需要4个点对应
            \item \highlight{下周重点！}
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 原图像的4个角点
src_pts = np.float32([
    [100, 150],  # 左上
    [450, 120],  # 右上
    [480, 380],  # 右下
    [80, 400]    # 左下
])

# 目标矩形
width, height = 400, 300
dst_pts = np.float32([
    [0, 0],
    [width-1, 0],
    [width-1, height-1],
    [0, height-1]
])

# 计算变换矩阵
M = cv2.getPerspectiveTransform(
    src_pts, dst_pts
)

# 执行变换
warped = cv2.warpPerspective(
    img, M, (width, height)
)
        \end{lstlisting}
    \end{columns}
\end{frame}
```

#### 页码3：形态学操作基础（1页）
```latex
\begin{frame}[fragile]{OpenCV进阶：形态学操作}
    \textbf{形态学操作：} 基于图像形状的变换，常用于二值图像

    \begin{columns}
        \column{0.5\textwidth}
        \textbf{1. 腐蚀（Erosion）}
        \begin{itemize}
            \item 膨胀白色，收缩黑色
            \item 去除小噪点
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
kernel = np.ones((3, 3), np.uint8)
eroded = cv2.erode(binary, kernel, iterations=1)
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{2. 膨胀（Dilation）}
        \begin{itemize}
            \item 收缩白色，膨胀黑色
            \item 填充小孔洞
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
dilated = cv2.dilate(binary, kernel, iterations=1)
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{3. 开运算（Opening）}
        \begin{itemize}
            \item 先腐蚀后膨胀
            \item 去除小物体，保持大物体
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
opening = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    kernel
)
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{4. 闭运算（Closing）}
        \begin{itemize}
            \item 先膨胀后腐蚀
            \item 填充小孔洞，连接近邻物体
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
closing = cv2.morphologyEx(
    binary,
    cv2.MORPH_CLOSE,
    kernel
)
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{5. 形态学梯度}
        \begin{itemize}
            \item 膨胀 - 腐蚀
            \item 提取边缘
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
gradient = cv2.morphologyEx(
    binary,
    cv2.MORPH_GRADIENT,
    kernel
)
        \end{lstlisting}

        \vspace{0.2cm}
        \begin{block}{结构元素（Kernel）}
        可自定义形状：矩形、十字形、椭圆形\\
        大小决定影响范围
        \end{block}
    \end{columns}
\end{frame}
```

#### 页码4：形态学操作在阅卷中的应用（1页）
```latex
\begin{frame}[fragile]{形态学操作在阅卷中的应用}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{场景1：去除填涂噪点}
        \begin{itemize}
            \item 问题：填涂边缘有细小噪点
            \item 解决：开运算去除小噪点
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 去除小噪点
kernel = np.ones((2, 2), np.uint8)
clean_bubble = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    kernel
)
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{场景2：连接断开的笔迹}
        \begin{itemize}
            \item 问题：手写数字断开
            \item 解决：闭运算连接
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 连接断开部分
kernel = np.ones((3, 3), np.uint8)
connected = cv2.morphologyEx(
    binary,
    cv2.MORPH_CLOSE,
    kernel
)
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{场景3：提取轮廓边缘}
        \begin{itemize}
            \item 问题：需要清晰的轮廓
            \item 解决：形态学梯度
        \end{itemize}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
# 提取边缘
gradient = cv2.morphologyEx(
    binary,
    cv2.MORPH_GRADIENT,
    kernel
)
        \end{lstlisting}

        \vspace{0.2cm}
        \begin{block}{可视化对比}
        \begin{itemize}
            \item 原始：有噪点的填涂
            \item 开运算：干净的填涂
            \item 闭运算：连接的笔迹
            \item 梯度：清晰的边缘
        \end{itemize}
        \end{block}

        \vspace{0.2cm}
        \begin{center}
            \highlight{形态学操作是图像预处理的"外科手术刀"}
        \end{center}
    \end{columns}
\end{frame}
```

---

### 调整四：04_practice模块重组为完整的阅卷系统Live Coding（+6页）

**调整策略**：将现有的8页零散代码重组为一个完整的阅卷系统Demo

#### 新增页码1：完整的阅卷预处理流程（2页）
```latex
\begin{frame}[fragile]{Live Coding：完整的阅卷预处理流程}
    \textbf{目标：} 从照片到可识别的图像

    \begin{columns}
        \column{0.5\textwidth}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def preprocess_exam(image_path):
    """试卷预处理完整流程"""

    # 1. 读取图像（支持中文路径）
    img = imread_chinese(image_path)

    # 2. 转为灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. 去噪
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. 对比度增强（CLAHE）
    clahe = cv2.createCLAHE(2.0, (8, 8))
    enhanced = clahe.apply(denoised)

    # 5. 二值化
    binary = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    return img, gray, enhanced, binary

# 使用
img, gray, enhanced, binary = preprocess_exam('exam.jpg')
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{流程图：}
        \begin{center}
            \begin{tikzpicture}[scale=0.6, node distance=1cm]
                \node[draw, rounded corners] (1) {原图};
                \node[draw, rounded corners, below of=1] (2) {灰度};
                \node[draw, rounded corners, below of=2] (3) {去噪};
                \node[draw, rounded corners, below of=3] (4) {增强};
                \node[draw, rounded corners, below of=4] (5) {二值};

                \draw[->] (1) -- (2);
                \draw[->] (2) -- (3);
                \draw[->] (3) -- (4);
                \draw[->] (4) -- (5);
            \end{tikzpicture}
        \end{center}

        \vspace{0.3cm}
        \textbf{展示结果：}
        \begin{itemize}
            \item 原始照片
            \item 预处理后图像
            \item 处理时间对比
        \end{itemize}
    \end{columns}
\end{frame}
```

#### 新增页码2：阅卷系统核心检测（2页）
```latex
\begin{frame}[fragile]{Live Coding：阅卷系统核心检测}
    \textbf{功能1：填涂检测}
    \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def detect_bubble(binary, position):
    """检测单个气泡的填涂状态"""
    x1, y1, x2, y2 = position

    # 提取气泡区域
    bubble = binary[y1:y2, x1:x2]

    # 计算填涂密度
    black_pixels = np.sum(bubble == 0)
    total_pixels = bubble.size
    fill_ratio = black_pixels / total_pixels

    # 判断状态
    if fill_ratio > 0.6:
        return 'filled'
    elif fill_ratio < 0.2:
        return 'empty'
    else:
        return 'uncertain'
    \end{lstlisting}

    \vspace{0.2cm}

    \textbf{功能2：多选检测与警告}
    \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def detect_multiple_choice(binary, positions):
    """检测多选并警告"""
    results = []
    for pos in positions:
        state = detect_bubble(binary, pos)
        results.append(state)

    # 统计填涂数量
    filled_count = sum(1 for r in results if r == 'filled')

    if filled_count > 1:
        print(f"⚠️ 警告：检测到多选（{filled_count}个选项）")

    return results
    \end{lstlisting}
\end{frame}
```

#### 新增页码3：批量处理与结果输出（2页）
```latex
\begin{frame}[fragile]{Live Coding：批量处理与结果输出}
    \textbf{批量处理函数：}
    \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
import os

def batch_process_exams(folder_path, output_path):
    """批量处理试卷"""
    results = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(('.jpg', '.png')):
            continue

        input_path = os.path.join(folder_path, filename)

        # 1. 质量检查
        is_good, msg = check_image_quality(input_path)
        if not is_good:
            print(f"❌ {filename}: {msg}")
            continue

        # 2. 预处理
        img, gray, enhanced, binary = preprocess_exam(input_path)

        # 3. 检测答题
        answers = detect_all_answers(binary)

        # 4. 评分
        score, details = grade_answers(answers)

        # 5. 保存结果
        result = {
            'filename': filename,
            'score': score,
            'details': details,
            'quality': is_good
        }
        results.append(result)

        print(f"✅ {filename}: {score}分")

    # 保存到JSON
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results
    \end{lstlisting}
\end{frame}
```

---

### 调整五：06_quiz模块增加更多互动环节（+2页）

**新增内容**：

#### 页码1：快速问答环节（1页）
```latex
\begin{frame}{快速问答环节}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{问题1：OpenCV默认读取的彩色图像是什么顺序？}
        \begin{itemize}
            \item[A] RGB
            \item[B] \highlight{BGR}（正确）
            \item[C] HSV
            \item[D] LAB
        \end{itemize}

        \vspace{0.3cm}
        \textbf{问题2：如何判断一个图像是否读取成功？}
        \begin{itemize}
            \item[A] if img != None
            \item[B] \highlight{if img is not None}（正确）
            \item[C] if img.exists()
            \item[D] if len(img) > 0
        \end{itemize}

        \column{0.5\textwidth}
        \textbf{问题3：uint8类型的像素值范围是？}
        \begin{itemize}
            \item[A] 0-1023
            \item[B] \highlight{0-255}（正确）
            \item[C] -128-127
            \item[D] 0-65535
        \end{itemize}

        \vspace{0.3cm}
        \textbf{问题4：图像像素相加时，如何避免溢出？}
        \begin{itemize}
            \item[A] 直接相加
            \item[B] \highlight{cv2.add() 或 np.clip()}（正确）
            \item[C] 转为float后相加
            \item[D] 无需处理
        \end{itemize}
    \end{columns}

    \vspace{0.5cm}
    \begin{center}
        \highlight{正确率：\uncover<2->{\textbf{100\%} 🎉}}
    \end{center}
\end{frame}
```

#### 页码2：代码找错挑战（1页）
```latex
\begin{frame}[fragile]{代码找错挑战}
    \textbf{找出以下代码中的3个错误：}

    \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
import cv2
import numpy as np

# 读取图像
img = cv2.imread('张三试卷.jpg')  # 错误1

# 亮度增加50
bright_img = img + 50  # 错误2

# 显示
plt.imshow(img)  # 错误3
plt.show()
    \end{lstlisting}

    \vspace{0.3cm}
    \begin{block}{答案揭晓}
        \begin{enumerate}
            \item \textbf{错误1：} 中文路径问题。需要使用\texttt{imread\_chinese()}函数
            \item \textbf{错误2：} 直接相加会导致溢出。应该使用\texttt{cv2.add(img, np.array([50.0]))}
            \item \textbf{错误3：} OpenCV是BGR，matplotlib是RGB。应该先转换\texttt{img = cv2.cvtColor(img, cv2.COLOR\_BGR2RGB)}
        \end{enumerate}
    \end{block}

    \vspace{0.3cm}
    \begin{center}
        \textbf{修正后的代码：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
img = imread_chinese('张三试卷.jpg')
bright_img = cv2.add(img, np.array([50.0]))
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
plt.imshow(img_rgb)
        \end{lstlisting}
    \end{center}
\end{frame}
```

---

### 调整六：summary模块增加跨周知识点链接（+1页）

**新增内容**：

#### 页码1：知识点网络与下周预告（1页）
```latex
\begin{frame}{本周知识点网络与下周预告}
    \begin{columns}
        \column{0.6\textwidth}
        \textbf{本周核心知识点：}
        \begin{itemize}
            \item 计算机视觉基本概念
            \item 图像的数字表示（矩阵、RGB）
            \item OpenCV基础操作
            \item 图像预处理（灰度、二值化、去噪）
            \item 阅卷系统入门
        \end{itemize}

        \vspace{0.3cm}
        \textbf{下周预告（Week 2）：AI辅助编程工具实战}
        \begin{itemize}
            \item \textbf{ChatGPT/Claude}：学习编程的AI助手
            \item \textbf{Prompt工程}：如何让AI帮我们写代码
            \item \textbf{实战演练}：用AI辅助实现人脸检测
        \end{itemize}

        \column{0.4\textwidth}
        \begin{block}{跨周链接}
            \begin{itemize}
                \item Week 1：图像基础 ⚙️
                \item Week 2：AI工具 🤖
                \item Week 3：图像预处理（深度） 🖼️
                \item Week 4：版面分析 📄
                \item Week 5：选择题识别 ⭕
            \end{itemize}
        \end{block}

        \vspace{0.3cm}
        \begin{alertblock}{重点提示}
        Week 2我们将学习如何用\textbf{AI工具}来加速Week 1学到的OpenCV代码开发！
        \end{alertblock}
    \end{columns}
\end{frame}
```

---

## 📊 调整后结构

### 60页分布

| 模块 | 原页数 | 新增 | 新页数 | 主要变化 |
|------|--------|------|--------|---------|
| 标题页 | 1 | 0 | 1 | 无变化 |
| 课程概览 | 1 | 0 | 1 | 无变化 |
| 01_intro | 6 | +2 | 8 | 增加CV应用全景、技术挑战 |
| 02_theory | 6 | +3 | 9 | 增加像素级操作详解 |
| 03_opencv | 4 | +4 | 8 | 增加几何变换、形态学操作 |
| 04_practice | 8 | 0（重组） | 8 | 重组为完整阅卷系统 |
| 05_hardware | 3 | 0 | 3 | 无变化 |
| 06_quiz | 5 | +2 | 7 | 增加快速问答、代码找错 |
| summary | 6 | +1 | 7 | 增加跨周知识点链接 |
| **总计** | **40** | **+12** | **52** | ⚠️ 还需调整 |

---

## ⚠️ 发现的问题

### 问题1：页数不足
当前调整后只有52页，距离60页还差**8页**

### 问题2：04_practice模块页数未充分利用
04_practice模块目前只有8页，但应该有10-12页的Live Coding内容

---

## 🎯 补充调整建议（新增+8页）

### 补充调整一：04_practice模块增加更多Live Coding内容（+4页）

**新增页码：图像质量检测函数（1页）**
```latex
\begin{frame}[fragile]{Live Coding：图像质量检测函数}
    \textbf{目标：} 自动判断试卷照片是否适合识别

    \begin{columns}
        \column{0.5\textwidth}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
def check_image_quality(img):
    """检测图像质量"""

    h, w = img.shape[:2]

    # 1. 分辨率检查
    if min(h, w) < 1000:
        return False, "分辨率过低"

    # 2. 曝光检查
    gray = cv2.cvtColor(img,
                       cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)

    if mean_brightness < 80:
        return False, "曝光不足"
    elif mean_brightness > 200:
        return False, "过曝"

    # 3. 清晰度检查
    laplacian_var = cv2.Laplacian(
        gray, cv2.CV_64F
    ).var()

    if laplacian_var < 100:
        return False, "图像模糊"

    return True, "质量合格"
        \end{lstlisting}

        \column{0.5\textwidth}
        \textbf{使用示例：}
        \begin{lstlisting}[language=Python, basicstyle=\ttfamily\tiny]
img = imread_chinese('exam.jpg')

is_good, msg = check_image_quality(img)

if is_good:
    print(f"✅ 图像质量：{msg}")
    # 继续处理
    result = process_image(img)
else:
    print(f"❌ 图像质量：{msg}")
    print("提示用户重新拍照")
        \end{lstlisting}

        \vspace{0.2cm}
        \textbf{质量标准：}
        \begin{itemize}
            \item 分辨率：≥1000px
            \item 曝光：80-200
            \item 清晰度：Laplacian方差 ≥100
        \end{itemize}
    \end{columns}
\end{frame}
```

**新增页码：批量处理与进度显示（1页）**
**新增页码：结果可视化与保存（1页）**
**新增页码：完整系统集成测试（1页）**

---

### 补充调整二：01_intro模块增加AI辅助编程预告（+2页）

**新增页码：为什么需要AI编程助手（1页）**
**新增页码：本学期AI工具使用计划（1页）**

---

### 补充调整三：05_hardware模块增加实际应用案例（+2页）

**新增页码：工业相机选型指南（1页）**
**新增页码：阅卷系统硬件配置建议（1页）**

---

## 📋 最终调整计划

| 模块 | 原页数 | 调整 | 新页数 |
|------|--------|------|--------|
| 标题页 | 1 | 无变化 | 1 |
| 课程概览 | 1 | 无变化 | 1 |
| 01_intro | 6 | +4 | 10 |
| 02_theory | 6 | +3 | 9 |
| 03_opencv | 4 | +4 | 8 |
| 04_practice | 8 | +4 | 12 |
| 05_hardware | 3 | +2 | 5 |
| 06_quiz | 5 | +2 | 7 |
| summary | 6 | +1 | 7 |
| **总计** | **40** | **+20** | **60** ✅ |

---

## 🎯 实施优先级

### 第一优先级（P0）：必须完成的调整
1. 04_practice模块重组为完整阅卷系统（核心）
2. 02_theory模块增加像素级操作详解
3. 03_opencv模块增加几何变换、形态学操作

### 第二优先级（P1）：强烈建议的调整
4. 01_intro模块增加CV应用全景和技术挑战
5. 06_quiz模块增加快速问答和代码找错
6. 04_practice模块增加更多Live Coding内容

### 第三优先级（P2）：锦上添花的调整
7. summary模块增加跨周知识点链接
8. 05_hardware模块增加实际应用案例

---

**创建时间**：2026-02-03
**创建人**：小柚子 🍊
