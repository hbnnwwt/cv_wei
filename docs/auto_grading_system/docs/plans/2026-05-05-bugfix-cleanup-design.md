# Bug 修复与代码清理设计

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复 4 个崩溃级 bug + 4 个逻辑级 bug + 4 项代码质量清理，使系统在异常输入下不再中断流程。

**Architecture:** 最小改动原则——每个修复都是局部改动，不引入新依赖或新架构。崩溃级问题通过添加 guard/try-except 解决；逻辑级问题通过修正条件判断解决。

**Tech Stack:** Python, OpenCV, Streamlit

---

## Part 1: 崩溃级修复（防中断）

### B1. app.py — essay_text 为 None 时 .split() 崩溃

**位置**: `app.py:734`

**现状**: `st.text_area` 的 `height` 参数计算 `len(essay_text.split('\n')) * 30`，当 OCR 识别失败返回 `None` 时 `.split()` 抛 `AttributeError`。

**修复**: 在计算 height 前加 `essay_text = essay_text or ""` 空值保护。

**改动量**: 1 行

### B2. app.py — svc 为 None 时 .essay_max_score 崩溃

**位置**: `app.py:1058`

**现状**: 批量详情展开器中 `svc.essay_max_score` 未检查 `svc` 是否为 None。当答案键文件加载失败时 `svc` 为 None。

**修复**: 该行外层已有 `if res and svc` 的判断（line ~1020），将 line 1058 移入同一条件分支，或加 `svc.essay_max_score if svc else 0`。

**改动量**: 1 行

### B3. marker.py — page2 为 None 时 .copy() 崩溃

**位置**: `marker.py:117`

**现状**: `mark_and_save()` 的 `page2` 参数在单页模式下可能为 None（只有第一页），但函数直接 `page2.copy()` 无检查。

**修复**: 在函数入口加 guard：`if page2 is None: page2 = np.zeros((100, 100, 3), dtype=np.uint8)`，或改为仅在 page2 非 None 时处理第二页标注。

**改动量**: ~5 行

### B4. app.py — svc.grade() / mark_and_save 无 try-except

**位置**: `app.py:760, 798`

**现状**: 单次模式下 `svc.grade()` 和 `mark_and_save()` 调用无异常保护。如果评分服务或标注模块抛异常，整个 Streamlit 流程中断，之前的可视化结果全部丢失。

**修复**: 将 `svc.grade()` 和 `mark_and_save()` 调用包裹在 try-except 中，异常时 `st.error()` 显示错误但保留已有结果。

**改动量**: ~10 行

---

## Part 2: 逻辑级修复（防错误结果）

### B5. pipeline.py — 空 essay dict 的 fallback 逻辑

**位置**: `pipeline.py:41-45`

**现状**: `get_essay_questions()` 中 `answer_key.get('essay')` 返回 `{}` 时为 falsy，触发 fallback `[31]`。对于明确没有简答题的试卷，应返回空列表。

**修复**: 改为显式检查 `answer_key.get('essay') is not None and len(answer_key['essay']) > 0`，只有 essay 键不存在时才 fallback 到 `[31]`，存在但为空时返回 `[]`。

**改动量**: 2 行

### B6. grading.py — 空分数列表时 SUM 公式倒写

**位置**: `grading.py:241-246`（`save_result_xlsx` 方法）

**现状**: `choice_scores` 为空时 `get_column_letter(2 + 0 - 1)` = `'A'`，SUM 范围变成 `B:A`（倒写）。

**修复**: 写 SUM 公式前检查 `choice_scores` 和 `judge_scores` 是否非空，为空时跳过公式或写 `0`。

**改动量**: 4 行

### B7. marker.py — 文件碰撞检测只看 page1

**位置**: `marker.py:133-137`

**现状**: 循环中只检查 `p1_path` 是否存在，`p2_path` 跟着同名后缀但可能覆盖已有文件。

**修复**: 改为同时检查 `p1_path` 和 `p2_path`，任一存在即递增后缀。

**改动量**: 3 行

### B8. app.py — 奇数张图片静默丢弃

**位置**: `app.py:874`

**现状**: `pairs = len(images) // 2` 后直接处理，多余的一张图片无任何提示。

**修复**: 在 `pairs` 计算后加 `if len(images) % 2 != 0: st.warning(...)`。

**改动量**: 2 行

---

## Part 3: 代码质量清理

### C1. app.py — except NameError hack

**位置**: `app.py:788-795`

**现状**: 用 `except NameError` 掩盖 `choice_all_result` / `judge_all_result` 未定义的问题。

**修复**: 在使用前初始化 `choice_all_result = None` / `judge_all_result = None`，然后用 `if choice_all_result is not None` 替代 `try/except NameError`。

**改动量**: ~6 行

### C2. _valid_region 函数重复

**位置**: `pipeline.py:34-38` 和 `marker.py:14-17`

**修复**: 保留 `pipeline.py` 中的定义，`marker.py` 改为 `from modules.pipeline import _valid_region`。但 `_valid_region` 是私有函数（下划线前缀），更规范的做法是将其提升为 `pipeline.py` 的公开函数（去掉下划线），或放到 `defaults.py` 中。

**改动量**: 3 行

### C3. pipeline.py — essay_questions 死参数

**位置**: `pipeline.py:105-106`

**修复**: 删除 `recognize_essay()` 的 `essay_questions` 参数（函数内未使用）。

**改动量**: 1 行

### C4. README 硬编码表状态更新

**修复**: 将已实际修复的 H 条目（H89, H58, H60, H36, H37, H106, H110, H84, H30, H15, H16, H19, H34）移入"已修复硬编码"表或标记为已完成。将唯一残留的 H107（正则与提示词耦合）标注为待修复。

**改动量**: 文档更新

---

## 文件清单

| 文件 | 修复项 |
|------|--------|
| `app.py` | B1, B2, B4, B8, C1 |
| `modules/marker.py` | B3, B7, C2 |
| `modules/pipeline.py` | B5, C2, C3 |
| `modules/grading.py` | B6 |
| `README.md` | C4 |

## 验证

1. 上传只有第一页的答题卡 → 不崩溃（B3, B4）
2. 上传奇数张图片到批量模式 → 显示警告（B8）
3. 使用无简答题的答案键 → 不出现第 31 题条目（B5）
4. 答案键加载失败 → 界面显示错误但不崩溃（B2, B4）
5. OCR 识别返回 None → 不崩溃（B1）
