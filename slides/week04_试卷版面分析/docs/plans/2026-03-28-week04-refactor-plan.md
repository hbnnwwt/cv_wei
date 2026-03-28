# Week 4 课件结构化重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 对第4周"试卷版面分析"课件进行全面结构化重构，修复编译错误、对齐 preamble、优化结构与视觉、补充内容。

**Architecture:** 保持现有模块化结构（sections/目录），修复致命 LaTeX 错误后，对齐 preamble 到 week01 标准，统一 AI 辅助编程模板，引入 `figures/答题卡.jpg`，生成 code/ 示例脚本。

**Tech Stack:** LaTeX Beamer, TikZ, tcolorbox, listings, Python/OpenCV

---

### Task 1: 对齐 preamble.tex 到 week01

**Files:**
- Modify: `preamble.tex`

**Step 1: 替换整个 preamble.tex 内容**

```latex
%===========================================================
% preamble.tex - Beamer 配置文件
%===========================================================

% 中文支持
\usepackage[UTF8]{ctex}

% 图形与表格
\usepackage{graphicx}
\usepackage{booktabs}

% 代码高亮
\usepackage{listings}
\lstset{
    language=Python,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue},
    commentstyle=\color{green!60!black},
    stringstyle=\color{orange},
    breaklines=true,
    frame=single,
    showstringspaces=false,
    backgroundcolor=\color{gray!10}
}

% 颜色与图形
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes, arrows, positioning}

% 数学公式
\usepackage{amsmath}
\usepackage{amssymb}

% 超链接
\usepackage{hyperref}

% tcolorbox for colored boxes
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}

%===========================================================
% 主题设置
%===========================================================
\usetheme{Madrid}
\usecolortheme{whale}
\usefonttheme{professionalfonts}

%===========================================================
% 页面边距设置（预留页脚空间）
%===========================================================
\setbeamersize{text margin left=0.5cm, text margin right=0.5cm}
\setbeamersize{text margin bottom=1cm}
\setbeamersize{text margin top=0.5cm}

%===========================================================
% 课程信息
%===========================================================
\title[试卷版面分析]{第4周：试卷版面分析}
\subtitle{怎么知道选择题、简答题在哪里？}
\author{北京石油化工学院\textbackslash 人工智能研究院\textbackslash 王文通}
\institute{通选课}
\date{2025-2026 学年}

%===========================================================
% 自定义命令
%===========================================================
\newcommand{\highlight}[1]{\textcolor{red}{\textbf{#1}}}
```

**Step 2: 编译验证**

Run: `cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week04_试卷版面分析" && xelatex -interaction=nonstopmode main.tex 2>&1 | tail -5`
Expected: 编译成功（可能有 warning 但无 error）

**Step 3: Commit**

```bash
git add preamble.tex
git commit -m "fix: 对齐 preamble 到 week01 标准，修正标题信息"
```

---

### Task 2: 修复 02_edge.tex 嵌套 lstlisting 错误

**Files:**
- Modify: `sections/02_edge.tex:214-243`

**Step 1: 替换 AI 辅助编程页面**

将第 214-243 行的嵌套 lstlisting 页面替换为两个独立 frame：

```latex
\begin{frame}{AI辅助编程：Canny边缘检测}
    \begin{tcolorbox}[colback=blue!5,colframe=blue!60,title={AI辅助提示}]
        你可以使用Cursor、ChatGPT、Claude等AI工具来帮助你实现Canny边缘检测。

        \textbf{Prompt示例：}\\
        \texttt{请用Python和OpenCV实现Canny边缘检测，并解释每个参数的含义。}
    \end{tcolorbox}
\end{frame}

\begin{frame}[fragile]{Canny边缘检测代码示例}
    \begin{lstlisting}[basicstyle=\ttfamily\scriptsize]
import cv2
import numpy as np

# 预处理
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Canny 边缘检测
edges = cv2.Canny(
    blur,           # 输入图像
    50,             # 低阈值 threshold1
    150             # 高阈值 threshold2
)

# 可视化
cv2.imshow('Edges', edges)
cv2.waitKey(0)
    \end{lstlisting}
\end{frame}
```

**Step 2: 编译验证**

Run: `xelatex -interaction=nonstopmode main.tex 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add sections/02_edge.tex
git commit -m "fix: 修复02_edge.tex嵌套lstlisting编译错误"
```

---

### Task 3: 修复 04_geometry.tex 嵌套 lstlisting 错误

**Files:**
- Modify: `sections/04_geometry.tex:97-127`

**Step 1: 替换 AI 辅助编程页面**

```latex
\begin{frame}{AI辅助编程：多边形逼近}
    \begin{tcolorbox}[colback=blue!5,colframe=blue!60,title={AI辅助提示}]
        你可以使用Cursor、ChatGPT、Claude等AI工具来帮助你实现多边形逼近。

        \textbf{Prompt示例：}\\
        \texttt{请用Python和OpenCV实现多边形逼近，解释approxPolyDP的参数含义。}
    \end{tcolorbox}
\end{frame}

\begin{frame}[fragile]{多边形逼近代码示例}
    \begin{lstlisting}[basicstyle=\ttfamily\scriptsize]
# 计算周长
peri = cv2.arcLength(contour, True)

# 多边形逼近
approx = cv2.approxPolyDP(
    contour,      # 输入轮廓
    0.02 * peri,  # 精度参数
    True          # 轮廓是否封闭
)

# 获取顶点数
num_vertices = len(approx)
print(f"顶点数: {num_vertices}")

# 绘制逼近结果
cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
    \end{lstlisting}
\end{frame}
```

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add sections/04_geometry.tex
git commit -m "fix: 修复04_geometry.tex嵌套lstlisting编译错误"
```

---

### Task 4: 重构 05_layout.tex AI 辅助编程页面

**Files:**
- Modify: `sections/05_layout.tex:67-96`

**Step 1: 替换 AI 辅助编程页面**

同样的嵌套问题（虽然结构略有不同，但有 TODO 注释后的 lstlisting 嵌套）。拆为两个 frame：

```latex
\begin{frame}{AI辅助编程：投影法}
    \begin{tcolorbox}[colback=blue!5,colframe=blue!60,title={AI辅助提示（建议侧屏演示）}]
        你可以使用Cursor、ChatGPT、Claude等AI工具来帮助你实现投影法。

        \textbf{Prompt示例：}\\
        \texttt{请用Python和NumPy实现水平投影和垂直投影，用于分析文档版面结构。}
    \end{tcolorbox}
\end{frame}

\begin{frame}[fragile]{水平投影代码示例}
    \begin{lstlisting}[basicstyle=\ttfamily\scriptsize]
def horizontal_projection(binary):
    """
    水平投影：统计每行的白色像素数
    binary: 二值图像（0=黑, 255=白）
    """
    binary = binary // 255
    proj = np.sum(binary, axis=1)
    return proj

# 使用
binary = cv2.adaptiveThreshold(gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV, 11, 2)
h_proj = horizontal_projection(binary)
    \end{lstlisting}
\end{frame}
```

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add sections/05_layout.tex
git commit -m "fix: 修复05_layout.tex嵌套lstlisting编译错误"
```

---

### Task 5: 在 01_overview.tex 引入答题卡图片

**Files:**
- Modify: `sections/01_overview.tex:7-22`（什么是版面分析页）

**Step 1: 在概述页添加答题卡图片**

将"什么是版面分析？"页面改为左右分栏，右侧放答题卡图片：

```latex
\begin{frame}{什么是版面分析？}
    \begin{columns}
        \column{0.55\textwidth}
        \begin{block}{定义}
            从文档图像中识别和定位不同区域（标题、正文、表格、图片等）
        \end{block}

        \vspace{0.3cm}

        \textbf{在阅卷系统中的作用：}
        \begin{enumerate}
            \item 找到试卷边界（定位试卷）
            \item 定位选择题区域（OMR识别）
            \item 定位判断题区域（符号匹配）
            \item 定位简答题区域（手写识别）
            \item 定位填空题区域（内容提取）
        \end{enumerate}

        \column{0.4\textwidth}
        \begin{center}
            \includegraphics[width=\textwidth]{figures/答题卡.jpg}
        \end{center}
    \end{columns}
\end{frame}
```

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add sections/01_overview.tex
git commit -m "feat: 在版面分析概述页引入答题卡图片"
```

---

### Task 6: 优化 01_overview.tex TikZ 流程图

**Files:**
- Modify: `sections/01_overview.tex:52-74`（版面分析完整流程页）

**Step 1: 优化流程图**

改善节点间距、添加图标文字、使用更好的颜色方案：

```latex
\begin{frame}{版面分析完整流程}
    \begin{center}
        \begin{tikzpicture}[node distance=1.2cm and 1.8cm, auto,
            block/.style={draw, rectangle, rounded corners=4pt, fill=blue!10,
                minimum height=1cm, minimum width=2.2cm, font=\small, align=center},
            arrow/.style={->, thick, >=stealth}]

            \node[block, fill=gray!15] (input) {输入图像\\{\scriptsize 试卷照片}};
            \node[block, right of=input, fill=yellow!15] (pre) {预处理\\{\scriptsize 灰度+降噪}};
            \node[block, right of=pre, fill=green!15] (edge) {边缘检测\\{\scriptsize Canny}};
            \node[block, right of=edge, fill=red!15] (contour) {轮廓检测\\{\scriptsize findContours}};
            \node[block, below of=contour, fill=purple!15] (filter) {轮廓筛选\\{\scriptsize 面积+形状}};
            \node[block, left of=filter, fill=orange!15] (layout) {版面分析\\{\scriptsize 投影法}};
            \node[block, left of=layout, fill=cyan!15] (output) {区域输出\\{\scriptsize 题目定位}};

            \draw[arrow] (input) -- (pre);
            \draw[arrow] (pre) -- (edge);
            \draw[arrow] (edge) -- (contour);
            \draw[arrow] (contour) -- (filter);
            \draw[arrow] (filter) -- (layout);
            \draw[arrow] (layout) -- (output);
        \end{tikzpicture}
    \end{center}
\end{frame}
```

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add sections/01_overview.tex
git commit -m "improve: 优化版面分析流程图TikZ样式"
```

---

### Task 7: 完善 00_logistics.tex 互动环节具体内容

**Files:**
- Modify: `sections/00_logistics.tex:178-206`（课堂互动环节设计页）

**Step 1: 为互动2和互动3添加具体代码内容**

在互动2（代码拼图）后添加打乱的代码片段示例，在互动3（错误找茬）后添加具体 bug 代码。

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add sections/00_logistics.tex
git commit -m "feat: 完善课堂互动环节的具体代码内容"
```

---

### Task 8: 排版规范化 — 统一代码 frame 格式

**Files:**
- Modify: `sections/02_edge.tex`（多处 lstlisting）
- Modify: `sections/03_contour.tex`（多处 lstlisting）
- Modify: `sections/04_geometry.tex`（多处 lstlisting）
- Modify: `sections/05_layout.tex`（多处 lstlisting）

**Step 1: 检查所有 lstlisting frame 是否有 [fragile] 选项**

确保每个包含 `\begin{lstlisting}` 的 frame 都标记了 `[fragile]`。

**Step 2: 统一代码字体大小**
- 标准代码：`\ttfamily\scriptsize`
- 长代码：`\ttfamily\tiny`

**Step 3: 编译验证**

**Step 4: Commit**

```bash
git add sections/
git commit -m "style: 统一代码frame格式和字体大小"
```

---

### Task 9: 生成 code/ 目录下的 Python 示例脚本

**Files:**
- Create: `code/canny_edge_detection.py`
- Create: `code/contour_detection.py`
- Create: `code/paper_locator.py`
- Create: `code/projection_layout.py`

**Step 1: 创建 canny_edge_detection.py**

```python
"""
Canny 边缘检测示例
演示如何使用 OpenCV 进行边缘检测
"""
import cv2
import numpy as np

def auto_canny(gray, sigma=0.33):
    """自动计算 Canny 阈值"""
    v = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(gray, lower, upper)

if __name__ == "__main__":
    img = cv2.imread("figures/答题卡.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 手动阈值
    edges_manual = cv2.Canny(blur, 50, 150)
    # 自动阈值
    edges_auto = auto_canny(blur)

    cv2.imshow("Original", img)
    cv2.imshow("Manual Canny (50,150)", edges_manual)
    cv2.imshow("Auto Canny", edges_auto)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

**Step 2: 创建 contour_detection.py**

```python
"""
轮廓检测示例
演示 findContours 的各种检索模式
"""
import cv2
import numpy as np

if __name__ == "__main__":
    img = cv2.imread("figures/答题卡.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    modes = [
        ("RETR_EXTERNAL", cv2.RETR_EXTERNAL),
        ("RETR_LIST", cv2.RETR_LIST),
        ("RETR_TREE", cv2.RETR_TREE),
    ]

    for name, mode in modes:
        contours, hierarchy = cv2.findContours(
            edges.copy(), mode, cv2.CHAIN_APPROX_SIMPLE
        )
        output = img.copy()
        cv2.drawContours(output, contours, -1, (0, 255, 0), 2)
        cv2.imshow(f"{name} ({len(contours)} contours)", output)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

**Step 3: 创建 paper_locator.py**

```python
"""
试卷定位示例
使用轮廓检测 + 多边形逼近找到试卷边界
"""
import cv2
import numpy as np

def find_paper_contour(contours, image_area):
    """从轮廓列表中找到试卷轮廓"""
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < image_area * 0.1:
            continue
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            candidates.append((area, approx))
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    return None

if __name__ == "__main__":
    img = cv2.imread("figures/答题卡.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_area = gray.shape[0] * gray.shape[1]
    paper = find_paper_contour(contours, image_area)

    output = img.copy()
    if paper is not None:
        cv2.drawContours(output, [paper], 0, (0, 255, 0), 3)
        print(f"找到试卷，4个顶点：{paper.reshape(-1, 2).tolist()}")
    else:
        print("未找到试卷轮廓")

    cv2.imshow("Paper Locator", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

**Step 4: 创建 projection_layout.py**

```python
"""
投影法版面分析示例
使用水平/垂直投影定位试卷题目区域
"""
import cv2
import numpy as np

def horizontal_projection(binary):
    """水平投影"""
    return np.sum(binary // 255, axis=1)

def find_divider_lines(proj, threshold=10, min_length=5):
    """找到分隔线（波谷）"""
    dividers = []
    start = None
    for i, val in enumerate(proj):
        if val < threshold:
            if start is None:
                start = i
        else:
            if start is not None:
                if i - start >= min_length:
                    dividers.append((start, i))
                start = None
    return dividers

if __name__ == "__main__":
    img = cv2.imread("figures/答题卡.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    h_proj = horizontal_projection(binary)
    threshold = np.mean(h_proj) * 0.1
    dividers = find_divider_lines(h_proj, threshold)

    output = img.copy()
    for y_start, y_end in dividers:
        y_mid = (y_start + y_end) // 2
        cv2.line(output, (0, y_mid), (output.shape[1], y_mid), (0, 0, 255), 1)

    cv2.imshow("Layout Analysis", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

**Step 5: Commit**

```bash
git add code/
git commit -m "feat: 添加4个Python示例脚本到code目录"
```

---

### Task 10: 最终编译验证与清理

**Step 1: 完整编译两次**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week04_试卷版面分析"
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

**Step 2: 检查编译日志中的错误**

```bash
grep -i "error" main.log | head -20
```

Expected: 无 error

**Step 3: 最终 Commit**

```bash
git add -A
git commit -m "refactor: Week4课件结构化重构完成"
```
