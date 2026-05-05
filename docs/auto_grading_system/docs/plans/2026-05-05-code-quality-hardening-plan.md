# 代码质量加固实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复 app.py 单模式绕过配置的正确性 bug，消除识别器间 ~100 行重复代码，将所有剩余硬编码参数集中到配置文件或命名常量。

**Architecture:** 三阶段——正确性修复（app.py + defaults.py）、基类重构（BubbleRecognizerBase）、参数集中化（config 扩展 + 提示词外部化）。

**Tech Stack:** Python 3.10+, OpenCV, openpyxl

---

## 阶段一：正确性修复（Task 1-3）

### Task 1: defaults.py 扩展共享常量

**Files:**
- Modify: `modules/defaults.py`（全部）
- Modify: `main.py:26-31`（替换本地常量）
- Modify: `app.py:30-34`（替换本地常量）

**Step 1: 扩展 defaults.py**

```python
"""集中管理的默认值常量。"""

import os

# API 默认值
DEFAULT_BASE_URL = "https://api-inference.modelscope.cn"
DEFAULT_LLM_MODEL = "Qwen/Qwen3-235B-A22B"
DEFAULT_OCR_MODEL = "Qwen/Qwen3-VL-235B-A22B-Instruct"

# 图像处理常量
MORPH_KERNEL = (3, 3)
FILL_BAND_THRESHOLD = 0.02

# 路径常量（相对于项目根目录）
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}


def path_constants(base_dir):
    """返回项目路径常量字典。"""
    return {
        'answer_key': os.path.join(base_dir, "参考答案.xlsx"),
        'default_folder': os.path.join(base_dir, "data", "answer_sheets"),
        'output_dir': os.path.join(base_dir, "data", "output"),
        'processed_dir': os.path.join(base_dir, "data", "processed"),
        'api_keys': os.path.join(base_dir, "config", "api_keys.json"),
        'model_config': os.path.join(base_dir, "config", "model_config.json"),
        'batch_checkpoint': os.path.join(base_dir, "data", "output", "_batch_checkpoint.json"),
    }
```

**Step 2: main.py 使用 defaults.py**

替换 `main.py:26-31`，删除 `IMAGE_EXTENSIONS`、`BASE_DIR`、`API_KEYS_PATH`、`MODEL_CFG_PATH` 本地定义，改为：

```python
from modules.defaults import (
    DEFAULT_BASE_URL, DEFAULT_LLM_MODEL, DEFAULT_OCR_MODEL,
    IMAGE_EXTS, path_constants,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATHS = path_constants(BASE_DIR)
```

main.py 中所有引用更新：
- `IMAGE_EXTENSIONS` → `IMAGE_EXTS`
- `API_KEYS_PATH` → `PATHS['api_keys']`
- `MODEL_CFG_PATH` → `PATHS['model_config']`
- `os.path.join(BASE_DIR, "data", "processed")` → `PATHS['processed_dir']`

**Step 3: app.py 使用 defaults.py**

替换 `app.py:30-34`，改为：

```python
from modules.defaults import (
    DEFAULT_BASE_URL, DEFAULT_LLM_MODEL, DEFAULT_OCR_MODEL,
    IMAGE_EXTS, path_constants,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATHS = path_constants(BASE_DIR)
```

app.py 中所有引用更新：
- `IMAGE_EXTS` 局部变量 → 已从 defaults 导入
- `ANSWER_KEY_PATH` → `PATHS['answer_key']`
- `os.path.join(BASE_DIR, "data", "processed")` (2处: L768, L896) → `PATHS['processed_dir']`
- `os.path.join(BASE_DIR, "data", "output")` (L392) → `PATHS['output_dir']`
- `os.path.join(BASE_DIR, "config", "api_keys.json")` (L158) → `PATHS['api_keys']`
- `os.path.join(BASE_DIR, "config", "model_config.json")` (L159) → `PATHS['model_config']`
- `os.path.join(BASE_DIR, "data", "output", "_batch_checkpoint.json")` (L925) → `PATHS['batch_checkpoint']`

**Step 4: Run tests**

Run: `cd E:\授课\计算机视觉（微）\kejian\cv_wei\docs\auto_grading_system && python -m pytest tests/ -q`
Expected: PASS（无功能变更）

**Step 5: Commit**

```bash
git add modules/defaults.py main.py app.py
git commit -m "refactor: 统一共享常量到 defaults.py"
```

---

### Task 2: app.py 单模式改用 pipeline 函数

**Files:**
- Modify: `app.py:569-648`（选择题/判断题识别）

**Step 1: 替换选择题识别代码**

将 `app.py:572-578`:
```python
choice_answers = {}
if regions1.get('choice'):
    x, y, w, h = regions1['choice']
    choice_roi = p1_orig[y:y + h, x:x + w]
    choice_rec = ChoiceRecognizer(threshold=threshold)
    choice_all_result = choice_rec.recognize_all_with_viz(
        choice_roi, question_count=20, question_start=1)
    choice_answers = choice_all_result['answers']
```

替换为:
```python
choice_answers = {}
choice_all_result = {'cell_results': [], 'grid_viz': None}
if regions1.get('choice'):
    choice_answers, choice_cells_data = recognize_choices(
        p1_orig, regions1, threshold, return_details=True)
    # 仍需完整结果用于可视化
    from modules.pipeline import LAYOUT as _L
    _ch = _L['choice']
    from modules.choice_recognizer import ChoiceRecognizer
    _cr = ChoiceRecognizer(threshold=threshold)
    x, y, w, h = regions1['choice']
    choice_roi = p1_orig[y:y + h, x:x + w]
    choice_all_result = _cr.recognize_all_with_viz(
        choice_roi,
        question_count=_ch['question_count'],
        question_start=_ch['question_start'])
    choice_answers = choice_all_result['answers']
```

**Step 2: 替换判断题识别代码**

将 `app.py:642-648`:
```python
judge_answers = {}
if regions2.get('judge'):
    x, y, w, h = regions2['judge']
    judge_roi = p2_orig[y:y + h, x:x + w]
    judge_rec = JudgeRecognizer(threshold=threshold)
    judge_all_result = judge_rec.recognize_all_with_viz(judge_roi)
    judge_answers = judge_all_result['answers']
```

替换为:
```python
judge_answers = {}
judge_all_result = {'cell_results': [], 'grid_viz': None}
if regions2.get('judge'):
    from modules.pipeline import LAYOUT as _L
    _ju = _L['judge']
    from modules.judge_recognizer import JudgeRecognizer
    _jr = JudgeRecognizer(threshold=threshold)
    x, y, w, h = regions2['judge']
    judge_roi = p2_orig[y:y + h, x:x + w]
    judge_all_result = _jr.recognize_all_with_viz(
        judge_roi,
        question_count=_ju['question_count'],
        question_start=_ju['question_start'])
    judge_answers = judge_all_result['answers']
```

**Step 3: 验证**

Run: `cd E:\授课\计算机视觉（微）\kejian\cv_wei\docs\auto_grading_system && python -c "from modules.pipeline import LAYOUT; print(LAYOUT)"`
Expected: 打印 LAYOUT 配置内容，无报错

**Step 4: Commit**

```bash
git add app.py
git commit -m "fix: app.py 单模式从 LAYOUT 配置读取题号范围"
```

---

### Task 3: app.py 消除散落的硬编码范围

**Files:**
- Modify: `app.py:741,749,753,887,1014-1020,1047,1059-1063`

**Step 1: 简答题题号 `{31: ''}` 改用 `get_essay_questions()`**

替换 `app.py:741`:
```python
"essay": {q: essay_text for q in svc.answer_key.get('essay', {31: ''})} if essay_text else {},
```
改为:
```python
"essay": {q: essay_text for q in get_essay_questions(svc.answer_key)} if essay_text else {},
```

替换 `app.py:887` 同理。

在 app.py 顶部导入中添加 `get_essay_questions`:
```python
from modules.pipeline import (
    preprocess_and_analyze, extract_student_id,
    recognize_choices, recognize_judges, recognize_essay,
    get_essay_questions,
)
```

**Step 2: `_render_question_table` 调用改用动态范围**

替换 `app.py:749`:
```python
rows = _render_question_table(1, 20, choice_answers, result["choice"])
```
改为:
```python
_ch = LAYOUT['choice']
rows = _render_question_table(
    _ch['question_start'],
    _ch['question_start'] + _ch['question_count'] - 1,
    choice_answers, result["choice"])
```

替换 `app.py:753` 同理用 `_ju = LAYOUT['judge']`。
替换 `app.py:1014-1020` 同理。

**Step 3: XLSX 导出 `range(1, 31)` 和 `q <= 20` 改用动态范围**

替换 `app.py:1047-1063`:
```python
for q in range(1, 31):
    headers.append(f"Q{q}")
```
改为:
```python
_ch = LAYOUT['choice']
_ju = LAYOUT['judge']
choice_start = _ch['question_start']
choice_end = choice_start + _ch['question_count'] - 1
judge_start = _ju['question_start']
judge_end = judge_start + _ju['question_count'] - 1
for q in range(choice_start, judge_end + 1):
    headers.append(f"Q{q}")
```

替换 `app.py:1059-1063`:
```python
for q in range(1, 31):
    if q <= 20:
        row.append(r["choice"].get(q, "-"))
    else:
        row.append(r["judge"].get(q, "-"))
```
改为:
```python
for q in range(choice_start, judge_end + 1):
    if q <= choice_end:
        row.append(r["choice"].get(q, "-"))
    else:
        row.append(r["judge"].get(q, "-"))
```

**Step 4: 在 app.py 顶部导入 LAYOUT**

```python
from modules.pipeline import LAYOUT
```

**Step 5: Run tests + Commit**

```bash
python -m pytest tests/ -q
git add app.py
git commit -m "refactor: app.py 所有题号范围改为 LAYOUT 动态读取"
```

---

## 阶段二：识别器基类重构（Task 4-5）

### Task 4: 新建 BubbleRecognizerBase 基类

**Files:**
- Create: `modules/bubble_base.py`

**Step 1: 编写基类**

```python
"""选择题/判断题识别器的共享基类。

抽取 _trim_margin、_analyze_zones、_detect_fill_start、
recognize_with_viz 等重复方法。
"""

import cv2
import numpy as np

from modules.defaults import MORPH_KERNEL, FILL_BAND_THRESHOLD


class BubbleRecognizerBase:
    """气泡填涂识别器基类。"""

    # 共享颜色常量
    COLOR_SELECTED = (0, 200, 0)
    COLOR_HALF = (0, 160, 255)
    COLOR_LINE = (180, 180, 180)

    def __init__(self, threshold=0.06, margin=5, zone_count=4,
                 option_labels=None):
        self.threshold = threshold
        self.margin = margin
        self.zone_count = zone_count
        self.option_labels = option_labels or [
            chr(ord('A') + i) for i in range(zone_count)]

    def _trim_margin(self, image):
        """裁剪图像四周边距。"""
        m = self.margin
        if m <= 0:
            return image
        h, w = image.shape[:2]
        if h <= 2 * m or w <= 2 * m:
            return image
        return image[m:-m, m:-m]

    def _analyze_zones(self, image):
        """分析各区域像素密度。

        Returns:
            dict: zone_fills, best_idx, above_threshold
        """
        gray = image if len(image.shape) == 2 else cv2.cvtColor(
            image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, MORPH_KERNEL)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        img_h, img_w = binary.shape
        zone_w = img_w / self.zone_count
        zone_fills = [0.0] * self.zone_count

        for z in range(self.zone_count):
            zx0 = int(z * zone_w)
            zx1 = int((z + 1) * zone_w)
            zone_pixels = binary[:, zx0:zx1]
            total = zone_pixels.size
            black = np.count_nonzero(zone_pixels)
            zone_fills[z] = black / total if total > 0 else 0.0

        best_idx = max(range(self.zone_count), key=lambda z: zone_fills[z])
        return {
            'zone_fills': zone_fills,
            'best_idx': best_idx,
            'above_threshold': zone_fills[best_idx] >= self.threshold,
        }

    def _detect_fill_start(self, gray):
        """通过水平投影频带检测填涂区域起始行。"""
        h, w = gray.shape
        _, binary = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, MORPH_KERNEL)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        proj = np.sum(binary, axis=1).astype(np.float64) / (255.0 * w)

        bands = []
        in_band = False
        band_start = 0
        for row in range(h):
            if proj[row] >= FILL_BAND_THRESHOLD:
                if not in_band:
                    band_start = row
                    in_band = True
            else:
                if in_band:
                    bands.append((band_start, row))
                    in_band = False
        if in_band:
            bands.append((band_start, h))

        if not bands:
            return 0

        min_h = h * 0.03
        while bands and (bands[0][1] - bands[0][0]) < min_h:
            bands = bands[1:]
        while bands and (bands[-1][1] - bands[-1][0]) < min_h:
            bands = bands[:-1]

        if not bands:
            return 0

        max_band_h = max(e - s for s, e in bands)
        for s, e in bands:
            if (e - s) >= max_band_h * 0.8:
                return s

        return 0

    def recognize(self, image, options=None):
        """识别填涂区域，返回选中的选项。"""
        image = self._trim_margin(image)
        if options is None:
            options = self.option_labels
        data = self._analyze_zones(image)
        if not data['above_threshold']:
            return None
        return options[data['best_idx']]

    def recognize_with_viz(self, image, options=None):
        """识别填涂区域并返回可视化标注图。

        Returns:
            tuple: (result, viz_image, zone_fills)
        """
        image = self._trim_margin(image)
        if options is None:
            options = self.option_labels

        data = self._analyze_zones(image)
        result = (options[data['best_idx']]
                  if data['above_threshold'] else None)

        gray = image if len(image.shape) == 2 else cv2.cvtColor(
            image, cv2.COLOR_BGR2GRAY)
        viz = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        img_h, img_w = gray.shape
        zone_w = img_w / self.zone_count
        font_scale = max(zone_w / 60, 0.3)
        font_thick = max(int(font_scale * 2), 1)

        for z in range(self.zone_count):
            zx0 = int(z * zone_w)
            zx1 = int((z + 1) * zone_w)
            fill = data['zone_fills'][z]
            is_selected = (z == data['best_idx'] and data['above_threshold'])

            if is_selected:
                cv2.rectangle(viz, (zx0, 0), (zx1, img_h),
                              self.COLOR_SELECTED, 2)
                text = f"{options[z]}:{fill:.0%}"
                cv2.putText(viz, text, (zx0 + 3, img_h - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                            self.COLOR_SELECTED, font_thick)
            elif fill > self.threshold * 0.5:
                cv2.rectangle(viz, (zx0, 0), (zx1, img_h),
                              self.COLOR_HALF, 1)

        for z in range(1, self.zone_count):
            x = int(z * zone_w)
            cv2.line(viz, (x, 0), (x, img_h), self.COLOR_LINE, 1)

        return result, viz, data['zone_fills']
```

**Step 2: Run import check**

Run: `cd E:\授课\计算机视觉（微）\kejian\cv_wei\docs\auto_grading_system && python -c "from modules.bubble_base import BubbleRecognizerBase; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add modules/bubble_base.py
git commit -m "feat: 新增 BubbleRecognizerBase 识别器基类"
```

---

### Task 5: ChoiceRecognizer / JudgeRecognizer 继承基类

**Files:**
- Modify: `modules/choice_recognizer.py`（大幅简化）
- Modify: `modules/judge_recognizer.py`（大幅简化）

**Step 1: 重写 choice_recognizer.py**

删除 `_trim_margin`、`_analyze_zones`、`recognize`、`recognize_with_viz`、`_detect_fill_start`（全部由基类提供），仅保留：
- `__init__`（调用 `super().__init__(threshold, margin, option_count=4, option_labels=['A','B','C','D'])`）
- `_detect_zone_boundaries`（选择题特有的连通域 + fallback 均匀切分）
- `_select_best_bubbles`（辅助方法）
- `_detect_rows_fixed`（网格切分）
- `recognize_all_with_viz`（批量识别，使用 `self.zone_count` 替换 `self.option_count`，使用 `self.option_labels` 替换局部 `options`）

```python
import cv2
import numpy as np

from modules.bubble_base import BubbleRecognizerBase
from modules.defaults import MORPH_KERNEL


class ChoiceRecognizer(BubbleRecognizerBase):
    """选择题填涂识别模块。"""

    def __init__(self, threshold=0.06, option_count=4, margin=5):
        super().__init__(
            threshold=threshold, margin=margin,
            zone_count=option_count,
            option_labels=[chr(ord('A') + i) for i in range(option_count)])

    @property
    def option_count(self):
        return self.zone_count

    # _detect_zone_boundaries 保持不变（连通域 + fallback 均匀切分）
    # _select_best_bubbles 保持不变
    # _detect_rows_fixed 保持不变
    # recognize_all_with_viz 保持不变，但：
    #   - self.option_count → self.zone_count
    #   - 局部 options 参数 → self.option_labels
    #   - 颜色常量 → self.COLOR_SELECTED / self.COLOR_HALF / self.COLOR_LINE
```

**Step 2: 重写 judge_recognizer.py**

同上，删除重复方法，仅保留：
- `__init__`（调用 `super().__init__(threshold, margin, zone_count=2, option_labels=['T', 'F'])`）
- `_detect_zone_boundaries`（判断题特有的均匀切分）
- `_detect_cells_fixed`（固定网格切分）
- `recognize_all_with_viz`（批量识别）

**Step 3: Run tests**

Run: `cd E:\授课\计算机视觉（微）\kejian\cv_wei\docs\auto_grading_system && python -m pytest tests/ -q`
Expected: PASS

**Step 4: Commit**

```bash
git add modules/choice_recognizer.py modules/judge_recognizer.py modules/bubble_base.py
git commit -m "refactor: choice/judge 识别器继承 BubbleRecognizerBase，消除 ~100 行重复"
```

---

## 阶段三：硬编码参数集中化（Task 6-9）

### Task 6: 图像处理参数参数化

**Files:**
- Modify: `modules/student_id_recognizer.py:18,49`（Canny 参数参数化）
- Modify: `modules/essay_recognizer.py:168`（OCR 图片上限参数化）
- Modify: `modules/choice_recognizer.py`（气泡尺寸约束参数化）

**Step 1: StudentIdRecognizer Canny 参数**

在 `__init__` 中新增 `canny_low=50, canny_high=150` 参数，存储为实例属性。
`_detect_grid` 中 `cv2.Canny(gray_roi, 50, 150)` 改为 `cv2.Canny(gray_roi, self.canny_low, self.canny_high)`。

**Step 2: EssayRecognizer OCR 图片上限**

在 `__init__` 中新增 `max_image_side=2048` 参数，存储为实例属性。
`_recognize_online` 中 `max_side = 2048` 改为 `max_side = self.max_image_side`。

**Step 3: ChoiceRecognizer 气泡尺寸约束**

在 `__init__` 中新增 `bubble_min_w=0.08, bubble_max_w=0.30, bubble_min_h=0.40` 参数。
`_detect_zone_boundaries` 中对应字面量改为实例属性。

**Step 4: Run tests + Commit**

```bash
python -m pytest tests/ -q
git add modules/student_id_recognizer.py modules/essay_recognizer.py modules/choice_recognizer.py
git commit -m "refactor: 图像处理参数改为构造器参数"
```

---

### Task 7: model_config.json 扩展 + 构造器读取

**Files:**
- Modify: `config/model_config.json`（新增 3 个字段）
- Modify: `modules/llm_essay_grader.py:37,75-79`（从配置读取）
- Modify: `modules/essay_recognizer.py`（从配置读取 OCR max_tokens）

**Step 1: 扩展 model_config.json**

```json
{
  "base_url": "https://api-inference.modelscope.cn",
  "llm_model": "Qwen/Qwen3-235B-A22B",
  "llm_max_tokens": 256,
  "llm_temperature": 0.3,
  "ocr_model": "Qwen/Qwen3-VL-235B-A22B-Instruct",
  "ocr_max_tokens": 1024,
  "ocr_prompt": "请逐行识别图片中的所有文字内容，只输出文字，不要添加解释。"
}
```

**Step 2: LLMEssayGrader 从配置读取**

`__init__` 新增 `max_tokens=256, temperature=0.3` 参数，存储为实例属性。
`_call_api` 中 `"max_tokens": 256` → `self.max_tokens`，`"temperature": 0.3` → `self.temperature`。

调用方（`app.py`、`main.py`）在构造时从 model_config 读取对应字段并传入。

**Step 3: EssayRecognizer 从配置读取 OCR 参数**

`_recognize_online` 中 `"max_tokens": 1024` 改为从 `self.api_config` 读取 `ocr_max_tokens`，fallback 到 1024。
OCR 提示词改为从 `self.api_config` 读取 `ocr_prompt`，fallback 到默认字符串。

**Step 4: Run tests + Commit**

```bash
python -m pytest tests/ -q
git add config/model_config.json modules/llm_essay_grader.py modules/essay_recognizer.py app.py main.py
git commit -m "refactor: API 参数从 model_config.json 读取"
```

---

### Task 8: sheet_layout.json 扩展 + 评分/网格配置集中化

**Files:**
- Modify: `config/sheet_layout.json`（新增 scoring 字段）
- Modify: `modules/grading.py`（从配置读取默认分值）
- Modify: `modules/judge_recognizer.py:215-217`（从 LAYOUT 动态生成 cell_mapping）
- Modify: `modules/choice_recognizer.py:258`（从 LAYOUT 读取 fixed_grid）

**Step 1: 扩展 sheet_layout.json**

```json
{
  "choice": {"rows": 5, "cols": 4, "question_start": 1, "question_count": 20},
  "judge":  {"rows": 3, "cols": 4, "question_start": 21, "question_count": 10},
  "layout": {
    "page1_fallback": {"student_id": [0.06, 0.26], "choice": [0.28, 0.80]},
    "page2_fallback": {"judge": [0.06, 0.46], "essay": [0.50, 0.90]}
  },
  "scoring": {
    "choice_score": 3,
    "judge_score": 2,
    "essay_max_score": 20
  }
}
```

**Step 2: GradingService.from_xlsx 从 LAYOUT 读取默认分值**

`modules/grading.py` 的 `from_xlsx()` 方法末尾改为：
```python
_scoring = LAYOUT.get('scoring', {})
return cls(answer_key,
           choice_score=_scoring.get('choice_score', 3),
           judge_score=_scoring.get('judge_score', 2),
           essay_max_score=_scoring.get('essay_max_score', 20))
```

**Step 3: JudgeRecognizer cell_mapping 动态生成**

`recognize_all_with_viz` 中:
```python
# 改为从参数读取
cell_mapping = list(range(question_start, question_start + question_count))
total_cells = rows_n * cols_n
cell_mapping += [None] * (total_cells - len(cell_mapping))
cells = self._detect_cells_fixed(gray_fill, rows_n, cols_n, cell_mapping)
```

新增 `rows_n`/`cols_n` 参数（从 LAYOUT 传入）。

**Step 4: ChoiceRecognizer fixed_grid 从 LAYOUT 传入**

`recognize_all_with_viz` 新增 `fixed_grid=None` 参数，默认从 LAYOUT 读取。

**Step 5: Run tests + Commit**

```bash
python -m pytest tests/ -q
git add config/sheet_layout.json modules/grading.py modules/judge_recognizer.py modules/choice_recognizer.py
git commit -m "refactor: 评分/网格配置从 sheet_layout.json 读取"
```

---

### Task 9: 提示词外部化 + marker.py 硬编码清理

**Files:**
- Create: `config/llm_grading_prompt.txt`
- Modify: `modules/llm_essay_grader.py:52-66`（从文件加载提示词）
- Modify: `modules/marker.py:107,117,86`（选项标签和输出目录）

**Step 1: 创建提示词模板**

`config/llm_grading_prompt.txt`:
```
你是一个阅卷助手。请根据参考答案评估学生答案。

注意事项：
- 学生答案是通过 OCR 从手写文字识别的，可能存在识别错误（形近字、同音字）
- 请根据语义判断，容忍合理的 OCR 识别偏差
- 如果答案明显不确定或 OCR 识别质量差，请在反馈中说明

参考答案：{reference}
学生答案：{student_answer}
满分：{max_score}分

请严格按以下格式返回（不要输出其他内容）：
得分：X
反馈：一句话评语
```

**Step 2: LLMEssayGrader 从文件加载提示词**

`__init__` 新增 `prompt_template=None` 参数，为 None 时尝试加载 `config/llm_grading_prompt.txt`，再 fallback 到内联默认值。

`_build_prompt` 改为 `self.prompt_template.format(reference=..., student_answer=..., max_score=...)`。

**Step 3: marker.py 选项标签从 pipeline 获取**

`mark_and_save` 新增 `choice_labels=None, judge_labels=None` 参数，默认值分别为 `['A','B','C','D']` 和 `['T','F']`。
`app.py`/`main.py` 调用时传入实际标签。

`output_dir` 默认值改为 `PATHS['processed_dir']`（从 defaults 导入）。

**Step 4: Run tests + Commit**

```bash
python -m pytest tests/ -q
git add config/llm_grading_prompt.txt modules/llm_essay_grader.py modules/marker.py app.py main.py
git commit -m "refactor: 提示词外部化 + marker 硬编码清理"
```

---

## 最终验证

```bash
python -m pytest tests/ -q
python -c "from modules.pipeline import LAYOUT; print(LAYOUT)"
python -c "from modules.bubble_base import BubbleRecognizerBase; print('OK')"
python -c "from modules.grading import GradingService; print(GradingService.__init__.__defaults__)"
```

确认：
1. 所有测试通过
2. LAYOUT 配置正确加载
3. 基类导入正常
4. GradingService 默认分值从配置读取
