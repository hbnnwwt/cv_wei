# 智能阅卷系统 — 参考答案版本完善设计

日期: 2026-04-24

## 背景

项目已具备完整的模块实现和 Streamlit GUI，但存在以下差距需要修复以达到参考答案标准：
- main.py 与已有模块不一致
- 缺少部分测试覆盖
- 简答题评分逻辑未集成
- 真实图片端到端验证缺失

## 修复清单

### 1. main.py 使用 StudentIdRecognizer

**问题**: main.py 内联了 `extract_student_id()` 函数，与 `modules/student_id_recognizer.py` 重复。

**方案**: 删除内联函数，改为导入 `StudentIdRecognizer`。

**改动**:
- 删除 `extract_student_id()` 函数
- 导入 `from modules.student_id_recognizer import StudentIdRecognizer`
- `process_student()` 中使用 `StudentIdRecognizer` 实例

### 2. grading.py 集成简答题评分

**问题**: `grade()` 方法返回的 `total` 只包含选择题 + 判断题，简答题得分为 0。

**方案**:
- 新增 `EssayGraderBase` 抽象基类，定义 `score(question_text, reference_answer, student_answer) -> (score, max_score, feedback)` 接口
- 新增 `DefaultEssayGrader` 返回 (0, max_score, "手动评分") 作为默认实现
- `GradingService.__init__` 接受可选的 `essay_grader` 参数
- `grade()` 方法调用 essay_grader 计算简答题得分并加入 total

**接口设计**:
```python
class EssayGraderBase:
    def score(self, question, reference, student_answer, max_score):
        raise NotImplementedError

class DefaultEssayGrader(EssayGraderBase):
    """默认实现：返回 0 分，标注需手动评分"""
    def score(self, question, reference, student_answer, max_score):
        return 0, max_score, "需手动评分"
```

### 3. run.bat 支持批量模式

**问题**: `run.bat` 只支持 `--image` 单图模式。

**方案**: 添加菜单选项，用户可选择单图或批量处理。

**改动**: 运行时询问用户选择模式，批量模式默认使用 `data/answer_sheets` 文件夹。

### 4. 新增 test_student_id_recognizer.py

**问题**: `StudentIdRecognizer` 模块无测试。

**方案**: 参照 `test_choice_recognizer.py` 的模式，用合成图像测试：
- 生成模拟学号填涂图像（9列×10行气泡网格）
- 测试填涂特定数字后的识别结果
- 测试未填涂、部分填涂等边界情况
- 测试不同 digit_count 参数

### 5. 扩展 test_main.py 覆盖批量模式

**问题**: 现有测试不覆盖 `--folder` 参数。

**方案**: 新增测试用例：
- `test_folder_mode_with_real_images`: 使用 `data/answer_sheets/` 运行批量模式
- `test_folder_mode_empty_folder`: 空文件夹报错
- `test_folder_mode_odd_count`: 奇数文件数警告但不崩溃

### 6. 更新 __init__.py

**问题**: 只导出 `ImagePreprocessor` 和 `LayoutAnalyzer`。

**方案**: 导出全部 6 个模块（作为参考答案版本）。

### 7. 端到端验证

**问题**: 真实答题卡图片的识别准确率未验证。

**方案**: 实现上述修复后，使用 4 张真实答题卡图片运行完整流程，检查：
- 学号是否正确识别
- 选择题答案是否合理
- 判断题答案是否合理
- 评分结果是否正确
- XLSX 输出是否正常

## 不做的事

- 不实现 LLM 评分的具体调用（只预留接口）
- 不改动 `app.py`（已正确使用 StudentIdRecognizer）
- 不改动 preprocess.py 和 layout.py（已提供的模块）

## 文件改动范围

| 文件 | 操作 |
|------|------|
| `main.py` | 修改：使用 StudentIdRecognizer |
| `modules/grading.py` | 修改：新增 EssayGraderBase 接口 |
| `modules/__init__.py` | 修改：导出全部模块 |
| `run.bat` | 修改：添加批量模式 |
| `tests/test_student_id_recognizer.py` | 新增 |
| `tests/test_main.py` | 修改：添加批量模式测试 |
