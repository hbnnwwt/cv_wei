# 学号识别改为逐气泡检测

日期: 2026-04-25

## 问题

`StudentIdRecognizer._find_grid_region` 使用 Canny + 膨胀 + RETR_CCOMP，
检测到的是整个学号网格区域的外轮廓，而非单个填涂气泡。

根因：膨胀把网格线和气泡边缘焊成一个连通区域，缺少"去除网格线、保留气泡"的步骤。

## 方案

形态学分离 + 连通域分析，与 `choice_recognizer` 保持架构一致。

## 数据流

```
灰度 ROI
  → OTSU BINARY_INV（填涂变白）
  → 形态学开运算（kernel > 网格线宽，< 气泡直径 → 擦掉网格线）
  → connectedComponentsWithStats（每个填涂气泡 = 独立连通域）
  → 过滤噪声 + 按质心映射到网格(col, row)
  → 每列取面积最大的组件 → 确定数字
```

## 组件变更

### 删除

- `_find_grid_region` — Canny + 膨胀方案整体废弃

### 新增

**`_find_bubbles(gray_roi)`**
- OTSU BINARY_INV → 形态学开运算（椭圆 kernel，尺寸 = min(roi_w/cols, roi_h/rows) * 0.6）
- connectedComponentsWithStats
- 过滤：面积 < 总面积 0.1% 的噪声；宽高比畸形的非圆形组件
- 返回：`[{cx, cy, area, x, y, w, h}, ...]`

**`_map_to_grid(bubbles, roi_shape, digit_count, total_rows)`**
- 按 x 均分列、按 y 均分行（排除 header 区域 top ~9%）
- 每个气泡质心 snap 到最近网格位置
- 返回：`{col: {row: bubble_info}}`

### 修改

**`_analyze_grid` → `_analyze_bubbles`**
- 调用 `_find_bubbles` + `_map_to_grid`
- 每列找面积最大的气泡，area / expected_bubble_area = 填充率
- 低于 threshold 标记为 `?`
- 输出格式不变

### 不变

- `recognize(roi)` 接口签名和返回值
- `recognize_with_viz(roi)` 接口签名和返回值
- 所有属性（contour_image → bubble_image 等，更换底层实现但属性名更新）

## 可视化

替换 Canny/膨胀/轮廓三张图：
- `binary_image`：OTSU 二值化结果
- `opened_image`：开运算后（网格线消失）
- `bubble_image`：检测到的气泡彩色标注

## 与 choice_recognizer 的一致性

| 步骤 | choice_recognizer | 新 student_id_recognizer |
|------|---|---|
| 二值化 | OTSU BINARY_INV | OTSU BINARY_INV |
| 形态学 | 开运算(3×3椭圆) | 开运算(自适应椭圆) |
| 检测 | connectedComponents | connectedComponents |
| 定位 | 按质心分 zone | 按质心分 grid(col,row) |
| 判定 | zone 内最大填充率 | col 内最大组件面积 |
