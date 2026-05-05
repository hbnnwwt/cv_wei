# 代码质量加固设计

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复 app.py 单模式绕过配置的正确性 bug，消除识别器间 ~100 行重复代码，将所有剩余硬编码参数集中到配置文件或命名常量。

**Architecture:** 三层改进——正确性修复（app.py 统一使用 pipeline 函数）、基类重构（BubbleRecognizerBase 消除 choice/judge/student_id 重复）、参数集中化（defaults.py 常量 + sheet_layout.json/model_config.json 扩展 + 提示词外部化）。

**Tech Stack:** Python 3.10+, OpenCV, openpyxl

---

## 第一部分：正确性修复

### 问题

app.py 单模式步进显示（第 570-648 行）直接实例化 `ChoiceRecognizer`/`JudgeRecognizer` 并硬编码 `question_count=20, question_start=1`，绕过了 `pipeline.recognize_choices()`/`recognize_judges()`（后者从 LAYOUT 配置读取）。结果：批处理遵循配置，单模式不遵循。

### 修复方案

1. **单模式改用 pipeline 函数**：将直接调用识别器的代码替换为 `pipeline.recognize_choices()`/`pipeline.recognize_judges()`，与批处理模式一致。

2. **消除 app.py 中散落的硬编码范围**：
   - `range(1, 20)`/`range(21, 30)` → 从 `LAYOUT` 或 `svc.answer_key` 动态获取
   - `{31: ''}` → 使用 `get_essay_questions()`
   - `q <= 20` 分支 → 使用 `_classify_question()`

3. **共享常量统一到 `defaults.py`**：
   - `IMAGE_EXTS` / `IMAGE_EXTENSIONS` → `defaults.py` 导出
   - `API_KEYS_PATH` / `MODEL_CFG_PATH` → `defaults.py` 导出（接收 `base_dir` 参数）
   - `ANSWER_KEY_PATH` / `PROCESSED_DIR` / `OUTPUT_DIR` → `defaults.py` 导出

### 影响文件

| 文件 | 变更 |
|------|------|
| `modules/defaults.py` | 新增路径常量和 IMAGE_EXTS |
| `app.py` | 单模式改用 pipeline 函数，删除本地硬编码范围 |
| `main.py` | 改用 defaults.py 常量 |

---

## 第二部分：识别器基类重构

### 现状

- `choice_recognizer.py`（398行）和 `judge_recognizer.py`（325行）有 ~100 行完全重复
- `student_id_recognizer.py` 共享 `_trim_margin` 和颜色常量

### 方案：BubbleRecognizerBase 基类

新建 `modules/bubble_base.py`：

```python
class BubbleRecognizerBase:
    # 颜色常量
    COLOR_SELECTED = (0, 200, 0)
    COLOR_HALF = (0, 160, 255)
    COLOR_LINE = (180, 180, 180)

    def __init__(self, threshold=0.06, margin=5):
        self.threshold = threshold
        self.margin = margin

    def _trim_margin(self, image, margin=None): ...
    def _detect_fill_start(self, gray): ...
    def _analyze_zones(self, binary, cell_w, cell_h, zone_count): ...
    def recognize_with_viz(self, region_image): ...  # 子类实现选项标签差异
```

### 基类方法来源

| 方法 | 来源行 | 说明 |
|------|--------|------|
| `_trim_margin` | choice:17 / judge:18 / student_id:34 | 完全相同 |
| `_detect_fill_start` | choice:117-163 / judge:104-150 | 47行完全重复 |
| `_analyze_zones` | choice:26-61 / judge:27-54 | 几乎相同，通过 `zone_count` 参数化 |
| `recognize_with_viz` | choice:73-114 / judge:64-101 | 结构相同，子类通过 `option_labels` 区分 |

### 子类保留逻辑

| 子类 | 保留 |
|------|------|
| `ChoiceRecognizer` | `recognize_all_with_viz()` 网格切分、`_detect_zone_boundaries()`（均匀切分）、P31 污渍检测 |
| `JudgeRecognizer` | `recognize_all_with_viz()` 固定网格、`_detect_cells_fixed()` |
| `StudentIdRecognizer` | 不继承基类（逻辑差异大），但可导入 `_trim_margin` 工具函数 |

### 行数预估

| 文件 | 改前 | 改后 |
|------|------|------|
| `bubble_base.py` | 新建 | ~120 |
| `choice_recognizer.py` | 398 | ~280 |
| `judge_recognizer.py` | 325 | ~220 |
| 合计 | 723 | ~620（净减 ~100） |

---

## 第三部分：硬编码参数集中化

### 3A. 图像处理参数 → defaults.py

| 参数 | 当前 | 改后 | 文件 |
|------|------|------|------|
| 形态学核 `(3,3)` | 9处字面量 | `MORPH_KERNEL = (3, 3)` | choice/judge/student_id |
| 水平投影阈值 `0.02` | 2处 | `FILL_BAND_THRESHOLD = 0.02`（搬入基类后仅一处） | 基类 |
| 气泡尺寸 `0.08/0.30/0.40` | choice 内 | 构造器参数 `bubble_min_w=0.08` 等 | choice |
| Canny `50, 150` | student_id 内 | 构造器参数 `canny_low=50, canny_high=150` | student_id |
| OCR 图片上限 `2048` | essay 内 | 构造器参数 `max_image_side=2048` | essay |

### 3B. API/模型参数 → model_config.json 扩展

| 参数 | 当前位置 | config 字段 |
|------|----------|------------|
| `max_tokens=256` | llm_essay_grader.py:78 | `"llm_max_tokens": 256` |
| `temperature=0.3` | llm_essay_grader.py:79 | `"llm_temperature": 0.3` |
| OCR `max_tokens=1024` | essay_recognizer.py:191 | `"ocr_max_tokens": 1024` |

构造器从 config 读取，fallback 到 defaults.py 的默认值。

### 3C. 评分与布局 → sheet_layout.json 扩展

| 参数 | 当前 | 改后 |
|------|------|------|
| 分值 `3/2/20` | grading.py:38 默认参数 | `sheet_layout.json` 新增 `"scoring": {"choice_score": 3, "judge_score": 2, "essay_max_score": 20}` |
| 选择题网格 `5x4` | choice 内 | 传入 `LAYOUT['choice']` 的 `rows`/`cols` |
| 判断题 `3x4` + cell_mapping | judge:215-217 | 从 `LAYOUT['judge']` 动态生成 |

### 3D. 提示词外部化

| 参数 | 当前 | 改后 |
|------|------|------|
| LLM 评分提示词 | llm_essay_grader.py:52-65 | `config/llm_grading_prompt.txt`，支持 `{reference}/{student_answer}/{max_score}` 占位符 |
| OCR 提示词 | essay_recognizer.py:188 | `model_config.json` `"ocr_prompt"` 字段 |
| LLM 分数解析正则 | llm_essay_grader.py:90 | 与提示词配对存放在 config，或改用 JSON mode |

### 3E. marker.py 硬编码

| 参数 | 改后 |
|------|------|
| 选项标签 `['A','B','C','D']`/`['T','F']` | 从 `LAYOUT` 或子类 `option_labels` 获取 |
| 默认输出目录 `'data/processed'` | `defaults.py` 常量 |

---

## 实施顺序

1. **第一部分**（正确性修复）— app.py 单模式统一用 pipeline，共享常量 → defaults.py
2. **第二部分**（基类重构）— 新建 BubbleRecognizerBase，choice/judge 继承
3. **第三部分**（参数集中化）— defaults.py 常量、config 扩展、提示词外部化

## 不改的文件

- `tests/` — 测试数据不是生产硬编码
- `preprocess.py` — 灰度转换模式虽有重复但分散在不同上下文，重构收益低

## 验证

1. 运行 `pytest tests/ -q` 确认无回归
2. 删除 `config/sheet_layout.json` 后启动 GUI，确认 fallback 默认值正常
3. 修改 `sheet_layout.json` 的 `scoring` 字段，确认 GradingService 行为变化
4. 单模式上传答题卡，确认选择题/判断题识别结果与批处理模式一致
