# LLM 简答题自动评分设计

## 背景

当前系统中简答题评分是空壳：`DefaultEssayGrader.score()` 始终返回 0 分，标注"需手动评分"。
OCR 部分（`EssayRecognizer` + PaddleOCR）已可用，返回识别文字。

目标：接入 LLM 对 OCR 识别结果进行语义评分，替换手动评分。

## 架构

```
答题卡图像
  → 版面分析（已实现）→ 简答题区域裁剪
  → PaddleOCR（已实现）→ 文字字符串
  → LLMEssayGrader（新增）→ ModelScope API → 得分 + 反馈
```

## 新增文件

### `modules/llm_essay_grader.py`

```python
class LLMEssayGrader(EssayGraderBase):
    def __init__(self, api_key, base_url, model):
        ...

    def score(self, question, reference, student_answer, max_score):
        # 构建 prompt → 调用 API → 解析返回
        ...

    def _call_api(self, messages):
        # ModelScope OpenAI 兼容格式调用
        # POST {base_url}/v1/chat/completions
        # Authorization: Bearer {api_key}
        ...
```

**Prompt 设计**（宽容模式）：

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

**返回解析**：
- 正则提取 `得分：(\d+)` 获取分数
- 正则提取 `反馈：(.+)` 获取评语
- 解析失败时回退：得分 0，反馈 "LLM 返回格式异常，需人工复核"

**API 调用**（参照 Exam_v5.0 的 `call_modelscope`）：
- 端点：`{base_url}/v1/chat/completions`
- 格式：OpenAI 兼容
- 认证：`Authorization: Bearer {api_key}`
- 模型：默认 `deepseek-ai/DeepSeek-V4-Pro-Base`
- 参数：`max_tokens=256, temperature=0.3`（低温度保证评分稳定）

### `config/llm_config.json`（自动生成）

```json
{
  "api_key": "",
  "base_url": "https://api-inference.modelscope.cn",
  "model": "deepseek-ai/DeepSeek-V4-Pro-Base"
}
```

## 修改文件

### `app.py`

1. **侧边栏**：新增"LLM 评分设置"区域
   - API Key 文本框（password 类型）
   - Base URL 文本框（默认 ModelScope）
   - 模型名文本框
   - "保存配置"按钮 → 写入 `config/llm_config.json`
   - 启动时自动加载 `config/llm_config.json`

2. **评分步骤**：有 API Key 时构造 `LLMEssayGrader` 传入 `GradingService`，否则回退到 `DefaultEssayGrader`

### `modules/pipeline.py`

无需修改。`GradingService` 已支持通过 `essay_grader` 参数注入自定义评分器。

### `requirements.txt`

新增 `requests>=2.28`（用于调用 ModelScope API）。

## 测试

### `tests/test_llm_essay_grader.py`

1. `test_init` — 参数正确存储
2. `test_parse_response_valid` — 解析正常格式的 LLM 返回
3. `test_parse_response_malformed` — 解析异常格式时回退到 0 分
4. `test_score_without_api_key` — 无 API Key 时降级到 DefaultEssayGrader
5. `test_config_save_and_load` — 配置文件保存/加载

注意：不测试实际 API 调用（依赖外部服务），只测试解析逻辑和降级逻辑。
