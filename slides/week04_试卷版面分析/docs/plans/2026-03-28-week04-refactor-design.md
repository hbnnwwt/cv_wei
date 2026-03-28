# Week 4 课件结构化重构设计

## 日期
2026-03-28

## 目标
对第4周"试卷版面分析"课件进行全面结构化重构：修复编译错误、对齐 preamble、优化结构与视觉、补充内容、生成代码示例。

## 约束
- 保留所有现有知识点
- 可调整章节结构和页面组织
- 图片使用 `figures/答题卡.jpg`（已有）及其他由教师提供的图片
- preamble 对齐到 week01

---

## 第一部分：修复与对齐

### 1.1 修复致命 LaTeX 错误
- `sections/02_edge.tex:225` — 嵌套 `\begin{lstlisting}` → 拆为独立 frame
- `sections/04_geometry.tex:108` — 同上

### 1.2 对齐 preamble 到 week01
- 添加 `tcolorbox` 及 skins/breakable 库
- 添加页面边距设置
- 添加 `\highlight` 自定义命令
- 修正标题为"第4周：试卷版面分析"

---

## 第二部分：结构优化

### 2.1 统一"AI辅助编程"页面模板
格式：tcolorbox 提示框 + lstlisting 完整代码，一个 frame 内完成。

### 2.2 代码排版规范化
- 所有代码 frame 用 `[fragile]`
- 字体统一规范

### 2.3 图片引入
- 使用 `figures/答题卡.jpg` 在概述页和效果展示页
- 为处理结果图预留 `\includegraphics` 占位（教师后续提供）

---

## 第三部分：内容补充

### 3.1 生成 code/ 示例脚本
- `canny_edge_detection.py`
- `contour_detection.py`
- `paper_locator.py`
- `projection_layout.py`

### 3.2 完善互动环节
- 代码拼图具体内容
- 错误找茬具体 bug 代码

---

## 第四部分：视觉提升

### 4.1 tcolorbox 替代部分 block
- AI 辅助提示 → 彩色 tcolorbox
- 注意事项 → 橙色 tcolorbox

### 4.2 TikZ 图表优化
- 版面分析流程图
- 投影波形图

### 4.3 页脚对齐 week01
- 确保 logo 页脚一致

---

## 涉及文件

| 文件 | 改动类型 |
|------|---------|
| `preamble.tex` | 对齐 week01 |
| `sections/02_edge.tex` | 修复嵌套 lstlisting + AI 辅助页面重构 |
| `sections/04_geometry.tex` | 修复嵌套 lstlisting + AI 辅助页面重构 |
| `sections/05_layout.tex` | AI 辅助页面重构 + 图片占位 |
| `sections/00_logistics.tex` | 互动环节具体内容 |
| `sections/01_overview.tex` | TikZ 优化 + 引入答题卡图片 |
| `sections/03_contour.tex` | 排版规范化 |
| `sections/06_conclusion.tex` | 微调 |
| `code/*.py` | 新建 4 个示例脚本 |
