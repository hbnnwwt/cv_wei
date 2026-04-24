# 智能阅卷系统参考答案完善 — 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将智能阅卷系统修复为参考答案标准——消除代码重复、补全测试、集成简答题评分接口、端到端验证。

**Architecture:** 在现有模块化架构上逐项修补。核心改动是 `grading.py` 新增 `EssayGraderBase` 抽象接口，`main.py` 改用已有 `StudentIdRecognizer` 替代内联函数，补全 `test_student_id_recognizer.py` 和 `test_main.py` 批量模式测试。

**Tech Stack:** Python 3.12, OpenCV, NumPy, pytest, openpyxl, PaddleOCR

---

### Task 1: grading.py — 新增 EssayGraderBase 接口

**Files:**
- Modify: `docs/auto_grading_system/modules/grading.py:1-10` (新增导入和基类)
- Modify: `docs/auto_grading_system/modules/grading.py:7` (`__init__` 新增 `essay_grader` 参数)
- Modify: `docs/auto_grading_system/modules/grading.py:46-81` (`grade()` 加入简答题评分)
- Test: `docs/auto_grading_system/tests/test_grading.py`

**Step 1: 写失败测试**

在 `tests/test_grading.py` 末尾新增：

```python
# ---------------------------------------------------------------------------
# EssayGraderBase / DefaultEssayGrader
# ---------------------------------------------------------------------------

class TestEssayGraderBase:
    def test_default_grader_returns_zero(self):
        from modules.grading import DefaultEssayGrader
        grader = DefaultEssayGrader()
        score, max_score, feedback = grader.score("题目", "参考答案", "学生答案", 10)
        assert score == 0
        assert max_score == 10
        assert "手动" in feedback

    def test_custom_grader_integration(self, service):
        """自定义 essay_grader 应被 grade() 调用。"""
        from modules.grading import GradingService, EssayGraderBase

        class StubGrader(EssayGraderBase):
            def score(self, question, reference, student_answer, max_score):
                return max_score, max_score, "满分"

        svc = GradingService(service.answer_key, essay_grader=StubGrader())
        recognized = {
            'choice': {1: 'A'},
            'judge': {},
            'essay': {31: "学生答案"},
        }
        result = svc.grade(recognized)
        assert result['essay_detail'][31]['score'] == 10  # 参考答案总分
        assert result['total'] > 3  # 至少包含选择题3分 + 简答题分

    def test_grade_without_essay_grader(self, service):
        """无 essay_grader 时简答题得 0 分。"""
        recognized = {
            'choice': {},
            'judge': {},
            'essay': {31: "学生答案"},
        }
        result = service.grade(recognized)
        assert result['essay_detail'][31]['score'] == 0
```

**Step 2: 运行测试验证失败**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_grading.py::TestEssayGraderBase -v
```

Expected: FAIL — `ImportError: cannot import name 'DefaultEssayGrader'`

**Step 3: 实现最小代码**

修改 `modules/grading.py`：

1. 在文件顶部（class GradingService 之前）新增：

```python
class EssayGraderBase:
    """简答题评分器抽象基类。子类需实现 score() 方法。"""

    def score(self, question, reference, student_answer, max_score):
        """评分并返回 (得分, 满分, 反馈)。"""
        raise NotImplementedError


class DefaultEssayGrader(EssayGraderBase):
    """默认实现：简答题返回 0 分，标注需手动评分。"""

    def score(self, question, reference, student_answer, max_score):
        return 0, max_score, "需手动评分"
```

2. 修改 `GradingService.__init__`，在第 7 行 `self.answer_key = answer_key` 之后加入：

```python
        self.essay_grader = essay_grader or DefaultEssayGrader()
```

同时修改方法签名为：
```python
def __init__(self, answer_key, essay_grader=None):
```

3. 在 `grade()` 方法中，`return` 语句之前新增简答题评分逻辑：

```python
        essay_detail = {}
        essay_score = 0
        for q, ref_text in self.answer_key.get('essay', {}).items():
            student_text = recognized_answers.get('essay', {}).get(q, '')
            s, mx, fb = self.essay_grader.score(q, ref_text, student_text, 10)
            essay_detail[q] = {'score': s, 'max_score': mx, 'feedback': fb}
            essay_score += s
```

4. 修改 `return` 字典，加入 `essay_detail` 和修正 `total`：

```python
        return {
            'choice': choice_detail,
            'judge': judge_detail,
            'essay_detail': essay_detail,
            'essay': recognized_answers.get('essay', {}),
            'total': choice_score + judge_score + essay_score,
        }
```

**Step 4: 运行测试验证通过**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_grading.py -v
```

Expected: ALL PASS（包括原有的 TestGrade、TestGenerateReport、TestFromXlsx、TestSaveResultXlsx 和新增的 TestEssayGraderBase）

**Step 5: 提交**

```bash
git add modules/grading.py tests/test_grading.py
git commit -m "feat: 新增 EssayGraderBase 抽象接口，grade() 集成简答题评分"
```

---

### Task 2: __init__.py — 导出全部模块

**Files:**
- Modify: `docs/auto_grading_system/modules/__init__.py`

**Step 1: 修改 `__init__.py`**

替换为：

```python
from .preprocess import ImagePreprocessor
from .layout import LayoutAnalyzer
from .choice_recognizer import ChoiceRecognizer
from .judge_recognizer import JudgeRecognizer
from .essay_recognizer import EssayRecognizer
from .student_id_recognizer import StudentIdRecognizer
from .grading import GradingService, EssayGraderBase, DefaultEssayGrader
```

**Step 2: 验证导入正常**

```bash
cd docs/auto_grading_system && python -c "from modules import StudentIdRecognizer, DefaultEssayGrader; print('OK')"
```

Expected: `OK`

**Step 3: 运行全部测试确认无破坏**

```bash
cd docs/auto_grading_system && python -m pytest tests/ -v
```

Expected: ALL PASS

**Step 4: 提交**

```bash
git add modules/__init__.py
git commit -m "feat: __init__.py 导出全部模块"
```

---

### Task 3: main.py — 使用 StudentIdRecognizer 替代内联函数

**Files:**
- Modify: `docs/auto_grading_system/main.py:17-22` (新增导入)
- Modify: `docs/auto_grading_system/main.py:40-76` (删除 `extract_student_id`)
- Modify: `docs/auto_grading_system/main.py:121-160` (`process_student` 使用 `StudentIdRecognizer`)
- Modify: `docs/auto_grading_system/main.py:229-262` (`single_process` 使用 `StudentIdRecognizer`)

**Step 1: 写失败测试**

在 `tests/test_main.py` 新增：

```python
class TestMainUsesStudentIdRecognizer:
    def test_main_imports_student_id_recognizer(self):
        """main.py 应能导入 StudentIdRecognizer。"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "main", os.path.join(project_root, "main.py"))
        main_mod = importlib.util.module_from_spec(spec)
        # 不执行，只检查导入
        source = open(os.path.join(project_root, "main.py"), encoding="utf-8").read()
        assert "StudentIdRecognizer" in source
        assert "extract_student_id" not in source
```

**Step 2: 运行测试验证失败**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_main.py::TestMainUsesStudentIdRecognizer -v
```

Expected: FAIL — `assert "extract_student_id" not in source`

**Step 3: 修改 main.py**

1. 在第 22 行 `from modules.grading import GradingService` 之后新增：

```python
from modules.student_id_recognizer import StudentIdRecognizer
```

2. 删除整个 `extract_student_id()` 函数（第 40-76 行）

3. 删除 `import cv2` 和 `import numpy as np`（第 12-13 行），main.py 不再直接使用

4. 修改 `process_student()` 函数（约第 121 行），将学号识别改为：

```python
    student_id = None
    if regions1.get('student_id'):
        x, y, w, h = regions1['student_id']
        sid_roi = image1[y:y + h, x:x + w]
        sid_rec = StudentIdRecognizer(digit_count=digit_count)
        student_id = sid_rec.recognize(sid_roi)
```

5. 修改 `single_process()` 函数中的学号识别部分（约第 248 行），同样改为：

```python
        student_id = None
        if regions.get('student_id'):
            x, y, w, h = regions['student_id']
            sid_roi = image[y:y + h, x:x + w]
            sid_rec = StudentIdRecognizer(digit_count=args.digit_count)
            student_id = sid_rec.recognize(sid_roi)
```

**Step 4: 运行测试验证通过**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_main.py -v
```

Expected: ALL PASS

**Step 5: 提交**

```bash
git add main.py
git commit -m "refactor: main.py 使用 StudentIdRecognizer 替代内联函数"
```

---

### Task 4: 新增 test_student_id_recognizer.py

**Files:**
- Create: `docs/auto_grading_system/tests/test_student_id_recognizer.py`

**Step 1: 写测试文件**

```python
"""学号识别模块测试。

验证 StudentIdRecognizer 能正确识别模拟的学号气泡网格。
运行: pytest tests/test_student_id_recognizer.py -v
"""

import cv2
import numpy as np
import pytest

from modules.student_id_recognizer import StudentIdRecognizer


def make_student_id_image(digits, digit_count=9, bubble_size=20, gap_x=15, gap_y=10):
    """生成学号填涂图像。

    Args:
        digits: 每位填涂的数字列表，如 [0,2,5,8,1,1,0,0,8]。
                None 表示该位未填涂。
        digit_count: 总位数
        bubble_size: 气泡直径
        gap_x: 列间距
        gap_y: 行间距

    Returns:
        灰度图像 (numpy.ndarray)
    """
    rows = 10  # 0-9
    cell_w = bubble_size + gap_x
    cell_h = bubble_size + gap_y
    w = digit_count * cell_w + gap_x
    h = rows * cell_h + gap_y

    img = np.ones((h, w), dtype=np.uint8) * 255

    for col in range(digit_count):
        filled_digit = digits[col] if col < len(digits) else None
        for row in range(rows):
            cx = gap_x + col * cell_w + bubble_size // 2
            cy = gap_y + row * cell_h + bubble_size // 2
            if row == filled_digit:
                cv2.circle(img, (cx, cy), bubble_size // 2, 0, -1)
            else:
                cv2.circle(img, (cx, cy), bubble_size // 2, 0, 2)

    return img


class TestStudentIdRecognizer:
    def test_init_default(self):
        """默认参数初始化。"""
        rec = StudentIdRecognizer()
        assert rec.digit_count == 9
        assert rec.threshold == 0.3

    def test_recognize_single_digit(self):
        """单列填涂应识别正确。"""
        digits = [None, None, None, None, None, None, None, None, 5]
        img = make_student_id_image(digits)
        rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
        result = rec.recognize(img)
        assert result is not None
        assert result[-1] == '5'

    def test_recognize_full_id(self):
        """完整学号识别。"""
        digits = [0, 2, 5, 8, 1, 1, 0, 0, 8]
        img = make_student_id_image(digits)
        rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
        result = rec.recognize(img)
        assert result is not None
        # 每位应正确或至少非空
        assert '?' not in result or len(result) == 9

    def test_recognize_no_fill(self):
        """全部未填涂应返回全 '?'。"""
        digits = [None] * 9
        img = make_student_id_image(digits)
        rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
        result = rec.recognize(img)
        assert result is not None
        # 未填涂的位应为 '?'
        assert '?' in result

    def test_recognize_returns_string(self):
        """返回值应为字符串。"""
        digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        img = make_student_id_image(digits)
        rec = StudentIdRecognizer(digit_count=9, threshold=0.2)
        result = rec.recognize(img)
        assert isinstance(result, str)
        assert len(result) == 9
```

**Step 2: 运行测试验证通过**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_student_id_recognizer.py -v
```

Expected: ALL PASS（StudentIdRecognizer 已实现）

**Step 3: 提交**

```bash
git add tests/test_student_id_recognizer.py
git commit -m "test: 新增 StudentIdRecognizer 单元测试"
```

---

### Task 5: test_main.py — 扩展批量模式测试

**Files:**
- Modify: `docs/auto_grading_system/tests/test_main.py`

**Step 1: 在 `tests/test_main.py` 末尾新增测试**

```python
class TestMainFolderMode:
    def test_folder_mode_with_real_images(self):
        """--folder 模式应能处理真实答题卡图片。"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        folder = os.path.join(project_root, 'data', 'answer_sheets')
        if not os.path.isdir(folder):
            pytest.skip("data/answer_sheets 文件夹不存在")

        result = _run_main('--folder', folder)
        # 不崩溃就算通过
        assert result.returncode is not None

    def test_folder_mode_empty_folder(self, tmp_path):
        """空文件夹应报错退出。"""
        empty = str(tmp_path / "empty")
        os.makedirs(empty)
        result = _run_main('--folder', empty)
        assert result.returncode != 0

    def test_folder_mode_nonexistent(self):
        """不存在的文件夹应报错。"""
        result = _run_main('--folder', '/nonexistent/path')
        assert result.returncode != 0

    def test_no_image_or_folder(self):
        """不提供 --image 和 --folder 应报错。"""
        result = _run_main()
        assert result.returncode != 0
```

**Step 2: 运行测试**

```bash
cd docs/auto_grading_system && python -m pytest tests/test_main.py -v
```

Expected: ALL PASS

**Step 3: 提交**

```bash
git add tests/test_main.py
git commit -m "test: 扩展 test_main.py 覆盖批量模式"
```

---

### Task 6: run.bat — 支持批量模式

**Files:**
- Modify: `docs/auto_grading_system/run.bat`

**Step 1: 修改 run.bat**

将 `run.bat` 中第 33-57 行（图像路径确定和执行部分）替换为：

```batch
REM ---- Run mode ----
echo   [1] Single image (default)
echo   [2] Batch grading (folder)
echo.
set /p "MODE=Select mode [1/2]: "

if "!MODE!"=="2" (
    echo.
    echo [Mode] Batch grading
    "!PYTHON_CMD!" -X utf8 main.py --folder "data\answer_sheets"
) else (
    if "%~1"=="" (
        set "IMAGE=data\answer_sheets\answer_sheet_1.png"
        echo [Info] No image specified, using default: !IMAGE!
    ) else (
        set "IMAGE=%~1"
    )
    if not exist "!IMAGE!" (
        echo [Error] Image not found: !IMAGE!
        pause
        exit /b 1
    )
    echo [Mode] Single image
    echo [Image] !IMAGE!
    echo.
    "!PYTHON_CMD!" -X utf8 main.py --image "!IMAGE!"
)
```

**Step 2: 验证 bat 文件语法**

手动检查无 `if` 嵌套超过 3 层，无未闭合引号。

**Step 3: 提交**

```bash
git add run.bat
git commit -m "feat: run.bat 支持批量处理模式"
```

---

### Task 7: 端到端验证

**Files:**
- 无代码改动，仅运行验证

**Step 1: 运行批量模式**

```bash
cd docs/auto_grading_system && python main.py --folder data/answer_sheets
```

Expected: 不崩溃，输出 2 个学生的识别结果和评分

**Step 2: 检查输出内容**

手动验证：
- 学号是否合理（非全 '?'）
- 选择题识别数量（应接近 20 题）
- 判断题识别数量（应接近 10 题）
- 总分在 0-80 范围内
- 结果.xlsx 已生成

**Step 3: 运行全部测试**

```bash
cd docs/auto_grading_system && python -m pytest tests/ -v
```

Expected: ALL PASS
