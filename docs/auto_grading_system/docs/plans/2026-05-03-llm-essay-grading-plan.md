# LLM 简答题自动评分实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 `LLMEssayGrader` 类，通过 ModelScope API 调用 LLM 对 OCR 识别的简答题答案进行语义评分。

**Architecture:** 新增 `modules/llm_essay_grader.py`，实现 `EssayGraderBase` 子类。ModelScope API 以 OpenAI 兼容格式调用。Streamlit 侧边栏新增 API 配置区域，配置缓存到 `config/llm_config.json`。

**Tech Stack:** Python, requests, ModelScope API (OpenAI 兼容), Streamlit, pytest

---

### Task 1: LLMEssayGrader — 核心类与返回解析

**Files:**
- Create: `modules/llm_essay_grader.py`
- Create: `tests/test_llm_essay_grader.py`
- Modify: `modules/__init__.py`

**Step 1: 写解析逻辑的失败测试**

```python
# tests/test_llm_essay_grader.py
import pytest
from modules.llm_essay_grader import LLMEssayGrader


class TestParseResponse:
    def test_valid_response(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "得分：15\n反馈：基本正确，但表述不够完整"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 15
        assert "基本正确" in feedback

    def test_full_score(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "得分：20\n反馈：完全正确"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 20
        assert "完全正确" in feedback

    def test_zero_score(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "得分：0\n反馈：答案错误"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 0

    def test_score_exceeds_max_clamped(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "得分：30\n反馈：超出满分"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 20

    def test_malformed_response_returns_zero(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "这个问题不太确定怎么评分"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 0
        assert "人工" in feedback or "异常" in feedback

    def test_empty_response(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        score, feedback = grader._parse_response("", max_score=20)
        assert score == 0

    def test_response_with_extra_text(self):
        grader = LLMEssayGrader(api_key="test", base_url="http://test",
                                model="test-model")
        text = "好的，让我来评估。\n\n得分：10\n反馈：部分正确\n\n希望这有帮助。"
        score, feedback = grader._parse_response(text, max_score=20)
        assert score == 10


class TestInit:
    def test_stores_params(self):
        grader = LLMEssayGrader(api_key="sk-123", base_url="http://api.test",
                                model="deepseek-v4")
        assert grader.api_key == "sk-123"
        assert grader.base_url == "http://api.test"
        assert grader.model == "deepseek-v4"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_llm_essay_grader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'modules.llm_essay_grader'`

**Step 3: 实现 LLMEssayGrader 核心类**

```python
# modules/llm_essay_grader.py
import re
import requests

from modules.grading import EssayGraderBase


class LLMEssayGrader(EssayGraderBase):
    """通过 LLM API 对简答题进行语义评分。

    调用 ModelScope OpenAI 兼容格式的 API，将参考答案和学生答案
    发给 LLM 判断得分。
    """

    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _build_prompt(self, question, reference, student_answer, max_score):
        return (
            "你是一个阅卷助手。请根据参考答案评估学生答案。\n\n"
            "注意事项：\n"
            "- 学生答案是通过 OCR 从手写文字识别的，可能存在识别错误"
            "（形近字、同音字）\n"
            "- 请根据语义判断，容忍合理的 OCR 识别偏差\n"
            "- 如果答案明显不确定或 OCR 识别质量差，请在反馈中说明\n\n"
            f"参考答案：{reference}\n"
            f"学生答案：{student_answer}\n"
            f"满分：{max_score}分\n\n"
            "请严格按以下格式返回（不要输出其他内容）：\n"
            "得分：X\n"
            "反馈：一句话评语"
        )

    def _call_api(self, messages):
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 256,
            "temperature": 0.3,
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "")
        return ""

    def _parse_response(self, text, max_score):
        score_match = re.search(r"得分[：:]\s*(\d+)", text)
        feedback_match = re.search(r"反馈[：:]\s*(.+)", text)

        if not score_match:
            return 0, "LLM 返回格式异常，需人工复核"

        score = int(score_match.group(1))
        score = min(score, max_score)
        feedback = feedback_match.group(1).strip() if feedback_match else "LLM 评分完成"
        return score, feedback

    def score(self, question, reference, student_answer, max_score):
        if not student_answer or not student_answer.strip():
            return 0, max_score, "未作答"

        prompt = self._build_prompt(question, reference, student_answer,
                                    max_score)
        messages = [{"role": "user", "content": prompt}]

        try:
            text = self._call_api(messages)
            score, feedback = self._parse_response(text, max_score)
            return score, max_score, feedback
        except Exception as e:
            return 0, max_score, f"LLM 调用失败: {e}"
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_llm_essay_grader.py -v`
Expected: 全部 PASS

**Step 5: 更新 `modules/__init__.py`**

在 `modules/__init__.py` 末尾添加导出：

```python
from .llm_essay_grader import LLMEssayGrader
```

**Step 6: 提交**

```bash
git add modules/llm_essay_grader.py tests/test_llm_essay_grader.py modules/__init__.py
git commit -m "feat: 新增 LLMEssayGrader 核心类与返回解析"
```

---

### Task 2: 配置文件加载与保存

**Files:**
- Modify: `modules/llm_essay_grader.py`
- Add tests to: `tests/test_llm_essay_grader.py`

**Step 1: 写配置相关失败测试**

在 `tests/test_llm_essay_grader.py` 末尾追加：

```python
import json
import os
import tempfile


class TestConfigLoadSave:
    def test_save_and_load(self, tmp_path):
        from modules.llm_essay_grader import save_config, load_config
        config = {
            "api_key": "sk-test-123",
            "base_url": "https://api-inference.modelscope.cn",
            "model": "deepseek-ai/DeepSeek-V4-Pro-Base",
        }
        config_path = str(tmp_path / "llm_config.json")
        save_config(config, config_path)
        loaded = load_config(config_path)
        assert loaded["api_key"] == "sk-test-123"
        assert loaded["base_url"] == "https://api-inference.modelscope.cn"
        assert loaded["model"] == "deepseek-ai/DeepSeek-V4-Pro-Base"

    def test_load_missing_file_returns_defaults(self, tmp_path):
        from modules.llm_essay_grader import load_config
        config_path = str(tmp_path / "nonexistent.json")
        loaded = load_config(config_path)
        assert loaded["api_key"] == ""
        assert "base_url" in loaded

    def test_from_config_creates_grader(self, tmp_path):
        from modules.llm_essay_grader import save_config, LLMEssayGrader
        config = {
            "api_key": "sk-abc",
            "base_url": "http://localhost:8080",
            "model": "test-model",
        }
        config_path = str(tmp_path / "llm_config.json")
        save_config(config, config_path)
        grader = LLMEssayGrader.from_config(config_path)
        assert grader.api_key == "sk-abc"
        assert grader.model == "test-model"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_llm_essay_grader.py::TestConfigLoadSave -v`
Expected: FAIL — `ImportError: cannot import name 'save_config'`

**Step 3: 在 `modules/llm_essay_grader.py` 中实现配置函数**

在文件顶部（`class LLMEssayGrader` 之前）添加：

```python
import json
import os


def load_config(config_path):
    if not os.path.exists(config_path):
        return {
            "api_key": "",
            "base_url": "https://api-inference.modelscope.cn",
            "model": "deepseek-ai/DeepSeek-V4-Pro-Base",
        }
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config, config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
```

在 `LLMEssayGrader` 类中添加类方法：

```python
@classmethod
def from_config(cls, config_path):
    config = load_config(config_path)
    return cls(
        api_key=config.get("api_key", ""),
        base_url=config.get("base_url", "https://api-inference.modelscope.cn"),
        model=config.get("model", "deepseek-ai/DeepSeek-V4-Pro-Base"),
    )
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_llm_essay_grader.py -v`
Expected: 全部 PASS

**Step 5: 提交**

```bash
git add modules/llm_essay_grader.py tests/test_llm_essay_grader.py
git commit -m "feat: LLMEssayGrader 配置文件加载/保存"
```

---

### Task 3: Streamlit 侧边栏 LLM 配置 UI

**Files:**
- Modify: `app.py:1-25` (imports)
- Modify: `app.py:140-164` (sidebar)

**Step 1: 在 app.py 顶部添加导入**

在 `app.py` 的 import 区域（约第 21-23 行之间）添加：

```python
from modules.llm_essay_grader import LLMEssayGrader, load_config, save_config
```

**Step 2: 在侧边栏添加 LLM 配置区域**

在 `app.py` 的 `with st.sidebar:` 块中，在 `st.header("参考答案")` 之前插入：

```python
    st.divider()
    st.header("LLM 评分设置")
    LLM_CONFIG_PATH = os.path.join(BASE_DIR, "config", "llm_config.json")
    _llm_cfg = load_config(LLLM_CONFIG_PATH)
    llm_api_key = st.text_input(
        "API Key", value=_llm_cfg.get("api_key", ""), type="password",
        help="ModelScope API Key")
    llm_base_url = st.text_input(
        "Base URL",
        value=_llm_cfg.get("base_url", "https://api-inference.modelscope.cn"),
        help="API 端点地址")
    llm_model = st.text_input(
        "模型", value=_llm_cfg.get("model", "deepseek-ai/DeepSeek-V4-Pro-Base"),
        help="模型 ID")
    if st.button("保存 LLM 配置"):
        save_config({"api_key": llm_api_key, "base_url": llm_base_url,
                      "model": llm_model}, LLM_CONFIG_PATH)
        st.success("配置已保存")
    llm_enabled = bool(llm_api_key and llm_api_key.strip())
    if llm_enabled:
        st.success("LLM 评分已启用")
    else:
        st.info("未配置 API Key，简答题将标记为需手动评分")
```

**Step 3: 提交**

```bash
git add app.py
git commit -m "feat(app): 侧边栏 LLM 评分配置 UI"
```

---

### Task 4: 将 LLMEssayGrader 集成到评分流程

**Files:**
- Modify: `app.py:47-53` (单套模式 `_load_grading_service` 或评分步骤)
- Modify: `app.py:608-636` (单套评分步骤)
- Modify: `app.py:673-676` (批量模式)

**Step 1: 修改单套模式评分步骤**

在 `app.py` 的 `Step 6 评分` 部分（约第 609 行），将 `svc = _load_grading_service()` 替换为：

```python
                essay_grader = None
                if llm_enabled:
                    essay_grader = LLMEssayGrader(
                        api_key=llm_api_key,
                        base_url=llm_base_url,
                        model=llm_model,
                    )
```

然后修改 `_load_grading_service` 调用方式——在第 609 行附近，改为：

```python
                svc = _load_grading_service()
                if svc and essay_grader:
                    svc.essay_grader = essay_grader
```

**Step 2: 修改批量模式评分**

在 `app.py` 的批量模式中（约第 673 行 `svc = _load_grading_service()` 之后），添加：

```python
                if svc and llm_enabled:
                    svc.essay_grader = LLMEssayGrader(
                        api_key=llm_api_key,
                        base_url=llm_base_url,
                        model=llm_model,
                    )
```

**Step 3: 手动验证**

在 Streamlit 中上传答题卡，确认：
- 无 API Key 时：简答题显示 "需手动评分"（原有行为）
- 有 API Key 时：简答题显示 LLM 返回的得分和反馈

**Step 4: 提交**

```bash
git add app.py
git commit -m "feat(app): 集成 LLMEssayGrader 到评分流程"
```

---

### Task 5: 更新 requirements.txt

**Files:**
- Modify: `requirements.txt`

**Step 1: 添加 requests 依赖**

在 `requirements.txt` 末尾添加：

```
requests>=2.28
```

**Step 2: 提交**

```bash
git add requirements.txt
git commit -m "feat: 添加 requests 依赖"
```

---

### Task 6: 全量测试与最终提交

**Step 1: 运行全部测试**

Run: `pytest tests/ -v`
Expected: 全部 PASS（87 + 新增 ≈ 95+）

**Step 2: 推送到 GitHub**

```bash
git push origin main
```
