// Week 01 计算机视觉 Web 演示系统 - 前端脚本

// 全局状态
const state = {
    modules: [],
    currentModule: null,
    currentOperation: null,
    originalImage: null,
    resultImage: null
};

// DOM 元素
const elements = {
    moduleNav: null,
    operationSelect: null,
    paramsPanel: null,
    paramsContainer: null,
    processBtn: null,
    resultPanel: null,
    resultContent: null,
    originalCanvas: null,
    resultCanvas: null,
    loadDefaultBtn: null,
    uploadInput: null,
    downloadBtn: null,
    testImageSelect: null
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initEventListeners();
    loadModules();
    loadDefaultImage();
});

// 初始化 DOM 元素
function initElements() {
    elements.moduleNav = document.getElementById('moduleNav');
    elements.operationSelect = document.getElementById('operationSelect');
    elements.paramsPanel = document.getElementById('paramsPanel');
    elements.paramsContainer = document.getElementById('paramsContainer');
    elements.processBtn = document.getElementById('processBtn');
    elements.resultPanel = document.getElementById('resultPanel');
    elements.resultContent = document.getElementById('resultContent');
    elements.originalCanvas = document.getElementById('originalCanvas');
    elements.resultCanvas = document.getElementById('resultCanvas');
    elements.loadDefaultBtn = document.getElementById('loadDefaultBtn');
    elements.uploadInput = document.getElementById('uploadInput');
    elements.downloadBtn = document.getElementById('downloadBtn');
    elements.testImageSelect = document.getElementById('testImageSelect');

    // 设置 canvas 上下文
    const originalCtx = elements.originalCanvas.getContext('2d');
    const resultCtx = elements.resultCanvas.getContext('2d');
}

// 初始化事件监听
function initEventListeners() {
    elements.loadDefaultBtn.addEventListener('click', loadDefaultImage);
    elements.uploadInput.addEventListener('change', handleUpload);
    elements.downloadBtn.addEventListener('click', downloadResult);
    elements.operationSelect.addEventListener('change', handleOperationChange);
    elements.processBtn.addEventListener('click', processImage);
    if (elements.testImageSelect) {
        elements.testImageSelect.addEventListener('change', handleTestImageSelect);
    }
}

// 加载模块列表
async function loadModules() {
    try {
        const response = await fetch('/api/modules');
        state.modules = await response.json();
        renderModuleNav();
    } catch (error) {
        console.error('加载模块失败:', error);
        elements.moduleNav.innerHTML = '<p>加载失败</p>';
    }
}

// 渲染模块导航
function renderModuleNav() {
    elements.moduleNav.innerHTML = '';

    state.modules.forEach((module, index) => {
        const btn = document.createElement('button');
        btn.className = 'module-btn';
        if (index === 0) btn.classList.add('active');
        btn.innerHTML = `
            <span class="module-title">${module.name}</span>
            <span class="module-desc">${module.description}</span>
        `;
        btn.addEventListener('click', () => selectModule(index));
        elements.moduleNav.appendChild(btn);
    });

    // 默认选择第一个模块
    if (state.modules.length > 0) {
        selectModule(0);
    }
}

// 选择模块
function selectModule(index) {
    state.currentModule = state.modules[index];

    // 更新导航按钮状态
    document.querySelectorAll('.module-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === index);
    });

    // 更新操作下拉列表
    updateOperationSelect();
}

// 更新操作下拉列表
function updateOperationSelect() {
    elements.operationSelect.innerHTML = '<option value="">请选择操作...</option>';

    if (!state.currentModule) return;

    state.currentModule.apis.forEach(api => {
        const option = document.createElement('option');
        option.value = api.name;
        option.textContent = api.label;
        elements.operationSelect.appendChild(option);
    });

    elements.paramsPanel.style.display = 'none';
    elements.processBtn.disabled = true;
}

// 处理操作选择变化
function handleOperationChange() {
    const operationName = elements.operationSelect.value;

    if (!operationName) {
        elements.paramsPanel.style.display = 'none';
        elements.processBtn.disabled = true;
        return;
    }

    // 找到对应的 API
    const api = state.currentModule.apis.find(a => a.name === operationName);
    state.currentOperation = api;

    // 渲染参数面板
    renderParamsPanel(api.params);

    elements.paramsPanel.style.display = 'block';
    elements.processBtn.disabled = !state.originalImage;
}

// 渲染参数面板
function renderParamsPanel(params) {
    elements.paramsContainer.innerHTML = '';

    if (!params || params.length === 0) {
        elements.paramsContainer.innerHTML = '<p style="color: var(--text-secondary);">此操作无需参数</p>';
        return;
    }

    params.forEach(param => {
        const paramItem = document.createElement('div');
        paramItem.className = 'param-item';

        const label = document.createElement('label');
        label.textContent = param.label;
        paramItem.appendChild(label);

        // 检查参数类型
        if (param.type === 'text') {
            // 文本输入框
            const input = document.createElement('input');
            input.type = 'text';
            input.id = `param_${param.name}`;
            input.className = 'select-input';
            input.value = param.default || '';
            paramItem.appendChild(input);
        } else {
            // 滑块（默认）
            const value = param.default !== undefined ? param.default : param.min;
            const valueDiv = document.createElement('div');
            valueDiv.className = 'param-value';

            const slider = document.createElement('input');
            slider.type = 'range';
            slider.id = `param_${param.name}`;
            slider.min = param.min;
            slider.max = param.max;
            slider.step = param.step || 1;
            slider.value = value;

            const valueSpan = document.createElement('span');
            valueSpan.id = `value_${param.name}`;
            valueSpan.textContent = value;

            valueDiv.appendChild(slider);
            valueDiv.appendChild(valueSpan);
            paramItem.appendChild(valueDiv);

            // 添加滑块事件监听
            slider.addEventListener('input', () => {
                valueSpan.textContent = slider.value;
            });
        }

        elements.paramsContainer.appendChild(paramItem);
    });
}

// 加载默认图片
async function loadDefaultImage() {
    try {
        const response = await fetch('/api/default_image');
        const data = await response.json();

        if (data.success) {
            displayImage(data.image, 'original');
            state.originalImage = data.image;
            elements.processBtn.disabled = !elements.operationSelect.value;
        }
    } catch (error) {
        console.error('加载默认图片失败:', error);
    }
}

// 处理测试图片选择
async function handleTestImageSelect(event) {
    const imageType = event.target.value;
    if (!imageType) return;

    try {
        const response = await fetch(`/api/test_image/${imageType}`);
        const data = await response.json();

        if (data.success) {
            displayImage(data.image, 'original');
            state.originalImage = data.image;
            elements.processBtn.disabled = !elements.operationSelect.value;
        } else {
            alert('加载测试图片失败: ' + data.error);
        }
    } catch (error) {
        console.error('加载测试图片失败:', error);
        alert('加载测试图片失败: ' + error.message);
    }

    // 重置选择器
    event.target.value = '';
}

// 处理图片上传
function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            // 绘制到 canvas
            const canvas = elements.originalCanvas;
            const ctx = canvas.getContext('2d');

            // 调整 canvas 大小
            const maxWidth = 600;
            const maxHeight = 400;
            let width = img.width;
            let height = img.height;

            if (width > maxWidth) {
                height = (maxWidth / width) * height;
                width = maxWidth;
            }
            if (height > maxHeight) {
                width = (maxHeight / height) * width;
                height = maxHeight;
            }

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);

            // 转换为 base64
            state.originalImage = canvas.toDataURL('image/jpeg', 0.8);
            elements.processBtn.disabled = !elements.operationSelect.value;
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// 显示图片
function displayImage(base64Data, type) {
    const canvas = type === 'original' ? elements.originalCanvas : elements.resultCanvas;
    const ctx = canvas.getContext('2d');

    const img = new Image();
    img.onload = () => {
        const maxWidth = 600;
        const maxHeight = 400;
        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
            height = (maxWidth / width) * height;
            width = maxWidth;
        }
        if (height > maxHeight) {
            width = (maxHeight / height) * width;
            height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);
    };
    img.src = 'data:image/jpeg;base64,' + base64Data;
}

// 处理图片
async function processImage() {
    if (!state.originalImage || !state.currentOperation) return;

    // 收集参数
    const params = {};
    if (state.currentOperation.params) {
        state.currentOperation.params.forEach(param => {
            const input = document.getElementById(`param_${param.name}`);
            if (input) {
                if (param.type === 'text') {
                    // 文本类型直接获取值
                    params[param.name] = input.value;
                } else {
                    // 滑块类型转换为数字
                    let value = parseFloat(input.value);
                    if (param.step === 1) value = parseInt(value);
                    params[param.name] = value;
                }
            }
        });
    }

    // 显示加载状态
    elements.processBtn.textContent = '处理中...';
    elements.processBtn.disabled = true;

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: state.originalImage,
                operation: state.currentOperation.name,
                params: params
            })
        });

        const data = await response.json();

        if (data.success !== false) {
            // 显示结果图片
            if (data.image) {
                displayImage(data.image, 'result');
                state.resultImage = data.image;
            }

            // ROI裁剪特殊处理 - 显示裁剪后的图片
            if (data.cropped) {
                displayImage(data.cropped, 'result');
                state.resultImage = data.cropped;
            }

            // 显示OMR算法步骤演示（特殊处理）
            if (data.steps) {
                displayResults({steps: data.steps, results: data.results});
            }
            // 显示质量检测结果
            else if (data.quality) {
                displayResults(data.quality);
            }
            // 显示普通结果数据
            else if (data.results || data.data) {
                displayResults(data.results || data.data);
            }
            // 显示ROI形状信息
            else if (data.roi_shape) {
                elements.resultPanel.style.display = 'block';
                elements.resultContent.innerHTML = `
                    <div class="result-item">
                        <div class="result-label">裁剪区域大小</div>
                        <div class="result-value">${data.roi_shape.join(' × ')}</div>
                    </div>
                `;
            }

            // 清除之前的结果面板
            if (!data.results && !data.data && !data.roi_shape && !data.quality && !data.steps) {
                elements.resultPanel.style.display = 'none';
            }
        } else {
            alert('处理失败: ' + data.error);
        }
    } catch (error) {
        console.error('处理失败:', error);
        alert('处理失败: ' + error.message);
    } finally {
        elements.processBtn.textContent = '执行处理';
        elements.processBtn.disabled = false;
    }
}

// 显示结果数据
function displayResults(data) {
    elements.resultPanel.style.display = 'block';
    elements.resultContent.innerHTML = '';

    if (!data) {
        return;
    }

    if (Array.isArray(data)) {
        // 气泡检测结果
        if (data.length > 0 && data[0].option) {
            renderBubbleResults(data);
        } else {
            // 空数组或其他数组，不渲染或显示提示
            elements.resultContent.innerHTML = '<div class="result-item" style="color: var(--text-secondary);">无检测结果</div>';
        }
    } else if (typeof data === 'object') {
        renderObjectResults(data);
    } else {
        elements.resultContent.innerHTML = `<div class="result-item">${data}</div>`;
    }
}

// 渲染气泡检测结果
function renderBubbleResults(results) {
    const grid = document.createElement('div');
    grid.className = 'bubble-grid';

    results.forEach(r => {
        const item = document.createElement('div');
        item.className = `bubble-item ${r.status}`;
        item.textContent = `${r.option}: ${r.ratio}%`;
        grid.appendChild(item);
    });

    elements.resultContent.appendChild(grid);
}

// 渲染对象结果
function renderObjectResults(data) {
    // OMR算法步骤演示
    if (data.steps) {
        renderOMRSteps(data);
        return;
    }

    // 质量检测
    if (data.overall !== undefined) {
        renderQualityResults(data);
        return;
    }

    // 批量处理
    if (data.summary) {
        renderBatchResults(data);
        return;
    }

    // 通用对象渲染 - 添加安全检查
    try {
        const entries = Object.entries(data);
        if (entries.length > 0) {
            renderGenericResults(entries);
        } else {
            elements.resultContent.innerHTML = '<div class="result-item" style="color: var(--text-secondary);">无结果数据</div>';
        }
    } catch (e) {
        console.error('渲染对象结果失败:', e);
        elements.resultContent.innerHTML = '<div class="result-item" style="color: var(--danger-color);">数据格式错误</div>';
    }
}

// 渲染OMR算法步骤
function renderOMRSteps(data) {
    const steps = data.steps;
    const stepNames = {
        'step1_preprocess': '步骤1: 图像预处理（灰度化+高斯模糊）',
        'step2_edged': '步骤2: Canny边缘检测',
        'step3_contour': '步骤3: 查找答题卡轮廓',
        'step4_warped': '步骤4: 透视变换矫正',
        'step5_threshold': '步骤5: 二值化（Otsu阈值）',
        'step6_bubbles': '步骤6: 查找并排序气泡轮廓',
        'step7_graded': '步骤7: 填涂检测与评分'
    };

    // 创建步骤容器
    const stepsContainer = document.createElement('div');
    stepsContainer.className = 'omr-steps-container';

    // 添加每个步骤的图片
    Object.entries(steps).forEach(([stepKey, base64Img]) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'omr-step-item';

        const title = document.createElement('div');
        title.className = 'omr-step-title';
        title.textContent = stepNames[stepKey] || stepKey;

        const imgContainer = document.createElement('div');
        imgContainer.className = 'omr-step-img';

        const img = document.createElement('img');
        img.src = 'data:image/jpeg;base64,' + base64Img;
        img.alt = stepNames[stepKey];

        imgContainer.appendChild(img);
        stepDiv.appendChild(title);
        stepDiv.appendChild(imgContainer);
        stepsContainer.appendChild(stepDiv);
    });

    elements.resultContent.appendChild(stepsContainer);

    // 如果有答题结果，也显示出来
    if (data.results && data.results.length > 0) {
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'result-item';
        resultsDiv.innerHTML = '<div class="result-label">答题结果</div>';

        const resultsTable = document.createElement('table');
        resultsTable.className = 'results-table';

        // 表头
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>题号</th>
                <th>学生答案</th>
                <th>正确答案</th>
                <th>结果</th>
            </tr>
        `;
        resultsTable.appendChild(thead);

        // 表体
        const tbody = document.createElement('tbody');
        data.results.forEach(r => {
            const row = document.createElement('tr');
            const resultClass = r.is_correct ? 'success' : 'error';
            const resultText = r.is_correct ? '✓ 正确' : '✗ 错误';
            row.innerHTML = `
                <td>${r.question}</td>
                <td>${r.selected}</td>
                <td>${r.correct}</td>
                <td class="${resultClass}">${resultText}</td>
            `;
            tbody.appendChild(row);
        });
        resultsTable.appendChild(tbody);

        resultsDiv.appendChild(resultsTable);
        elements.resultContent.appendChild(resultsDiv);
    }
}

// 渲染质量检测结果
function renderQualityResults(data) {
    const fields = [
        { key: 'resolution', label: '分辨率' },
        { key: 'brightness', label: '亮度' },
        { key: 'brightness_status', label: '亮度状态' },
        { key: 'contrast', label: '对比度' },
        { key: 'contrast_status', label: '对比度状态' },
        { key: 'sharpness', label: '清晰度' },
        { key: 'sharpness_status', label: '清晰度状态' },
        { key: 'noise_level', label: '噪声水平' },
        { key: 'noise_status', label: '噪声状态' },
        { key: 'noise_variance', label: '噪声方差' },
        { key: 'noise_variance_status', label: '噪声评级' },
        { key: 'quality_score', label: '质量得分' },
        { key: 'overall', label: '整体评价' }
    ];

    fields.forEach(field => {
        const item = document.createElement('div');
        item.className = 'result-item';

        let valueClass = '';
        if (field.key.includes('status') || field.key === 'overall' || field.key === 'noise_status') {
            if (['正常', '清晰', '合格', '完美', '优秀', '良好', '低噪声'].includes(data[field.key])) {
                valueClass = 'success';
            } else if (['过暗', '过亮', '模糊', '高噪声', '严重噪声', '差'].includes(data[field.key])) {
                valueClass = 'danger';
            } else if (['中等噪声', '有噪声', '一般'].includes(data[field.key])) {
                valueClass = 'warning';
            }
        }

        // 质量得分特殊处理
        if (field.key === 'quality_score') {
            const score = data[field.key];
            if (score >= 4) valueClass = 'success';
            else if (score >= 2) valueClass = 'warning';
            else valueClass = 'danger';
        }

        item.innerHTML = `
            <div class="result-label">${field.label}</div>
            <div class="result-value ${valueClass}">${data[field.key]}</div>
        `;
        elements.resultContent.appendChild(item);
    });
}

// 渲染批量处理结果
function renderBatchResults(data) {
    // 摘要
    const summary = document.createElement('div');
    summary.className = 'result-item';
    summary.innerHTML = `
        <div class="result-label">处理摘要</div>
        <div>试卷数: ${data.summary.total_papers} | 题目数: ${data.summary.num_questions}</div>
        <div>平均分: ${data.summary.avg_score} | 最高: ${data.summary.max_score} | 最低: ${data.summary.min_score}</div>
    `;
    elements.resultContent.appendChild(summary);

    // 答案分布
    if (data.answer_distribution) {
        const dist = document.createElement('div');
        dist.className = 'result-item';
        dist.innerHTML = '<div class="result-label">答案分布</div>';

        Object.entries(data.answer_distribution).forEach(([q, distData]) => {
            const row = document.createElement('div');
            row.style.marginTop = '0.5rem';

            const maxCount = Math.max(...Object.values(distData));
            const bars = Object.entries(distData).map(([opt, count]) => {
                const width = (count / maxCount * 100).toFixed(0);
                return `<span style="display:inline-block;width:${width}%;background:var(--primary-color);margin:0 2px;padding:2px 5px;border-radius:3px;font-size:0.7rem;">${opt}:${count}</span>`;
            }).join('');

            row.innerHTML = `<div>${q}: ${bars}</div>`;
            dist.appendChild(row);
        });

        elements.resultContent.appendChild(dist);
    }
}

// 渲染通用结果
function renderGenericResults(data) {
    // 确保data是数组
    const dataArray = Array.isArray(data) ? data : Array.from(data);

    dataArray.forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.innerHTML = `
            <div class="result-label">${key}</div>
            <div class="result-value">${value}</div>
        `;
        elements.resultContent.appendChild(item);
    });
}

// 下载结果
function downloadResult() {
    if (!state.resultImage) {
        alert('没有可下载的结果');
        return;
    }

    const link = document.createElement('a');
    link.href = 'data:image/jpeg;base64,' + state.resultImage;
    link.download = 'result.jpg';
    link.click();
}
