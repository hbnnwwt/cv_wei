# Week03 课件完全重写设计方案

## 日期: 2026-03-28

## 背景

Week03「图像预处理与增强」需要完全重写，沿袭 Week01 的成熟模式，使两周课件在结构、风格、质量上完全一致。

## 当前状态

- Week03 已有模块化结构（6大模块，30+ tex文件），但与 Week01 风格差异大
- 修复后评分从3.0提升到7.75，但距理想状态还有差距
- figures/为空，缺少可视化素材
- preamble缺少tcolorbox、自定义命令、页面边距设置

## 设计方案

### 1. 目录结构（对齐Week01）

```
week03_图像预处理与增强/
├── main.tex              # 主控文件（内联课前/概览/时间/分组/多屏/代码对应关系）
├── preamble.tex          # 对齐Week01：tcolorbox + 自定义命令 + 页面边距
├── modules/              # 扁平化教学模块
│   ├── 01_pipeline.tex       # 图像处理流水线概述
│   ├── 02_denoising.tex      # 图像去噪
│   ├── 03_enhancement.tex    # 图像增强
│   ├── 04_binarization.tex   # 图像二值化
│   ├── 05_geometry.tex       # 几何变换
│   ├── 06_real_cases.tex     # 综合实战与行业应用
│   └── 07_quiz.tex           # 课堂测验
├── sections/
│   └── summary.tex           # 总结与作业
├── code/                 # GUI演示程序
│   ├── gui_launcher.py
│   ├── gui_config.py
│   ├── gui_config.ini
│   ├── gui_01_denoising.py
│   ├── gui_02_enhancement.py
│   ├── gui_03_binarization.py
│   ├── gui_04_geometry.py
│   └── images/               # 测试图像
├── images/               # 教学示意图（Python生成）
└── teacher_guide/        # 教师版（保留）
```

### 2. main.tex 结构（对齐Week01）

内联页面：标题页 → 课前预备知识 → 课程概览 → 时间分配 → 分组策略 → 多屏协同 → 代码演示对应关系 → modules → summary

### 3. preamble.tex 对齐

- tcolorbox（skins, breakable）
- 页面边距（左0.5cm/右0.5cm/底1cm/顶0.5cm）
- 自定义命令（\highlight, \code）
- 字号10pt

### 4. modules/ 教学模块

| 模块 | 内容 | 页数 |
|---|---|---|
| 01_pipeline | 流水线概述、应用场景、学习路径 | 6页 |
| 02_denoising | 噪声模型、卷积、滤波器、代码实战、对比 | 12页 |
| 03_enhancement | 直方图、均衡化、CLAHE、Gamma、锐化 | 10页 |
| 04_binarization | 二值化原理、全局/Otsu/自适应、代码实战 | 10页 |
| 05_geometry | 仿射、透视变换、自动矫正实战 | 8页 |
| 06_real_cases | 综合案例、行业应用 | 4页 |
| 07_quiz | 课堂测验 | 4页 |

### 5. GUI演示程序

4个GUI演示程序，使用gui_launcher模式统一管理。

### 6. images/ 示意图

用Python生成6张教学图示。

## 验收标准

- 编译通过（xelatex main.tex）
- 目录结构与Week01一致
- preamble配置与Week01对齐
- 代码演示可运行
- 示意图生成成功
