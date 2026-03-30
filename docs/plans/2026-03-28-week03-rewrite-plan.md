# Week03 课件完全重写 - 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 Week03「图像预处理与增强」课件完全重写，沿袭 Week01 的成熟模式（目录结构、preamble配置、main.tex内联页面、modules扁平化、GUI演示程序、images示意图）。

**Architecture:** 参照 `week01_计算机视觉导论与图像基础/` 的完整结构，将 week03 的 sections/子目录结构重构为 modules/扁平结构，重写 preamble.tex 和 main.tex，新建4个GUI演示程序和6张Python生成示意图。

**Tech Stack:** LaTeX Beamer (XeLaTeX), Python (OpenCV, NumPy, Matplotlib, customtkinter), TikZ

---

## 参考文件

- Week01 preamble: `slides/week01_计算机视觉导论与图像基础/preamble.tex`
- Week01 main: `slides/week01_计算机视觉导论与图像基础/main.tex`
- Week01 modules: `slides/week01_计算机视觉导论与图像基础/modules/01_intro.tex` ~ `06_quiz.tex`
- Week01 summary: `slides/week01_计算机视觉导论与图像基础/sections/summary.tex`
- Week01 GUI launcher: `slides/week01_计算机视觉导论与图像基础/code/gui_launcher.py`
- Week01 GUI config: `slides/week01_计算机视觉导论与图像基础/code/gui_config.py`
- Week01 GUI demo: `slides/week01_计算机视觉导论与图像基础/code/gui_01_opencv_basics.py`
- 原则文件: `原则.md`
- Week03 旧内容: `slides/week03_图像预处理与增强/sections/` (01_denoising ~ 05_conclusion)

---

### Task 1: 备份旧文件并创建新目录结构

**Files:**
- Create: `modules/` 目录
- Keep: `sections/` 目录（旧内容暂不删除，留作参考）
- Keep: `teacher_guide/` 目录
- Keep: `code/` 目录（旧代码暂不删除）

**Step 1: 备份旧sections内容**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
cp -r sections sections_backup
```

**Step 2: 创建新目录结构**

```bash
mkdir -p modules sections images
```

**Step 3: 验证目录结构**

```bash
ls -la modules/ sections/ images/
```
Expected: 三个空目录存在

---

### Task 2: 重写 preamble.tex（对齐Week01）

**Files:**
- Modify: `preamble.tex`

**Step 1: 重写 preamble.tex**

完全参照 Week01 的 preamble.tex，写入以下内容：

```latex
%===========================================================
% preamble.tex - Beamer 配置文件（对齐Week01）
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
    backgroundcolor=\color{gray!10},
    escapechar=!            % 允许在代码中使用!...!进行LaTeX转义
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
\setbeamersize{text margin bottom=1cm}  % 底部预留1cm边距
\setbeamersize{text margin top=0.5cm}     % 顶部保留0.5cm边距

%===========================================================
% 课程信息
%===========================================================
\title[图像预处理与增强]{第3周：图像预处理与增强}
\subtitle{试卷拍照模糊怎么办？}
\author{北京石油化工学院\textbackslash 人工智能研究院\textbackslash 王文通}
\institute{通选课}
\date{2025-2026 学年}

%===========================================================
% 自定义命令
%===========================================================
% 高亮命令
\newcommand{\highlight}[1]{\textcolor{red}{\textbf{#1}}}
% 行内代码命令
\newcommand{\code}[1]{\texttt{#1}}
```

**Step 2: 编译验证**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
xelatex -interaction=nonstopmode main.tex 2>&1 | tail -5
```
Expected: 编译成功（暂无内容变化，仅preamble更新）

---

### Task 3: 重写 main.tex（对齐Week01内联页面结构）

**Files:**
- Modify: `main.tex`

**Step 1: 重写 main.tex**

参照 Week01 的 main.tex 结构，写入：

```latex
%===========================================================
% main.tex - 主控文件（对齐Week01结构）
%===========================================================
\documentclass[aspectratio=169, 10pt]{beamer}

% 导入配置文件
\input{preamble.tex}

% 学校信息
\institute{%
    \begin{minipage}{6cm}
        \centering
        \textbf{北京石油化工学院}\\
        \textit{人工智能研究院}
    \end{minipage}
}

\begin{document}

%===========================================================
% 标题页与目录
%===========================================================
\begin{frame}
    \titlepage
\end{frame}

%===========================================================
% 课前预备知识
%===========================================================
\begin{frame}{课前预备知识}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{需要的预备知识：}
        \begin{itemize}
            \item \textbf{图像基础}
            \begin{itemize}
                \item 像素、通道、数据类型
                \item 灰度图与彩色图
            \end{itemize}
            \item \textbf{NumPy基础}
            \begin{itemize}
                \item 数组索引与切片
                \item 矩阵运算
            \end{itemize}
            \item \textbf{OpenCV基础}
            \begin{itemize}
                \item 图像读写（Week 1已学）
                \item 颜色空间转换
            \end{itemize}
        \end{itemize}

        \column{0.5\textwidth}
        \textbf{预备视频链接：}
        \begin{itemize}
            \item NumPy基础（10分钟入门）
            \begin{itemize}
                \item \footnotesize \url{https://www.bilibili.com/video/BV1Wy4y1h7ii}
            \end{itemize}
            \item OpenCV入门（20分钟）
            \begin{itemize}
                \item \footnotesize \url{https://www.bilibili.com/video/BV1pv4y1Q7yR}
            \end{itemize}
        \end{itemize}

        \vspace{0.5cm}
        \begin{alertblock}{重要提示}
            本周内容建立在Week 1基础上，请确保已掌握图像读写操作！
        \end{alertblock}
    \end{columns}
\end{frame}

\section*{课程概览}
\begin{frame}{课程概览}
    \begin{columns}
        \column{0.45\textwidth}
        \textbf{本周内容：}
        \begin{itemize}
            \item 图像处理流水线概述
            \item 图像去噪（滤波器）
            \item 图像增强（直方图、CLAHE）
            \item 图像二值化（阈值方法）
            \item 几何变换（仿射、透视）
            \item 综合实战案例
        \end{itemize}

        \column{0.55\textwidth}
        \textbf{在阅卷系统中的位置：}
        \begin{enumerate}
            \item 图像采集（Week 1 已完成）
            \item \highlight{图像预处理（本周）}
            \item 版面分析（Week 4）
            \item 选择题识别（Week 5）
            \item 判断题识别（Week 6）
            \item OCR文字识别（Week 7-8）
        \end{enumerate}
    \end{columns}
\end{frame}

\begin{frame}{本周时间分配（160分钟 = 3学时）}
    \begin{columns}
        \column{0.5\textwidth}
        \textbf{第1学时（45分钟）：}
        \begin{itemize}
            \item[00:00-00:10] 理论讲解：流水线概述（10min）
            \item[00:10-00:30] 理论+演示：图像去噪（20min）
            \item[00:30-00:45] 实践：去噪代码实战（15min）
        \end{itemize}

        \textbf{第2学时（45分钟）：}
        \begin{itemize}
            \item[00:45-01:05] 理论+演示：图像增强（20min）
            \item[01:05-01:30] 理论+演示：图像二值化（25min）
        \end{itemize}

        \column{0.5\textwidth}
        \textbf{第3学时（70分钟）：}
        \begin{itemize}
            \item[01:30-01:50] 理论+演示：几何变换（20min）
            \item[01:50-02:10] 实践：综合实战（20min）
            \item[02:10-02:30] 互动测验（20min）
            \item[02:30-02:40] 总结与作业（10min）
        \end{itemize}

        \vspace{0.5cm}
        \begin{alertblock}{时间控制提示}
        如果进度落后，建议跳过"挑战任务"
        \end{alertblock}
    \end{columns}
\end{frame}

\begin{frame}{本周分组策略}
    \textbf{分组原则：}
    \begin{itemize}
        \item 每4人为一组
        \item 确保不同专业背景混合
        \item 建议包含：理工科、文科、无编程基础、有编程基础
    \end{itemize}

    \vspace{0.3cm}

    \textbf{角色分工：}
    \begin{table}
        \centering
        \small
        \begin{tabular}{lp{6cm}l}
            \toprule
            \textbf{角色} & \textbf{职责} & \textbf{适合} \\
            \midrule
            组长 & 统筹协调、进度管理 & 组织能力强的 \\
            算法实现者 & 实现图像处理代码 & 有编程基础的 \\
            参数调优者 & 调整滤波参数、优化效果 & 细心负责的 \\
            测试者 & 收集测试用例、报告问题 & 细心负责的 \\
            \bottomrule
        \end{tabular}
    \end{table}

    \vspace{0.3cm}

    \begin{block}{本周协作任务}
        用OpenCV实现试卷图像的完整预处理流程（去噪→增强→二值化）
    \end{block}
\end{frame}

\begin{frame}{多屏协同设计}
    \textbf{本课程采用多屏协同教学方式：}

    \vspace{0.3cm}

    \begin{columns}
        \column{0.5\textwidth}
        \textbf{主屏（左侧）：理论讲解}
        \begin{itemize}
            \item PPT幻灯片
            \item 概念和原理讲解
            \item 算法对比表格
            \item 互动测验
        \end{itemize}

        \column{0.5\textwidth}
        \textbf{侧屏（右侧）：实时演示}
        \begin{itemize}
            \item OpenCV代码实时演示
            \item 图像处理效果展示
            \item 参数调整实时反馈
            \item 调试过程展示
        \end{itemize}
    \end{columns}

    \vspace{0.5cm}

    \begin{block}{移动设备互动}
        使用手机参与互动测验（问卷星）
    \end{block}
\end{frame}

%===========================================================
% 代码演示对应关系
%===========================================================
\begin{frame}{代码演示程序对应关系}
    \textbf{运行方式：} 在\code{code}文件夹下运行\code{gui\_launcher.py}，选择对应的演示程序

    \vspace{0.3cm}

    \begin{table}
        \centering
        \small
        \begin{tabular}{lp{5cm}l}
            \toprule
            \textbf{PPT页面} & \textbf{演示程序} & \textbf{可调参数} \\
            \midrule
            图像去噪 & gui\_01\_denoising.py & 核大小、滤波类型 \\
            图像增强 & gui\_02\_enhancement.py & CLAHE参数、Gamma值 \\
            图像二值化 & gui\_03\_binarization.py & 阈值方法、阈值大小 \\
            几何变换 & gui\_04\_geometry.py & 旋转角度、透视参数 \\
            \bottomrule
        \end{tabular}
    \end{table}

    \vspace{0.3cm}

    \begin{alertblock}{提示}
        每个演示程序都有交互式参数滑块，拖动即可实时观察效果变化！
    \end{alertblock}
\end{frame}

%===========================================================
% 教学模块
%===========================================================
\input{modules/01_pipeline.tex}
\input{modules/02_denoising.tex}
\input{modules/03_enhancement.tex}
\input{modules/04_binarization.tex}
\input{modules/05_geometry.tex}
\input{modules/06_real_cases.tex}
\input{modules/07_quiz.tex}

%===========================================================
% 总结与作业
%===========================================================
\input{sections/summary.tex}

\end{document}
```

**Step 2: 编译验证**

先创建空的tex文件防止编译失败：

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
touch modules/01_pipeline.tex modules/02_denoising.tex modules/03_enhancement.tex modules/04_binarization.tex modules/05_geometry.tex modules/06_real_cases.tex modules/07_quiz.tex
echo "" > sections/summary.tex
xelatex -interaction=nonstopmode main.tex 2>&1 | tail -5
```
Expected: 编译成功，生成PDF（内容暂空）

---

### Task 4: 编写 modules/01_pipeline.tex（图像处理流水线概述）

**Files:**
- Create: `modules/01_pipeline.tex`

**Step 1: 编写模块内容**

参照 Week01 的 `modules/01_intro.tex` 风格（三栏学习路径、tikz图、互动设计）。

内容要点：
1. 选择适合你的学习路径（观察者/使用者/创造者三栏）
2. 试卷预处理的问题场景（拍照模糊、光照不均、倾斜等）
3. 图像处理流水线图（TikZ绘制：原图→去噪→增强→二值化→几何矫正→识别）
4. 本周学习目标清单
5. 与Week 1的知识衔接
6. AI辅助提示框（如何用AI理解预处理概念）

每页使用 Week01 风格：`\highlight{}`、tcolorbox、`\begin{columns}` 双栏布局、`\begin{alertblock}{Web演示}` 提示。

**Step 2: 编译验证**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
xelatex -interaction=nonstopmode main.tex 2>&1 | grep -E "Error|Warning" | head -10
```
Expected: 无Error

**Step 3: Commit**

```bash
git add modules/01_pipeline.tex
git commit -m "feat(week03): add pipeline overview module"
```

---

### Task 5: 编写 modules/02_denoising.tex（图像去噪）

**Files:**
- Create: `modules/02_denoising.tex`

**Step 1: 编写模块内容**

参照 Week01 的 `modules/04_practice.tex` 风格（Web演示提示、TODO代码、tcolorbox预期结果、错误做法对比）。

内容要点（约12页）：
1. 噪声类型与特征（表格：高斯/椒盐/泊松/周期噪声）
2. 试卷扫描常见噪声（alertblock + 实际场景列表）
3. 空间域滤波原理（卷积核示意、TikZ矩阵图）
4. 均值滤波 vs 高斯滤波 vs 中值滤波（代码+对比表）
5. OpenCV代码实现（带TODO的脚手架代码）
6. 双边滤波（进阶）
7. 去噪效果对比表（表格：方法/速度/效果/适用场景）
8. 代码实战（TODO框架，带AI提示框）
9. 代码找茬环节（故意写错代码让学生找bug）

**Step 2: 编译验证**

**Step 3: Commit**

```bash
git add modules/02_denoising.tex
git commit -m "feat(week03): add denoising module"
```

---

### Task 6: 编写 modules/03_enhancement.tex（图像增强）

**Files:**
- Create: `modules/03_enhancement.tex`

**Step 1: 编写模块内容**

参照 Week01 的 `modules/02_theory.tex` 风格（TikZ直方图、公式推导、代码对比、\highlight{}标注）。

内容要点（约10页）：
1. 为什么要增强图像（双栏：低质量问题 vs 增强目标）
2. 图像直方图（TikZ绘制直方图、calcHist代码）
3. 直方图均衡化（原理公式 + 代码 + 效果对比）
4. CLAHE自适应增强（原理 + 参数说明 + 代码）
5. Gamma校正（公式 + 代码 + 不同gamma值对比）
6. 图像锐化（拉普拉斯算子、Unsharp Masking）
7. 增强方法对比总结表

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 7: 编写 modules/04_binarization.tex（图像二值化）

**Files:**
- Create: `modules/04_binarization.tex`

**Step 1: 编写模块内容**

内容要点（约10页）：
1. 什么是二值化（定义 + 公式 + TikZ示意图）
2. 二值化在OCR中的应用场景
3. 全局阈值法（cv2.threshold + 手动选阈值）
4. Otsu自适应阈值（原理 + 直方图双峰图 + 代码）
5. 自适应阈值（ADAPTIVE_THRESH_MEAN/GAUSSIAN + 代码）
6. 三种方法对比（表格 + 代码实战 + 效果对比）
7. 代码找茬挑战（二值化代码中的bug）

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 8: 编写 modules/05_geometry.tex（几何变换）

**Files:**
- Create: `modules/05_geometry.tex`

**Step 1: 编写模块内容**

内容要点（约8页）：
1. 仿射变换基础（变换矩阵 + 包含操作列表）
2. 仿射变换代码实现（translate/rotate函数 + TODO）
3. 透视变换原理（4点对应 + 代码）
4. 自动矫正实战（试卷倾斜矫正完整流程）
5. 挑战任务：智能裁剪答题卡

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 9: 编写 modules/06_real_cases.tex（综合实战与行业应用）

**Files:**
- Create: `modules/06_real_cases.tex`

**Step 1: 编写模块内容**

内容要点（约4页）：
1. 试卷预处理完整流程代码（TikZ流程图 + 完整函数）
2. 行业应用案例（医疗影像、工业检测、文档扫描等）

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 10: 编写 modules/07_quiz.tex（课堂测验）

**Files:**
- Create: `modules/07_quiz.tex`

**Step 1: 编写模块内容**

参照 Week01 的 `modules/06_quiz.tex` 和 `sections/summary.tex` 风格（问题+答案分页、代码找错、\highlight{}标注正确答案）。

内容要点（约4页）：
1. 快速问答（4道选择题，问题页+答案页）
2. 代码找错挑战（3个错误的二值化代码）

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 11: 编写 sections/summary.tex（总结与作业）

**Files:**
- Modify: `sections/summary.tex`

**Step 1: 编写总结内容**

参照 Week01 的 `sections/summary.tex` 风格（TikZ流程回顾、核心函数列表、作业要求、下周预告、Q&A页）。

内容要点：
1. 预处理流程回顾（TikZ流程图）
2. 核心代码回顾（cv2.GaussianBlur / createCLAHE / threshold / warpPerspective）
3. 课后作业：实现完整的试卷预处理流水线
4. 知识点网络与下周预告（Week 4：版面分析）
5. Q&A页

**Step 2: 编译验证**

**Step 3: Commit**

---

### Task 12: 生成 images/ 教学示意图

**Files:**
- Create: `images/generate_figures.py`
- Create: `images/pipeline_overview.png`
- Create: `images/noise_types.png`
- Create: `images/convolution_process.png`
- Create: `images/histogram_examples.png`
- Create: `images/binarization_comparison.png`
- Create: `images/transform_types.png`

**Step 1: 编写图片生成脚本**

使用 matplotlib + numpy 生成教学示意图（参照 Week01 的 `images/` 生成脚本模式）：

1. `pipeline_overview.png` — 图像处理流水线（6步流程）
2. `noise_types.png` — 四种噪声类型对比（2x2网格）
3. `convolution_process.png` — 卷积滑动过程示意
4. `histogram_examples.png` — 直方图形态对比（偏暗/正常/偏亮）
5. `binarization_comparison.png` — 三种二值化方法对比
6. `transform_types.png` — 仿射vs透视变换对比

**Step 2: 运行脚本生成图片**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
python images/generate_figures.py
```
Expected: 6张PNG文件生成成功

**Step 3: Commit**

---

### Task 13: 编写 GUI 演示程序

**Files:**
- Create: `code/gui_launcher.py` （Week03版）
- Create: `code/gui_config.py`
- Create: `code/gui_config.ini`
- Create: `code/gui_01_denoising.py`
- Create: `code/gui_02_enhancement.py`
- Create: `code/gui_03_binarization.py`
- Create: `code/gui_04_geometry.py`

**Step 1: 复制 gui_config.py 和 gui_config.ini**

从 Week01 复制并修改标题为 Week03。

**Step 2: 编写 gui_launcher.py（Week03版）**

参照 Week01 的 gui_launcher.py，替换 GUI_DEMOS 列表：

```python
GUI_DEMOS = [
    ("gui_01_denoising.py", "图像去噪演示", "高斯/中值/双边滤波对比 - 可调核大小"),
    ("gui_02_enhancement.py", "图像增强演示", "直方图均衡化/CLAHE/Gamma校正 - 实时预览"),
    ("gui_03_binarization.py", "图像二值化演示", "全局/Otsu/自适应阈值对比 - 可调参数"),
    ("gui_04_geometry.py", "几何变换演示", "仿射/透视变换 - 交互式参数调整"),
]
```

**Step 3: 编写 gui_01_denoising.py**

参照 Week01 的 gui_01_opencv_basics.py 结构：
- customtkinter 框架
- 左侧参数面板（核大小滑块、滤波类型下拉框）
- 右侧 matplotlib 显示区（原图 vs 去噪后对比）
- imread_chinese() 支持中文路径

**Step 4: 编写 gui_02_enhancement.py**

- 参数面板：CLAHE clipLimit/tileGridSize、Gamma值、锐化强度
- 显示区：原图+直方图 vs 增强后+直方图

**Step 5: 编写 gui_03_binarization.py**

- 参数面板：阈值方法选择、阈值大小、adaptiveBlockSize、C值
- 显示区：原图 vs 灰度直方图 vs 二值化结果

**Step 6: 编写 gui_04_geometry.py**

- 参数面板：旋转角度、缩放比例、透视四点位置
- 显示区：原图 vs 变换后图像

**Step 7: 测试运行**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强/code"
python gui_launcher.py
```
Expected: GUI窗口正常启动，4个演示可选择

**Step 8: Commit**

---

### Task 14: 完整编译测试与清理

**Step 1: 完整编译**

```bash
cd "E:/授课/计算机视觉（微）/kejian/cv_wei/slides/week03_图像预处理与增强"
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```
Expected: 无Error，生成main.pdf

**Step 2: 验证PDF页数**

```bash
# 检查PDF是否存在且大小合理
ls -la main.pdf
```
Expected: main.pdf > 500KB，约54页

**Step 3: 清理旧文件**

确认modules/和code/都可用后：
```bash
rm -rf sections_backup sections/00_logistics sections/01_denoising sections/02_enhancement sections/03_binarization sections/04_geometry sections/05_conclusion
```
注意：`sections/` 目录只保留 `summary.tex`。

**Step 4: 清理审查报告等临时文件**

```bash
rm -f week3_*.md
```

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat(week03): complete rewrite aligned with week01 structure"
```

---

## 执行依赖关系

```
Task 1 (目录结构)
  ├── Task 2 (preamble.tex)
  │     └── Task 3 (main.tex)
  │           ├── Task 4 (01_pipeline.tex)
  │           ├── Task 5 (02_denoising.tex)
  │           ├── Task 6 (03_enhancement.tex)
  │           ├── Task 7 (04_binarization.tex)
  │           ├── Task 8 (05_geometry.tex)
  │           ├── Task 9 (06_real_cases.tex)
  │           ├── Task 10 (07_quiz.tex)
  │           └── Task 11 (summary.tex)
  ├── Task 12 (images/)
  └── Task 13 (GUI code/)
        └── Task 14 (编译测试与清理)
```

Tasks 4-13 可以并行执行（每个模块独立）。Task 14 必须在所有其他任务完成后执行。
