/**
 * 分析工具页面交互功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 回归分析 - 交互项设置
    const enableInteractions = document.getElementById('enable-interactions');
    const interactionSelector = document.getElementById('interaction-selector');
    if (enableInteractions && interactionSelector) {
        enableInteractions.addEventListener('change', function() {
            interactionSelector.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 回归分析 - 添加交互项
    const addInteractionBtn = document.getElementById('add-interaction');
    const interactionPairs = document.querySelector('.interaction-pairs');
    if (addInteractionBtn && interactionPairs) {
        addInteractionBtn.addEventListener('click', function() {
            // 获取所有选中的自变量
            const selectedVars = [];
            document.querySelectorAll('input[name="independent_variables"]:checked').forEach(input => {
                selectedVars.push({
                    value: input.value,
                    label: input.parentNode.textContent.trim()
                });
            });
            
            if (selectedVars.length < 2) {
                alert('请至少选择两个自变量才能创建交互项');
                return;
            }
            
            // 创建交互项选择器
            const interactionItem = document.createElement('div');
            interactionItem.className = 'interaction-item mb-2 p-2 border rounded';
            
            // 创建第一个变量下拉框
            const var1Select = document.createElement('select');
            var1Select.className = 'form-select form-select-sm mb-2';
            var1Select.name = 'interaction_var1[]';
            
            // 创建第二个变量下拉框
            const var2Select = document.createElement('select');
            var2Select.className = 'form-select form-select-sm';
            var2Select.name = 'interaction_var2[]';
            
            // 添加选项
            selectedVars.forEach(variable => {
                const option1 = document.createElement('option');
                option1.value = variable.value;
                option1.textContent = variable.label;
                var1Select.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = variable.value;
                option2.textContent = variable.label;
                var2Select.appendChild(option2);
            });
            
            // 添加删除按钮
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn btn-sm btn-outline-danger mt-2';
            removeBtn.innerHTML = '<i class="bi bi-x-lg"></i> 移除';
            removeBtn.addEventListener('click', function() {
                interactionItem.remove();
            });
            
            // 组装交互项
            const interactionHeader = document.createElement('div');
            interactionHeader.className = 'd-flex align-items-center mb-2';
            interactionHeader.innerHTML = '<span class="me-2">交互项:</span><span class="badge bg-info">交互变量对</span>';
            
            interactionItem.appendChild(interactionHeader);
            interactionItem.appendChild(var1Select);
            
            const crossIcon = document.createElement('div');
            crossIcon.className = 'text-center my-1';
            crossIcon.innerHTML = '<i class="bi bi-x"></i>';
            interactionItem.appendChild(crossIcon);
            
            interactionItem.appendChild(var2Select);
            interactionItem.appendChild(removeBtn);
            
            // 添加到容器
            interactionPairs.appendChild(interactionItem);
        });
    }
    
    // 回归分析 - 验证方法切换
    const validationMethod = document.querySelector('select[name="validation_method"]');
    const trainTestOptions = document.getElementById('train-test-options');
    const cvOptions = document.getElementById('cv-options');
    const bootstrapOptions = document.getElementById('bootstrap-options');
    
    if (validationMethod && trainTestOptions && cvOptions && bootstrapOptions) {
        validationMethod.addEventListener('change', function() {
            const method = this.value;
            
            trainTestOptions.style.display = method === 'train_test_split' ? 'block' : 'none';
            cvOptions.style.display = method === 'cross_validation' ? 'block' : 'none';
            bootstrapOptions.style.display = method === 'bootstrap' ? 'block' : 'none';
        });
    }
    
    // 回归分析 - 测试集比例滑块
    const testSizeSlider = document.getElementById('test-size');
    const testSizeValue = document.getElementById('test-size-value');
    
    if (testSizeSlider && testSizeValue) {
        testSizeSlider.addEventListener('input', function() {
            testSizeValue.textContent = this.value + '%';
        });
    }
    
    // 生存分析 - 协变量调整
    const enableCovariates = document.getElementById('enable-covariates');
    const covariatesSelector = document.getElementById('covariates-selector');
    
    if (enableCovariates && covariatesSelector) {
        enableCovariates.addEventListener('change', function() {
            covariatesSelector.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 生存分析 - 竞争风险分析
    const enableCompetingRisks = document.getElementById('enable-competing-risks');
    const competingRisksOptions = document.getElementById('competing-risks-options');
    
    if (enableCompetingRisks && competingRisksOptions) {
        enableCompetingRisks.addEventListener('change', function() {
            competingRisksOptions.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 生存分析 - 分层分析
    const enableStratification = document.getElementById('enable-stratification');
    const stratificationOptions = document.getElementById('stratification-options');
    
    if (enableStratification && stratificationOptions) {
        enableStratification.addEventListener('change', function() {
            stratificationOptions.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 风险评估 - 特征选择
    const enableFeatureSelection = document.getElementById('enable-feature-selection');
    const featureSelectionOptions = document.getElementById('feature-selection-options');
    
    if (enableFeatureSelection && featureSelectionOptions) {
        enableFeatureSelection.addEventListener('change', function() {
            featureSelectionOptions.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 风险评估 - 特征数量滑块
    const featureCountSlider = document.getElementById('feature-count');
    const featureCountValue = document.getElementById('feature-count-value');
    
    if (featureCountSlider && featureCountValue) {
        featureCountSlider.addEventListener('input', function() {
            featureCountValue.textContent = this.value;
        });
    }
    
    // 风险评估 - 超参数调优
    const enableHyperparameterTuning = document.getElementById('enable-hyperparameter-tuning');
    const hyperparameterOptions = document.getElementById('hyperparameter-options');
    
    if (enableHyperparameterTuning && hyperparameterOptions) {
        enableHyperparameterTuning.addEventListener('change', function() {
            hyperparameterOptions.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // 风险评估 - 自定义阈值
    const customThresholds = document.getElementById('custom-thresholds');
    const thresholdInputs = document.getElementById('threshold-inputs');
    
    if (customThresholds && thresholdInputs) {
        customThresholds.addEventListener('change', function() {
            thresholdInputs.style.display = this.checked ? 'block' : 'none';
            
            if (this.checked) {
                // 根据风险等级数量生成阈值滑块
                const riskLevels = document.querySelector('select[name="risk_levels"]').value;
                const thresholdSliders = document.getElementById('threshold-sliders');
                
                if (thresholdSliders) {
                    thresholdSliders.innerHTML = '';
                    
                    // 生成n-1个阈值滑块，其中n是风险等级数量
                    const numSliders = parseInt(riskLevels) - 1;
                    
                    for (let i = 0; i < numSliders; i++) {
                        const sliderContainer = document.createElement('div');
                        sliderContainer.className = 'mb-3';
                        
                        const label = document.createElement('label');
                        label.className = 'form-label';
                        label.textContent = `阈值 ${i + 1}`;
                        
                        const slider = document.createElement('input');
                        slider.type = 'range';
                        slider.className = 'form-range';
                        slider.min = '0';
                        slider.max = '100';
                        slider.step = '1';
                        slider.value = Math.round(100 * (i + 1) / (numSliders + 1));
                        slider.name = `threshold_${i}`;
                        
                        const valueDisplay = document.createElement('div');
                        valueDisplay.className = 'd-flex justify-content-between';
                        
                        const minSpan = document.createElement('span');
                        minSpan.textContent = '0%';
                        
                        const valueSpan = document.createElement('span');
                        valueSpan.className = 'threshold-value';
                        valueSpan.textContent = slider.value + '%';
                        
                        const maxSpan = document.createElement('span');
                        maxSpan.textContent = '100%';
                        
                        valueDisplay.appendChild(minSpan);
                        valueDisplay.appendChild(valueSpan);
                        valueDisplay.appendChild(maxSpan);
                        
                        // 添加事件监听器更新显示值
                        slider.addEventListener('input', function() {
                            valueSpan.textContent = this.value + '%';
                        });
                        
                        sliderContainer.appendChild(label);
                        sliderContainer.appendChild(slider);
                        sliderContainer.appendChild(valueDisplay);
                        thresholdSliders.appendChild(sliderContainer);
                    }
                }
            }
        });
        
        // 风险等级数量变化时更新阈值滑块
        const riskLevelsSelect = document.querySelector('select[name="risk_levels"]');
        if (riskLevelsSelect) {
            riskLevelsSelect.addEventListener('change', function() {
                if (customThresholds.checked) {
                    // 触发自定义阈值的change事件以更新滑块
                    const event = new Event('change');
                    customThresholds.dispatchEvent(event);
                }
            });
        }
    }
    
    // 结局预测 - 预测时间点类型切换
    const timePointType = document.querySelector('select[name="time_point_type"]');
    const fixedTimePoints = document.getElementById('fixed-time-points');
    const dynamicTimePoints = document.getElementById('dynamic-time-points');
    
    if (timePointType && fixedTimePoints && dynamicTimePoints) {
        timePointType.addEventListener('change', function() {
            const type = this.value;
            
            fixedTimePoints.style.display = type === 'fixed' ? 'block' : 'none';
            dynamicTimePoints.style.display = type === 'dynamic' ? 'block' : 'none';
        });
    }
}); 