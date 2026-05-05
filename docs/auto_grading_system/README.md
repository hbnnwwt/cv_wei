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

---

## 已修复清单

### 高优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P2 | `main.py` | 缺少 LLM 评分、错题标注、配置加载、OCR 引擎选择 | 新增 `_build_essay_grader()` 从 `config/` 加载 API 密钥和模型配置构建 LLM 评分器；新增 `_build_ocr_config()` 构建 OCR API 配置；添加 `--llm`（启用 LLM 评分）、`--ocr-engine`（选择引擎）、`--threshold`（填涂阈值）、`--no-mark`（跳过标注）CLI 参数；`batch_process()` 中调用 `mark_and_save()` 生成错题标注图 |
| P3 | `main.py` / `pipeline.py` | CLI 默认阈值 0.5，GUI 使用 0.06 | `--threshold` 参数默认值改为 `0.06`，与 GUI slider 默认值一致；`pipeline.py` 中 `recognize_choices()`/`recognize_judges()` 的 threshold 参数默认值也统一为 `0.06` |
| P4 | `README.md` | 引用不存在的 `config/llm_config.json` | 将文档中所有 `llm_config.json` 引用更正为实际使用的 `model_config.json`（Base URL、模型名称）+ `api_keys.json`（API 密钥，不入库） |
| P5 | `essay_recognizer.py:10` | 无条件 `import torch`，未安装 torch 时崩溃 | 将 `import torch` 包裹在 `try/except ImportError` 中，torch 不可用时设 `has_torch = False`，后续 `recognize()` 中检查该标志并跳过 torch 相关逻辑 |
| P6 | `essay_recognizer.py:211-215` | `recognize()` 吞掉所有异常，返回空字符串 | 区分异常类型：`ImportError`/`OSError`/`ValueError`（依赖缺失/模型加载失败）记录到 `self.last_error` 并返回空串；其他异常同样记录 `last_error` 但不再静默吞掉，方便调试 |
| P22 | `app.py:837` | 批量处理静默限制 50 对学生 | 删除 `pairs = pairs[:50]` 硬编码截断，改为 `for i in range(pair_count)` 按实际图片对数量处理，不再静默丢弃超出的学生 |
| P26 | `main.py:140` | `参考答案.xlsx` 缺失时崩溃 | 在调用 `GradingService.from_xlsx()` 前加 `os.path.exists(answer_key_path)` 检查，文件不存在时打印错误路径并 `sys.exit(1)` |
| P28 | `preprocess.py` | 过暗/过亮扫描无质量警告 | OTSU 二值化后计算 `white_ratio`（白色像素占比），`>98%` 判过暗、`<2%` 判过亮，存入 `preprocessor.quality_warning` 属性（字符串列表），下游可读取并提示用户 |

### 中优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P7 | `llm_essay_grader.py` | API 失败时静默评 0 分 | `_call_api()` 添加最多 2 次重试循环，退避间隔 `1s * (attempt + 1)`；3 次均失败后返回 `(0, max_score, "API 调用失败: ...")` 并在反馈中包含错误信息 |
| P8 | `pipeline.py` | 未验证 `regions` 字典格式/类型 | 新增 `_valid_region(val)` 函数：检查 `isinstance(val, (tuple, list))`、`len(val) == 4`、所有元素为 `int/float`；`extract_student_id()`/`recognize_choices()`/`recognize_judges()`/`recognize_essay()` 在使用 region 前先调用此函数，无效时返回 `None` 或空结果 |
| P9 | `marker.py` | 未验证 `region` 是否为 4 元组 | 同 P8，添加 `_valid_region()` 校验函数，`mark_choices()`/`mark_judges()` 在解包 region 前先校验，无效时跳过对应标注 |
| P10 | `grading.py` | 题目范围硬编码 1-20、21-30 | 改为 `for q in sorted(self.answer_key.get('choice', {}))` 遍历答案键中的实际题号，不再依赖硬编码范围 |
| P11 | `student_id_recognizer.py` | "第三大轮廓"启发式检测脆弱 | 在轮廓筛选中增加宽高比约束 `0.5 <= w/h <= 5.0` 和面积占比约束 `area > 0.1 * image_area`，过滤掉极端形状和过小的噪声轮廓 |
| P12 | `tests/` | 缺少 `test_pipeline.py` 和 `test_marker.py` | 新建 `test_pipeline.py`（15 个用例：覆盖 preprocess_and_analyze、extract_student_id、recognize_choices/judges/essay 的正常/异常输入）和 `test_marker.py`（14 个用例：覆盖 mark_and_save、mark_choices/judges 的各种 region/结果组合） |
| P13 | `grading.py` | `None == None` 可能误判满分 | 将 `score = self.choice_score if given == correct else 0` 改为先判断 `if given is None: score = 0`，避免 `None == None` 为 `True` 导致未答题得满分 |
| P14 | `main.py` | `save_result_xlsx(output_path, output_path, ...)` | 重写 `_save_results_xlsx()`：用 `openpyxl.Workbook()` 从头创建工作簿，不再调用 `GradingService.save_result_xlsx()` 依赖模板文件；手动写入表头、答案行和分数行 |
| P15 | `config/api_keys.json` | 真实 API Key 可能入库 | 确认 git 历史无泄露；创建 `api_keys.json.example` 模板（值为空字符串），实际文件在 `.gitignore` 中排除 |
| P23 | `app.py` / `main.py` | CLI 和 GUI 图片格式列表不一致 | GUI 的文件上传 accept 后缀添加 `.tiff`/`.tif`，与 CLI 的 `IMAGE_EXTENSIONS` 集合保持一致 |
| P24 | `app.py:410` | 并发 GUI 会话互相覆盖临时文件 | 用 `uuid.uuid4().hex[:8]` 生成唯一前缀，临时文件命名为 `tmp_{uuid}_{code}.png`，避免多用户同时操作时互相覆盖 |
| P25 | `marker.py:125` | 重复学号导致标注图被静默覆盖 | 输出文件名逻辑改为：先尝试 `{student_id}_marked.png`，若已存在则追加 `_2`、`_3`... 序号直到文件不存在，避免覆盖已有标注 |
| P27 | `grading.py:69` | `from_xlsx` 遇到非数字列标题崩溃 | `int(q_num)` 包裹在 `try/except (ValueError, TypeError)` 中，转换失败时 `continue` 跳过该列，避免空列或文字列标题导致崩溃 |
| P28 | `preprocess.py` | 过暗/过亮扫描无质量警告 | 同 P28 高优先级条目（重复编号） |
| P33 | `app.py` / `main.py` | 批处理无崩溃恢复 | 每处理完一个学生后，将已处理结果追加到 `_batch_checkpoint.json`；程序崩溃重启时检测该文件，提示用户已有部分结果可恢复 |

### 低优先级

| 编号 | 文件 | 问题 | 修复内容 |
|------|------|------|----------|
| P16 | `main.py` | 无 `--threshold` CLI 参数 | 新增 `parser.add_argument('--threshold', type=float, default=0.06)`，传递给 `process_student()` 和 `recognize_choices()`/`recognize_judges()` |
| P17 | `app.py` | 重复注释行 | 删除多余的重复注释行 |
| P18 | `essay_recognizer.py` | MIME 类型不匹配 | 在线 OCR 上传图片时，base64 编码前缀从 `data:image/jpeg` 改为 `data:image/png`，与实际 PNG 编码格式一致 |
| P19 | `pipeline.py` | `process_student_pair` 未被使用 | `main.py` 不再调用 `process_student_pair()`，改用 `process_student()` 函数（直接调用 `preprocess_and_analyze`/`extract_student_id`/`recognize_*`），`process_student_pair` 保留供外部使用 |
| P20 | `main.py` | `single_process` 未使用 pipeline 函数 | 重写 `single_process()` 调用 `preprocess_and_analyze()` → `extract_student_id()` → `recognize_choices()`/`recognize_judges()`/`recognize_essay()`，与批量模式共用同一套 pipeline 函数 |
| P21 | `test_essay_recognizer.py` | 缺少 online OCR 引擎测试 | 新增 `check_engine_available()` 函数检测引擎是否可导入；新增 online 模式 mock 测试，mock `requests.post` 返回预设 OCR 结果，验证在线引擎调用逻辑 |
| P34 | `llm_essay_grader.py:89` | LLM 分数解析只匹配整数 | 正则从 `(\d+)` 改为 `(\d+(?:\.\d+)?)` ，支持解析 `15.5` 等小数分数 |
| P29 | `preprocess.py` | 大图像（4000x6000）无内存保护 | 添加 `MAX_DIMENSION = 8000` 常量，`process()` 入口检查图像宽高，超过阈值时 `warnings.warn()` 提示可能内存不足，但不拒绝处理 |
| P30 | `preprocess.py:49-67` | 极端旋转（>45°）方向判断失败 | 旋转校正中的 `bot` 判断添加 `bot > 0.005` 额外阈值，防止 `top ≈ 0` 时 `bot` 的微小数值波动导致方向误判 |
| P31 | `choice/judge_recognizer.py` | 咖啡渍或笔迹导致误报 | 选择题：改为比较最暗与最亮选项的填充比率，若 `worst > best * 0.7`（即所有选项都接近最暗），判定为污渍，返回 `None`；判断题：因仅 2 个选项且正常填充率低（~10%），污渍检测过于敏感，直接移除 |
| P32 | `student_id_recognizer.py:190` | 学号数字全部填满无歧义警告 | 添加 `self.ambiguity_warnings` 列表属性，每个数字列中若最高填充率与次高之差 `< 0.05`，追加警告信息，供 GUI 展示提醒用户 |
| P35 | `app.py` | 单次模式不清理临时文件 | 流程结束后用 `glob("tmp_*.png")` 匹配所有临时文件并逐一 `os.remove()` 清理 |
| P36 | `essay_recognizer.py` | 在线 OCR 无批量取消机制 | `recognize()` 方法新增 `cancel_check` 回调参数（可调用对象），每次 API 调用前检查 `cancel_check()` 返回值，为 `True` 时提前终止并返回已识别内容 |
| P37 | `main.py:256-297` | XLSX 导出题号范围硬编码 `range(1,31)` | `_save_results_xlsx()` 从 LAYOUT 读取 `choice.question_start/question_count` 和 `judge.*` 动态构建表头和分数行；简答题列用 `get_essay_questions(service.answer_key)` 动态获取题号 |
| P38 | `judge_recognizer.py:60` | 默认 question_count 含 `question_start+9` 硬编码 | 删除冗余的 `rows_n*cols_n - (rows_n*cols_n - (...))` 表达式，简化为 `question_count = rows_n * cols_n`（pipeline 调用时已从 LAYOUT 传入正确的 question_count） |

---

## 硬编码分析

以下列出需要集中管理的硬编码值，按严重程度排序。

---

## 已修复硬编码

| 编号 | 问题 | 文件 | 修复内容 |
|------|------|------|----------|
| H90-H91 | `save_result_xlsx` 内用字面量 `3`/`2` 而非实例变量 | `grading.py:201,206` | 将 `3`/`2` 替换为 `self.choice_score`/`self.judge_score`，修改构造器参数即可自动更新所有分值计算 |
| H92-H93 | UI 显示 "20分" 硬编码 | `app.py:755,1011` | 将 `"20分"` 字符串替换为 `f"{svc.essay_max_score}分"`，从 `GradingService` 实例动态读取简答题满分 |
| H127 | pipeline 默认阈值 0.5 与识别器 0.06 不一致 | `pipeline.py:32,47` | `recognize_choices()`/`recognize_judges()` 的 threshold 默认值从 `0.5` 改为 `0.06`，与 GUI slider 和识别器内部阈值一致 |
| H128 | API URL/模型名重复 5+ 处 | 4 个文件 × 共 16 处 | 新建 `modules/defaults.py` 定义 `DEFAULT_BASE_URL`/`DEFAULT_LLM_MODEL`/`DEFAULT_OCR_MODEL` 三个常量；`llm_essay_grader.py`（4处）、`essay_recognizer.py`（2处）、`main.py`（4处）、`app.py`（6处）统一 `from modules.defaults import ...` 导入，消除散落的字符串字面量 |
| H129 | 简答题题号 31 硬编码 6 处 | `pipeline/main/app` | 新增 `get_essay_questions(answer_key=None)` 函数：优先从 `answer_key['essay']` 的键集合推断题号列表，fallback 为 `[31]`；`pipeline.py` 的 `recognize_essay()`/`process_student_pair()` 新增 `essay_questions` 参数；`app.py`/`main.py` 中 `{31: essay_text}` 改为 `{essay_questions[0]: essay_text}` |
| H130 | 题目范围/网格维度重复 6 处 | `pipeline/layout/grading/app/main` | 新建 `config/sheet_layout.json` 集中存储 `choice.rows/cols/question_start/question_count` 和 `judge.*`；`pipeline.py` 顶部加载为模块级 `LAYOUT` 常量，`recognize_choices()`/`recognize_judges()` 从 `LAYOUT['choice']`/`LAYOUT['judge']` 读取 question_count 和 question_start，传给识别器 |
| H57 | 版面 fallback 比率硬编码 | `layout.py` | `PAGE1_FALLBACK`/`PAGE2_FALLBACK` 不再作为类属性硬编码，改为从 `pipeline.LAYOUT['layout']` 读取 `page1_fallback`/`page2_fallback` 的 student_id/choice/judge/essay 区间比率 |
| H79 | `<=20`/`<=30` 划分题型 | `grading.py` | 新增 `_classify_question(q_num)` 函数：从 `LAYOUT['choice']`/`LAYOUT['judge']` 读取 `question_start + question_count - 1` 计算题型边界，动态判断题号属于 choice/judge/essay，替代原来的 `<= 20`/`<= 30` 硬编码判断 |
| H65-H66 | pipeline 中 `question_count=20/10` 硬编码 | `pipeline.py:48,63` | `recognize_choices()`/`recognize_judges()` 从 `LAYOUT['choice']`/`LAYOUT['judge']` 读取 `question_count` 和 `question_start`，传给识别器的 `recognize_all_with_viz()`，不再在 pipeline 层硬编码题数 |
| H45 | 批量上限 `50` 对学生 | `app.py:837` | 删除 `pairs = pairs[:50]` 截断，改为按实际图片对数量循环（与 P22 修复同一问题） |

### 评分与分值

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H89 | 每题分值 `3/2/20` 硬编码为默认值 | `grading.py:38` | `GradingService.__init__` 的 `choice_score=3`/`judge_score=2`/`essay_max_score=20` 作为默认参数可被覆盖（如 `GradingService(answer_key, choice_score=5)`），但默认值本身仍硬编码在函数签名中。**修复方案**：将默认值移入 `sheet_layout.json` 新增 `scoring` 字段（`{"choice_score": 3, "judge_score": 2, "essay_max_score": 20}`），`GradingService` 构造时从配置读取 |

### 布局与网格

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H58 | 选择题网格 `5x4` 硬编码 | `choice_recognizer.py` | pipeline 层已从 `LAYOUT` 配置读取 `question_count`/`question_start`，但识别器内部的 `recognize_all_with_viz()` 仍按固定行列数切分网格、逐格扫描气泡。**修复方案**：将 `rows`/`cols` 也加入 `sheet_layout.json` 的 `choice` 字段，pipeline 传参时一并传入识别器，识别器内部用传入参数替代硬编码 |
| H60 | 判断题题号映射 `[21..30]` 和 `3x4` 硬编码 | `judge_recognizer.py:215-217` | `cell_mapping = [21, 22, ..., 30]` 和 `self._detect_cells_fixed(gray_fill, 3, 4, cell_mapping)` 中行列数和题号列表直接写在函数体内。**修复方案**：同 H58，从 `sheet_layout.json` 的 `judge` 字段读取 `rows`/`cols`/`question_start`/`question_count`，动态生成 `cell_mapping` 列表 |

### 图像处理参数

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H30 | Canny 阈值 `50, 150` 硬编码 | `student_id_recognizer.py:49` | `cv2.Canny(gray_roi, 50, 150)` 固定阈值，低对比度扫描件边缘检测不足。**修复方案**：将 `canny_low`/`canny_high` 作为 `StudentIdRecognizer.__init__()` 参数（默认 `50`/`150`），或改为中值自适应阈值 `median * 0.5` / `median * 1.5` |
| H15/H96 | 形态学核大小 `(3,3)` 散落 9 处 | choice/judge/student_id | `cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))` 在 `choice_recognizer.py`（3处）、`judge_recognizer.py`（3处）、`student_id_recognizer.py`（2处）重复出现。**修复方案**：在 `sheet_layout.json` 新增 `morphology.kernel_size` 字段，各识别器初始化时从配置读取，或至少在 `defaults.py` 中定义 `MORPH_KERNEL_SIZE = (3, 3)` 常量统一导入 |
| H16/H24 | 水平投影密度阈值 `0.02` 重复 2 处 | `choice_recognizer.py:128`、`judge_recognizer.py:115` | `_detect_fill_start()` 中 `threshold = 0.02` 判断内容频带起始行，两个识别器各自硬编码相同值。**修复方案**：提取为 `defaults.py` 常量 `FILL_START_THRESHOLD = 0.02`，或作为识别器构造器参数 |
| H19/H27 | 气泡检测尺寸约束 `0.08/0.30/0.40` 重复 | `choice_recognizer.py:179-181` | `min_bw = cell_w * 0.08`、`max_bw = cell_w * 0.30`、`min_bh = cell_h * 0.40` 用于过滤连通域面积，仅出现在选择题识别器。**修复方案**：提取为命名常量 `BUBBLE_MIN_W_RATIO`/`BUBBLE_MAX_W_RATIO`/`BUBBLE_MIN_H_RATIO`，放入 `defaults.py` 或作为构造器参数 |
| H34 | 在线 OCR 图片尺寸上限 `2048` | `essay_recognizer.py:168` | `max_side = 2048` 用于缩放大图后 base64 编码上传，不同 VL 模型支持的最大分辨率不同（Qwen-VL 支持 4096）。**修复方案**：将 `max_side` 作为 `EssayRecognizer.__init__()` 参数（默认 `2048`），或从 `model_config.json` 新增 `ocr_max_image_size` 字段读取 |

### API 与模型

| 编号 | 问题 | 文件 | 说明 |
|------|------|------|------|
| H36 | LLM max_tokens `256` | `llm_essay_grader.py:78` | `_call_api()` 中 `"max_tokens": 256` 限制 LLM 输出长度，详细评语可能被截断。**修复方案**：将 `max_tokens` 作为 `LLMEssayGrader.__init__()` 参数（默认 `256`），或从 `model_config.json` 新增 `llm_max_tokens` 字段读取 |
| H37 | LLM temperature `0.3` | `llm_essay_grader.py:79` | `"temperature": 0.3` 控制评分一致性，不同场景可能需要不同值。**修复方案**：同 H36，作为构造器参数或从配置文件读取 |
| H84 | OCR max_tokens `1024` | `essay_recognizer.py:191` | 在线 OCR payload 中 `"max_tokens": 1024` 限制识别输出，长手写答案可能截断。**修复方案**：从 `model_config.json` 新增 `ocr_max_tokens` 字段读取，或作为 `EssayRecognizer` 构造器参数 |
| H106 | LLM 评分提示词硬编码 | `llm_essay_grader.py:52-65` | `_build_prompt()` 中评分提示词直接写在代码中（"你是一个阅卷助手..."），不同科目/评分标准无法定制。**修复方案**：将提示词模板移入 `config/` 目录（如 `config/llm_prompt.txt`），支持 `{reference}`/`{student_answer}`/`{max_score}` 占位符替换，`_build_prompt()` 从文件加载模板 |
| H110 | OCR 提示词硬编码 | `essay_recognizer.py:188` | 在线 OCR 的用户提示为 `"请逐行识别图片中的所有文字内容，只输出文字，不要添加解释。"`，不同场景可能需要不同指令。**修复方案**：将 OCR 提示词移入 `model_config.json` 新增 `ocr_prompt` 字段，`_recognize_online()` 从配置读取 |
| H107 | LLM 返回解析正则硬编码 | `llm_essay_grader.py:90-91` | `_parse_response()` 用 `re.search(r"得分[：:]\s*(\d+(?:\.\d+)?)", text)` 解析分数，与 H106 的提示词格式强耦合——改提示词格式就必须同步改正则。**修复方案**：提示词和正则配对存放在同一配置源中（如 `model_config.json` 的 `llm_score_pattern` 字段），或改用 JSON mode 输出让 LLM 返回结构化数据，彻底消除正则依赖 |
