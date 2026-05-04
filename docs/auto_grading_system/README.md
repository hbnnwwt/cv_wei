# 智能阅卷系统

基于计算机视觉的答题卡自动识别与评分系统。支持选择题（1-20题）、判断题（21-30题）、简答题（31题）的自动识别与评分。

## 功能特性

- **学号识别**：基于气泡填涂检测，自动识别学号
- **选择题识别**：连通域分析 + 像素密度法，检测 A/B/C/D 填涂
- **判断题识别**：同上方法，检测 T/F 填涂
- **简答题识别**：支持 4 种 OCR 引擎
  - PaddleOCR（默认，手写体效果最佳）
  - RapidOCR（ONNX 推理，无需 GPU）
  - EasyOCR（对比用，手写效果较差）
  - Online（Qwen3-VL 视觉模型，通过 ModelScope API 调用）
- **LLM 自动评分**：可选用 Qwen3-235B 对简答题进行自动评分并给出反馈
- **错题标注**：在答题卡图片上用红色 × 标记错题位置，标注各部分得分
- **批量导出**：支持一键导出评分结果为 xlsx 文件

## 项目结构

```
auto_grading_system/
├── app.py                         # Streamlit Web GUI
├── main.py                        # CLI 入口
├── requirements.txt               # Python 依赖
├── run_gui.bat                    # 启动 GUI
├── run.bat                        # 启动 CLI
├── setup.bat                      # 首次环境配置
├── 参考答案.xlsx                   # 参考答案
├── 答题卡 - A4打印模板.pdf          # 答题卡打印模板
│
├── modules/                       # 核心模块
│   ├── preprocess.py              # 图像预处理（去噪、二值化、旋转校正）
│   ├── layout.py                  # 版面分析（检测答题区域）
│   ├── choice_recognizer.py       # 选择题识别
│   ├── judge_recognizer.py        # 判断题识别
│   ├── essay_recognizer.py        # 简答题 OCR（多引擎）
│   ├── student_id_recognizer.py   # 学号识别
│   ├── grading.py                 # 评分服务
│   ├── llm_essay_grader.py        # LLM 简答题评分
│   ├── marker.py                  # 错题标注与得分写入
│   └── pipeline.py                # 识别管线编排
│
├── config/                        # 配置
│   ├── model_config.json          # 模型配置（Base URL、模型名称，可入库）
│   └── api_keys.json              # API 密钥（敏感，不入库）
│
├── data/                          # 数据目录
│   ├── answer_sheets/             # 样例答题卡图片
│   ├── output/                    # 识别输出
│   └── processed/                 # 标注后的答题卡图片
│
└── tests/                         # 测试用例
```

## 快速开始

### 1. 环境配置

双击 `setup.bat`，自动安装 Python 依赖（使用清华镜像源）。

### 2. 启动 GUI（推荐）

```
run_gui.bat
```

浏览器打开 `http://localhost:8501`，按以下步骤操作：

1. **上传答题卡**：分别上传第1页（学号+选择题）和第2页（判断题+简答题）
2. **预览识别**：逐步查看预处理、版面分析、学号识别、选择题/判断题识别、OCR 结果
3. **查看评分**：系统自动与参考答案对比，显示得分
4. **导出结果**：下载 xlsx 评分文件

### 3. 启动 CLI

```
run.bat
```

交互式菜单，支持单张识别和批量处理。

### 4. 运行测试

```
run_tests.bat        # Windows
bash run_tests.sh    # Linux/macOS
```

## 识别流程

```
原始图片 → 预处理（去噪/二值化/旋转校正）
         → 版面分析（检测学号/选择题/判断题/简答题区域）
         → 学号识别（气泡填涂检测）
         → 选择题识别（1-20题，像素密度法）
         → 判断题识别（21-30题，像素密度法）
         → 简答题 OCR（31题，PaddleOCR/在线模型）
         → 评分（与参考答案对比 + LLM 简答题评分）
         → 标注输出（红色×标记错题 + 得分写入图片）
```

## 环境要求

- Python 3.10+
- Windows / Linux / macOS
- GPU 可选（PaddleOCR 支持加速，但非必需）

## 依赖

```
opencv-python>=4.5
numpy>=1.21,<2.5
openpyxl>=3.0
paddleocr==2.10.0
paddlepaddle==2.6.2
scipy>=1.7
rapidocr-onnxruntime>=1.3
easyocr>=1.7
streamlit>=1.30
requests>=2.28
```

## 待做清单

### 高优先级

| 编号 | 文件 | 问题 | 说明 |
|------|------|------|------|
| P1 | `choice_recognizer.py` / `judge_recognizer.py` | **未检测多选情况** | 多个气泡超过阈值时只取密度最高的一个返回，应检测多选并返回 `None`（判 0 分）。空白未填涂已正确处理（返回 `None` → 0 分） |
| P2 | `main.py` | 缺少 LLM 评分、错题标注、配置加载、OCR 引擎选择 | CLI 版本严重落后于 GUI，缺少 `LLMEssayGrader`、`marker.mark_and_save`、`config` 加载、OCR 引擎选择功能 |
| P3 | `main.py` / `pipeline.py` | CLI 默认阈值 0.5，GUI 使用 0.06 | `main.py` 调用 `recognize_choices/judges` 时未传 `threshold`，使用 `pipeline.py` 默认值 0.5，导致几乎无法识别填涂气泡 |
| P4 | `README.md` | ~~引用不存在的 `config/llm_config.json`~~ | 已修复：更新为 `model_config.json` + `api_keys.json` |
| P5 | `essay_recognizer.py:10` | 无条件 `import torch`，未安装 torch 时崩溃 | 应像 `paddleocr` 一样用 `try/except` 包装 |
| P6 | `essay_recognizer.py:211-215` | `recognize()` 吞掉所有异常，返回空字符串 | 调用方无法区分"无文字"和"引擎崩溃"，应返回结构化结果 |

### 中优先级

| 编号 | 文件 | 问题 | 说明 |
|------|------|------|------|
| P7 | `llm_essay_grader.py:111-112` | API 失败时静默评 0 分 | 暂时性错误（超时、限流）导致学生得 0 分，应加重试或"不确定"状态 |
| P8 | `pipeline.py:22-69` | 未验证 `regions` 字典格式/类型 | `regions['student_id']` 若非 4 元组会抛 `TypeError`，应加 `isinstance` 检查 |
| P9 | `marker.py:37,95,105,113` | 未验证 `region` 是否为 4 元组 | 解包前缺少格式校验，异常 region 会崩溃 |
| P10 | `grading.py:93,102` | 题目范围硬编码 1-20、21-30 | 应从答案键动态获取范围，否则增减题目数会出错 |
| P11 | `student_id_recognizer.py:86-88` | "第三大轮廓"启发式检测脆弱 | 扫描噪声、印章等可导致选错区域，已有 `xfail` 测试承认此问题 |
| P12 | `tests/` | 缺少 `test_pipeline.py` 和 `test_marker.py` | pipeline 是核心编排层，marker 负责输出，两者无测试覆盖 |
| P13 | `grading.py:95-97` | `None == None` 可能误判满分 | 未答题且答案键缺条目时 `given == correct` 为 `True`，应显式检查 |
| P14 | `main.py:124` | `save_result_xlsx(output_path, output_path, ...)` | 模板路径和输出路径相同，文件不存在时崩溃 |
| P15 | `config/api_keys.json` | 真实 API Key 可能入库 | `.gitignore` 已排除，但应确认历史中无泄露，并提供 `.example` 模板 |

### 低优先级

| 编号 | 文件 | 问题 | 说明 |
|------|------|------|------|
| P16 | `main.py:63-74` | 无 `--threshold` CLI 参数 | 应添加与 GUI slider 等价的命令行参数 |
| P17 | `app.py:560-561` | 重复注释行 | `# ── 4b: 选择题识别 ──` 出现两次，删除多余行 |
| P18 | `essay_recognizer.py:164-166` | MIME 类型不匹配 | PNG 编码但 `data:image/jpeg` 前缀，应统一 |
| P19 | `pipeline.py:72-99` | `process_student_pair` 未被使用 | 与 `main.py` 的 `process_student` 重复，应统一 |
| P20 | `main.py:128-159` | `single_process` 未使用 pipeline 函数 | 直接调底层模块，与 `batch_process` 路径不一致 |
| P21 | `test_essay_recognizer.py` | 缺少 online OCR 引擎测试 | 4 种引擎中 online 路径无测试覆盖 |
