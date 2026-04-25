# 学号识别逐气泡检测 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 StudentIdRecognizer 从"Canny+膨胀+网格分割"改为"形态学开运算+连通域分析+逐气泡检测"，与 choice_recognizer 架构一致。

**Architecture:** OTSU BINARY_INV → 形态学开运算（消除网格线）→ connectedComponentsWithStats（检测独立气泡）→ 按质心映射到网格坐标 → 每列取面积最大的组件确定数字。接口签名不变，app.py 可视化从三步边缘检测改为三步气泡检测。

**Tech Stack:** OpenCV (cv2), NumPy, pytest

---

### Task 1: 重写 `_find_bubbles` 和 `_map_to_grid`

**Files:**
- Modify: `docs/auto_grading_system/modules/student_id_recognizer.py` (替换 `_find_grid_region` 为 `_find_bubbles` + `_map_to_grid`)

**Step 1: 写 `_find_bubbles` 方法**

在 `student_id_recognizer.py` 中，删除 `_find_grid_region` 方法（第 23-105 行），替换为：

```python
def _find_bubbles(self, gray_roi):
    """通过 OTSU 二值化 + 形态学开运算 + 连通域分析检测填涂气泡。

    BINARY_INV 使填涂区域变白 → 开运算消除网格线 →
    connectedComponentsWithStats 检测独立气泡。

    Returns:
        list[dict]: 气泡列表 [{cx, cy, area, x, y, w, h}, ...]
    """
    h, w = gray_roi.shape
    total_area = h * w

    # OTSU 二值化（反转：填涂=白）
    _, binary = cv2.threshold(
        gray_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    self._binary_image = binary.copy()

    # 形态学开运算：kernel 尺寸介于网格线宽和气泡直径之间
    cell_est = min(w / self.digit_count, h / self.TOTAL_ROWS)
    ksize = max(int(cell_est * 0.6), 3)
    if ksize % 2 == 0:
        ksize += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    self._opened_image = opened.copy()

    # 可视化底图
    viz = cv2.cvtColor(gray_roi, cv2.COLOR_GRAY2BGR)

    # 连通域分析
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        opened, connectivity=8)

    min_area = total_area * 0.001
    bubbles = []
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        if area < min_area or bw * bh == 0:
            continue
        # 过滤非圆形：宽高比偏离 1 太多
        aspect = bw / bh
        if aspect < 0.3 or aspect > 3.0:
            continue
        cx, cy = centroids[i]
        bubbles.append({
            'cx': float(cx), 'cy': float(cy),
            'area': int(area),
            'x': int(bx), 'y': int(by),
            'w': int(bw), 'h': int(bh),
        })
        cv2.rectangle(viz, (bx, by), (bx + bw, by + bh), (0, 200, 0), 1)

    self._bubble_image = viz
    return bubbles
```

**Step 2: 写 `_map_to_grid` 方法**

紧接 `_find_bubbles` 之后添加：

```python
def _map_to_grid(self, bubbles, roi_shape):
    """将气泡按质心映射到网格坐标 (col, row)。

    将 ROI 按 x 均分为 digit_count 列、按 y 均分为 TOTAL_ROWS 行。
    排除 header 行（top 9%），每个气泡 snap 到最近的网格位置。

    Args:
        bubbles: _find_bubbles 返回的气泡列表
        roi_shape: (h, w) ROI 尺寸

    Returns:
        dict: {col: {row: bubble_dict}}
    """
    h, w = roi_shape
    header_ratio = 1.0 / self.TOTAL_ROWS
    col_w = w / self.digit_count
    row_h = h * (1.0 - header_ratio) / self.ROW_COUNT

    grid = {}
    for b in bubbles:
        col = min(int(b['cx'] / col_w), self.digit_count - 1)
        data_y = b['cy'] - h * header_ratio
        if data_y < 0:
            continue
        row = min(int(data_y / row_h), self.ROW_COUNT - 1)
        if row < 0 or row >= self.ROW_COUNT:
            continue
        grid.setdefault(col, {})
        # 同一位置取面积更大者
        if row not in grid[col] or b['area'] > grid[col][row]['area']:
            grid[col][row] = b
    return grid
```

**Step 3: 更新 `__init__` 中的可视化属性**

将第 19-21 行的：
```python
self._contour_image = None
self._canny_image = None
self._dilated_image = None
```
替换为：
```python
self._binary_image = None
self._opened_image = None
self._bubble_image = None
```

**Step 4: 更新底部属性**

将第 244-257 行的三个属性替换为：

```python
@property
def bubble_image(self):
    """气泡检测结果的可视化图。"""
    return self._bubble_image

@property
def binary_image(self):
    """OTSU 二值化结果。"""
    return self._binary_image

@property
def opened_image(self):
    """形态学开运算后的结果。"""
    return self._opened_image
```

**Step 5: 提交**

```bash
git add docs/auto_grading_system/modules/student_id_recognizer.py
git commit -m "feat(student_id): 替换轮廓检测为形态学气泡检测方法"
```

---

### Task 2: 重写 `_analyze_bubbles` 替换 `_analyze_grid`

**Files:**
- Modify: `docs/auto_grading_system/modules/student_id_recognizer.py` (替换 `_analyze_grid`)

**Step 1: 删除 `_analyze_grid` 并替换为 `_analyze_bubbles`**

删除第 107-174 行的 `_analyze_grid`，替换为：

```python
def _analyze_bubbles(self, roi):
    """通过气泡检测分析学号区域，返回填充率数据。

    Returns:
        dict or None: 分析结果
    """
    if roi is None or roi.size == 0:
        return None

    gray = roi if len(roi.shape) == 2 else cv2.cvtColor(
        roi, cv2.COLOR_BGR2GRAY)

    bubbles = self._find_bubbles(gray)
    if not bubbles:
        return None

    grid = self._map_to_grid(bubbles, gray.shape)
    if not grid:
        return None

    h, w = gray.shape
    header_ratio = 1.0 / self.TOTAL_ROWS
    cell_w = w / self.digit_count
    cell_h = h * (1.0 - header_ratio) / self.ROW_COUNT
    expected_area = cell_w * cell_h * 0.5

    fill_grid = []
    best_rows = []
    best_fills = []
    digits = []

    for col in range(self.digit_count):
        col_fills = []
        best_fill = 0
        best_row = -1

        for row in range(self.ROW_COUNT):
            b = grid.get(col, {}).get(row)
            fill = (b['area'] / expected_area) if b else 0.0
            col_fills.append(fill)
            if fill > best_fill:
                best_fill = fill
                best_row = row

        fill_grid.append(col_fills)
        best_rows.append(best_row)
        best_fills.append(best_fill)

        if best_fill >= self.threshold and best_row >= 0:
            digits.append(str(best_row))
        else:
            digits.append("?")

    return {
        'bounds': (0, h, 0, w),
        'cell_size': (cell_w, cell_h),
        'fill_grid': fill_grid,
        'best_rows': best_rows,
        'best_fills': best_fills,
        'digits': digits,
    }
```

**Step 2: 更新 `recognize` 方法调用**

将 `recognize` 中的 `self._analyze_grid(roi)` 改为 `self._analyze_bubbles(roi)`。

**Step 3: 更新 `recognize_with_viz` 方法调用**

将 `recognize_with_viz` 中的 `self._analyze_grid(roi)` 改为 `self._analyze_bubbles(roi)`。

同时更新 `recognize_with_viz` 中的可视化部分。将第 197-228 行的灰度图叠加逻辑替换为：

```python
gray = roi if len(roi.shape) == 2 else cv2.cvtColor(
    roi, cv2.COLOR_BGR2GRAY)
viz = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

font_scale = max(min(cell_w, cell_h) / 60, 0.25)
font_thick = max(int(font_scale * 2), 1)

# 绘制网格参考线（淡灰）
for col in range(self.digit_count + 1):
    x = int(grid_x0 + col * cell_w)
    cv2.line(viz, (x, 0), (x, h), (220, 220, 220), 1)
for row in range(self.TOTAL_ROWS + 1):
    y = int(grid_y0 + row * cell_h)
    cv2.line(viz, (0, y), (w, y), (220, 220, 220), 1)

for col in range(self.digit_count):
    for row in range(self.ROW_COUNT):
        cx0 = int(grid_x0 + col * cell_w)
        cy0 = int(grid_y0 + (row + 1) * cell_h)  # +1 跳过 header
        cx1 = int(grid_x0 + (col + 1) * cell_w)
        cy1 = int(grid_y0 + (row + 2) * cell_h)

        fill = data['fill_grid'][col][row]
        is_selected = (row == data['best_rows'][col]
                       and fill >= self.threshold)

        if is_selected:
            cv2.rectangle(viz, (cx0, cy0), (cx1, cy1), (0, 200, 0), 2)
            text = str(row)
            cv2.putText(viz, text, (cx0 + 3, cy1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                        (0, 200, 0), font_thick)
        elif fill > self.threshold * 0.5:
            cv2.rectangle(viz, (cx0, cy0), (cx1, cy1),
                          (0, 160, 255), 1)
```

注意：`grid_x0` 和 `grid_y0` 来自 `data['bounds']`，即 `(0, h, 0, w)` 解包为 `grid_y0, grid_y1, grid_x0, grid_x1`，所以 `grid_x0=0, grid_y0=0`。

**Step 4: 提交**

```bash
git add docs/auto_grading_system/modules/student_id_recognizer.py
git commit -m "feat(student_id): 用气泡检测替换网格分割分析逻辑"
```

---

### Task 3: 更新测试

**Files:**
- Modify: `docs/auto_grading_system/tests/test_student_id_recognizer.py`

**Step 1: 更新 `test_contour_image_after_recognize`**

将第 118-123 行替换为：

```python
def test_bubble_image_after_recognize(self):
    digits = [0, 2, 5, 8, 1, 1, 0, 0, 8]
    img = make_student_id_image(digits)
    rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
    rec.recognize(img)
    assert rec.bubble_image is not None
```

**Step 2: 添加新测试验证气泡检测**

在 `TestStudentIdRecognizer` 类末尾添加：

```python
def test_binary_and_opened_images(self):
    digits = [1, 3, 5, 7, 9, 0, 2, 4, 6]
    img = make_student_id_image(digits)
    rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
    rec.recognize(img)
    assert rec.binary_image is not None
    assert rec.opened_image is not None

def test_unfilled_column_returns_question_mark(self):
    """某列未填涂时返回 ?。"""
    digits = [None] * 9
    img = make_student_id_image(digits)
    rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
    result = rec.recognize(img)
    assert result == "?" * 9
```

**Step 3: 运行全部测试**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_student_id_recognizer.py -v
```

Expected: 全部 PASS

**Step 4: 提交**

```bash
git add docs/auto_grading_system/tests/test_student_id_recognizer.py
git commit -m "test(student_id): 更新测试适配气泡检测方案"
```

---

### Task 4: 更新 app.py 可视化

**Files:**
- Modify: `docs/auto_grading_system/app.py` (第 355-384 行)

**Step 1: 替换学号区域可视化部分**

将 app.py 第 355-376 行的三步边缘检测可视化替换为：

```python
                    # 4a-1: 二值化 → 开运算 → 气泡检测（分三步展示）
                    st.markdown("**4a-1  学号区域气泡检测**")

                    _c1, _c2, _c3 = st.columns(3)
                    with _c1:
                        st.caption("Step 1: OTSU 二值化")
                        if sid_rec.binary_image is not None:
                            st.image(sid_rec.binary_image,
                                     use_container_width=True,
                                     caption="BINARY_INV + OTSU")
                    with _c2:
                        st.caption("Step 2: 形态学开运算")
                        if sid_rec.opened_image is not None:
                            st.image(sid_rec.opened_image,
                                     use_container_width=True,
                                     caption="OPEN (消除网格线)")
                    with _c3:
                        st.caption("Step 3: 连通域检测气泡")
                        if sid_rec.bubble_image is not None:
                            st.image(sid_rec.bubble_image,
                                     use_container_width=True,
                                     caption="绿色=检测到的气泡")
```

**Step 2: 更新 4a-2 的标题**

将第 382 行的 `网格扫描` 改为 `气泡识别`：

```python
                        st.markdown(
                            f"**4a-2  气泡识别**  识别结果: `{student_id}`")
```

**Step 3: 提交**

```bash
git add docs/auto_grading_system/app.py
git commit -m "feat(app): 更新学号可视化从边缘检测改为气泡检测"
```

---

### Task 5: 端到端验证

**Step 1: 运行全部测试**

```bash
cd docs/auto_grading_system && python -m pytest tests/ -v
```

Expected: 全部 PASS，无回归。

**Step 2: 检查 app.py 语法**

```bash
cd docs/auto_grading_system && python -c "import app; print('OK')"
```

Expected: `OK`

**Step 3: 最终提交（如有遗漏修复）**

```bash
git add -A && git commit -m "fix: 端到端验证后的最终修正"
```
