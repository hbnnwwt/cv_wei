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
| P1 | `choice_recognizer.py` / `judge_recognizer.py` | **未检测多选情况** | 多个气泡超过阈值时只取密度最高的一个返回，应检测多选并返回 `None`（判 0 分）。空白未填涂已正确处理（返回 `None` → 0 分）。需实际答题卡数据验证 |

### 新发现的边界情况

| 编号 | 优先级 | 文件 | 问题 | 说明 |
|------|--------|------|------|------|
| P22 | 高 | `app.py:837` | 批量处理静默限制 50 对学生 | `min(..., 50)` 丢弃第 51 对及之后的学生，无警告 |
| P23 | 中 | `app.py` / `main.py` | CLI 和 GUI 的图片格式列表不一致 | GUI 不支持 `.tiff`/`.tif`，CLI 支持 |
| P24 | 中 | `app.py:410` | 并发 GUI 会话互相覆盖临时文件 | 多用户同时使用会覆盖 `tmp_*.png` |
| P25 | 中 | `marker.py:125` | 重复学号导致标注图被静默覆盖 | 未填学号的学生都会产生 `??????????_page1_marked.png` |
| P26 | 高 | `main.py:140` | `参考答案.xlsx` 缺失时崩溃 | CLI 无 `os.path.exists` 检查 |
| P27 | 中 | `grading.py:69` | `from_xlsx` 遇到非数字列标题崩溃 | `int(q_num)` 无 try/except |
| P28 | 中 | `preprocess.py` | 过暗/过亮扫描无质量警告 | OTSU 可能产生全黑/全白二值图，识别出垃圾结果 |
| P29 | 低 | `preprocess.py` | 大图像（4000x6000）无内存保护 | 约 70MB 副本/张，无预检查 |
| P30 | 低 | `preprocess.py:49-67` | 极端旋转（>45°）方向判断失败 | 密度比较假设内容大致直立 |
| P31 | 低 | `choice/judge_recognizer.py` | 咖啡渍或笔迹导致误报 | 大面积污渍通过 OTSU + 开运算，无合理性检查 |
| P32 | 低 | `student_id_recognizer.py:190` | 学号数字全部填满无歧义警告 | 不检查最佳/次佳填充率差距 |
| P33 | 中 | `app.py` / `main.py` | 批处理无崩溃恢复 | 第 40/50 个学生崩溃时，前 39 个结果丢失 |
| P34 | 低 | `llm_essay_grader.py:89` | LLM 分数解析只匹配整数 | `(\d+)` 截断小数分数（如 15.5 → 15） |
| P35 | 低 | `app.py` | 单次模式不清理临时文件 | 旧 `tmp_*.png` 可能被重命名为新学生文件 |
| P36 | 低 | `essay_recognizer.py` | 在线 OCR 无批量取消机制 | 50 人 × 120s 超时 = 最长 100 分钟 |

---

## 已修复清单

### 高优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P2 | `main.py` | 缺少 LLM 评分、错题标注、配置加载、OCR 引擎选择 | 补齐 `--llm`、`--ocr-engine`、`--threshold`、`--no-mark`、配置加载、错题标注 |
| P3 | `main.py` / `pipeline.py` | CLI 默认阈值 0.5，GUI 使用 0.06 | `--threshold` 默认 0.06，与 GUI 一致 |
| P4 | `README.md` | 引用不存在的 `config/llm_config.json` | 更新为 `model_config.json` + `api_keys.json` |
| P5 | `essay_recognizer.py:10` | 无条件 `import torch`，未安装 torch 时崩溃 | 用 `try/except` 包装 |
| P6 | `essay_recognizer.py:211-215` | `recognize()` 吞掉所有异常，返回空字符串 | 区分 `ImportError`/`OSError`/`ValueError` 与一般异常，记录 `last_error` |

### 中优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P7 | `llm_essay_grader.py` | API 失败时静默评 0 分 | 添加最多 2 次重试，退避间隔递增 |
| P8 | `pipeline.py` | 未验证 `regions` 字典格式/类型 | 添加 `_valid_region()` 校验 |
| P9 | `marker.py` | 未验证 `region` 是否为 4 元组 | 添加 `_valid_region()` 校验 |
| P10 | `grading.py` | 题目范围硬编码 1-20、21-30 | 从答案键动态获取题目范围 |
| P11 | `student_id_recognizer.py` | "第三大轮廓"启发式检测脆弱 | 增加宽高比（0.5~5.0）和面积占比（>10%）校验 |
| P12 | `tests/` | 缺少 `test_pipeline.py` 和 `test_marker.py` | 创建 29 个测试用例覆盖两个模块 |
| P13 | `grading.py` | `None == None` 可能误判满分 | `given is None` 时分数直接为 0 |
| P14 | `main.py` | `save_result_xlsx(output_path, output_path, ...)` | 重写为从头创建工作簿，不再依赖模板文件 |
| P15 | `config/api_keys.json` | 真实 API Key 可能入库 | 确认历史无泄露，创建 `.example` 模板 |

### 低优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P16 | `main.py` | 无 `--threshold` CLI 参数 | 添加 `--threshold` 参数，默认 0.06 |
| P17 | `app.py` | 重复注释行 | 删除多余行 |
| P18 | `essay_recognizer.py` | MIME 类型不匹配 | 改为 `data:image/png` |
| P19 | `pipeline.py` | `process_student_pair` 未被使用 | main.py 统一使用 pipeline 函数 |
| P20 | `main.py` | `single_process` 未使用 pipeline 函数 | 重写后统一使用 `preprocess_and_analyze` |
| P21 | `test_essay_recognizer.py` | 缺少 online OCR 引擎测试 | 添加 `check_engine_available` 和 online 模式 mock 测试 |

---

## 硬编码分析

以下列出需要集中管理的硬编码值，按严重程度排序。

### 关键架构问题（跨文件重复、无单一配置源）

| 编号 | 问题 | 涉及文件 | 说明 |
|------|------|----------|------|
| H127 | **填涂阈值默认值不一致** | pipeline(0.5) vs ChoiceRecognizer(0.06) vs StudentIdRecognizer(0.2) vs extract_student_id(0.3) | 无单一真实来源，pipeline 默认 0.5 远高于实际可用值 |
| H128 | **API URL/模型名重复 5+ 处** | `llm_essay_grader.py` ×3, `essay_recognizer.py` ×1, `main.py` ×1, `app.py` ×3 | 应统一从 `model_config.json` 读取，不散落各处 |
| H129 | **简答题题号 `31` 硬编码 6 处** | `pipeline.py`, `main.py` ×2, `app.py` ×2 | 应从答案键推断 |
| H130 | **题目范围/网格维度重复 6 处** | `5x4` 选择、`3x4` 判断、`1-20`/`21-30` 散落 6 个文件 | 应集中在一份答题卡布局配置中 |
| H57 | **版面 fallback 比率硬编码** | `layout.py` PAGE1/2_FALLBACK `(0.06, 0.26)` 等 | 不同答题卡模板会失效 |

### 评分与分值

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H89 | 每题分值 `3/2/20` 硬编码为默认值 | `grading.py:22` | 构造器可覆盖但默认值散落 |
| H90-H91 | `save_result_xlsx` 内用字面量 `3`/`2` 而非 `self.choice_score` | `grading.py:201,206` | 与构造器默认值不同步风险 |
| H92-H93 | UI 显示 "20分" 硬编码 | `app.py:755,1011` | 应读 `svc.essay_max_score` |

### 布局与网格

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H58 | 选择题网格 `5x4` 硬编码 | `choice_recognizer.py:258` | 题目数变化时需改代码 |
| H60 | 判断题题号映射 `[21..30]` 和 `3x4` 硬编码 | `judge_recognizer.py:244-246` | 同上 |
| H65-H66 | pipeline 中 `question_count=20/10` 硬编码 | `pipeline.py:48,63` | 不从配置读取 |
| H79 | `grading.py` 中 `<=20`/`<=30` 划分题型 | `grading.py:70-75` | 题型边界硬编码 |

### 图像处理参数

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H30 | Canny 阈值 `50, 150` 硬编码 | `student_id_recognizer.py:48` | 不同扫描质量需不同阈值 |
| H15/H96 | 形态学核大小 `(3,3)` 散落多处 | choice/judge/student_id | 统一或参数化 |
| H16/H24 | 水平投影密度阈值 `0.02` 重复 | choice/judge recognizer | 应提取为常量或参数 |
| H19/H27 | 气泡检测尺寸约束 `0.08/0.30/0.40` 重复 | choice/judge recognizer | 同上 |
| H34 | 在线 OCR 图片尺寸上限 `2048` | `essay_recognizer.py:162` | 不同模型限制不同 |
| H45 | 批量上限 `50` 对学生 | `app.py:837` | 无警告静默截断 |

### API 与模型

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H36 | LLM max_tokens `256` | `llm_essay_grader.py:78` | 长答案可能被截断 |
| H37 | LLM temperature `0.3` | `llm_essay_grader.py:79` | 应可调 |
| H84 | OCR max_tokens `1024` | `essay_recognizer.py:184` | 长文识别可能截断 |
| H106 | LLM 评分提示词硬编码 | `llm_essay_grader.py:52-65` | 不同科目需不同评分标准 |
| H110 | OCR 提示词硬编码 | `essay_recognizer.py:182` | 不同场景需不同提示 |
| H107 | LLM 返回解析正则硬编码 | `llm_essay_grader.py:89` | 与提示词耦合，改提示词需同步改正则 |
