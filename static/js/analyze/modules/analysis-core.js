/**
 * GeniusMed Vault - 分析核心模块
 * 提供统计分析、临床分析和可视化的核心功能
 */

// 全局分析状态管理
const AnalysisState = {
    selectedDataset: null,
    selectedVariables: [],
    analysisType: null,
    analysisOptions: {},
    results: null,
    
    // 重置状态
    reset() {
        this.selectedDataset = null;
        this.selectedVariables = [];
        this.analysisType = null;
        this.analysisOptions = {};
        this.results = null;
    },
    
    // 设置数据集
    setDataset(datasetId) {
        this.selectedDataset = datasetId;
        this.selectedVariables = [];
    },
    
    // 添加变量
    addVariable(variableId) {
        if (!this.selectedVariables.includes(variableId)) {
            this.selectedVariables.push(variableId);
        }
    },
    
    // 移除变量
    removeVariable(variableId) {
        const index = this.selectedVariables.indexOf(variableId);
        if (index !== -1) {
            this.selectedVariables.splice(index, 1);
        }
    },
    
    // 设置分析类型
    setAnalysisType(type) {
        this.analysisType = type;
        this.analysisOptions = {};
    },
    
    // 设置分析选项
    setAnalysisOption(key, value) {
        this.analysisOptions[key] = value;
    },
    
    // 存储分析结果
    setResults(results) {
        this.results = results;
    }
};

// 数据集变量加载和管理
const DatasetManager = {
    // 加载数据集变量
    loadDatasetVariables(datasetId, toolType) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            // 显示加载状态
            const loadingHtml = `
                <div class="loading-indicator">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <span class="ms-2">正在加载变量...</span>
                </div>
            `;
            
            // 根据工具类型选择不同的变量容器
            let variablesContainer;
            switch(toolType) {
                case 'descriptive':
                    variablesContainer = document.querySelector('#descriptive-panel .variables-container .variables-list');
                    break;
                case 'hypothesis':
                    variablesContainer = document.querySelector('#hypothesis-panel .variables-container');
                    break;
                case 'correlation':
                    variablesContainer = document.querySelector('#correlation-panel .variables-container');
                    break;
                case 'regression':
                    variablesContainer = document.querySelector('#regression-panel .variables-container');
                    break;
                case 'survival':
                    variablesContainer = document.querySelector('#survival-panel .variables-container');
                    break;
                case 'risk':
                    variablesContainer = document.querySelector('#risk-panel .variables-container');
                    break;
                case 'charts':
                    variablesContainer = document.querySelector('#charts-panel .variables-container');
                    break;
                default:
                    variablesContainer = document.querySelector('.variables-container');
            }
            
            if (!variablesContainer) {
                reject(new Error(`找不到变量容器: ${toolType}`));
                return;
            }
            
            // 显示加载状态
            variablesContainer.innerHTML = loadingHtml;
            
            // 调用API获取变量
            fetch(`/api/datasets/${datasetId}/variables`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取变量失败: ' + response.status + ' ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '获取变量失败');
                }
                
                // 处理变量数据
                const variables = data.variables || [];
                let continuousVars = [];
                let categoricalVars = [];
                let temporalVars = [];
                
                // 分类变量
                variables.forEach(variable => {
                    if (variable.type === 'continuous') {
                        continuousVars.push(variable);
                    } else if (variable.type === 'categorical') {
                        categoricalVars.push(variable);
                    } else if (variable.type === 'temporal') {
                        temporalVars.push(variable);
                    } else {
                        // 默认处理为分类变量
                        categoricalVars.push(variable);
                    }
                });
                
                // 构建变量选择器HTML
                let variablesHTML = '';
                
                if (continuousVars.length > 0) {
                    variablesHTML += `<div class="variable-category">连续变量</div>
                                     <div class="variable-selector">`;
                    
                    continuousVars.forEach(variable => {
                        const checkboxName = toolType === 'hypothesis' ? 'hypothesis_variables' : 
                                            toolType === 'correlation' ? 'correlation_variables' : 
                                            toolType === 'regression' ? 'independent_variables' :
                                            toolType === 'survival' ? 'survival_variables' :
                                            toolType === 'risk' ? 'risk_variables' :
                                            toolType === 'charts' ? 'chart_variables' : 'variables';
                        variablesHTML += `<label><input type="checkbox" name="${checkboxName}" value="${variable.id}"> ${variable.name}</label>`;
                    });
                    
                    variablesHTML += `</div>`;
                }
                
                if (categoricalVars.length > 0) {
                    variablesHTML += `<div class="variable-category">分类变量</div>
                                     <div class="variable-selector">`;
                    
                    categoricalVars.forEach(variable => {
                        const checkboxName = toolType === 'hypothesis' ? 'hypothesis_variables' : 
                                            toolType === 'correlation' ? 'correlation_variables' : 
                                            toolType === 'regression' ? 'independent_variables' :
                                            toolType === 'survival' ? 'survival_variables' :
                                            toolType === 'risk' ? 'risk_variables' :
                                            toolType === 'charts' ? 'chart_variables' : 'variables';
                        variablesHTML += `<label><input type="checkbox" name="${checkboxName}" value="${variable.id}"> ${variable.name}</label>`;
                    });
                    
                    variablesHTML += `</div>`;
                }
                
                if (temporalVars.length > 0) {
                    variablesHTML += `<div class="variable-category">时间变量</div>
                                     <div class="variable-selector">`;
                    
                    temporalVars.forEach(variable => {
                        const checkboxName = toolType === 'hypothesis' ? 'hypothesis_variables' : 
                                            toolType === 'correlation' ? 'correlation_variables' : 
                                            toolType === 'regression' ? 'independent_variables' :
                                            toolType === 'survival' ? 'survival_variables' :
                                            toolType === 'risk' ? 'risk_variables' :
                                            toolType === 'charts' ? 'chart_variables' : 'variables';
                        variablesHTML += `<label><input type="checkbox" name="${checkboxName}" value="${variable.id}"> ${variable.name}</label>`;
                    });
                    
                    variablesHTML += `</div>`;
                }
                
                // 如果没有变量
                if (variables.length === 0) {
                    variablesHTML = `<div class="alert alert-info">该数据集没有可用的变量</div>`;
                }
                
                // 更新变量容器
                variablesContainer.innerHTML = variablesHTML;
                
                // 如果是假设检验，还需要更新分组变量下拉列表
                if (toolType === 'hypothesis') {
                    const groupVarSelect = document.getElementById('group-variable');
                    if (groupVarSelect) {
                        // 清除现有选项
                        while (groupVarSelect.options.length > 1) {
                            groupVarSelect.remove(1);
                        }
                        
                        // 添加分类变量作为分组变量选项
                        categoricalVars.forEach(variable => {
                            const option = document.createElement('option');
                            option.value = variable.id;
                            option.textContent = variable.name;
                            groupVarSelect.appendChild(option);
                        });
                    }
                }
                
                resolve(variables);
            })
            .catch(error => {
                console.error('加载变量失败:', error);
                
                // 显示错误信息
                variablesContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>加载变量失败</strong>
                        <p>${error.message}</p>
                        <p>请检查您是否已登录，以及是否有权限访问此数据集。</p>
                        <p>您可以尝试刷新页面或重新登录。</p>
                    </div>
                `;
                
                // 记录详细错误到控制台以便调试
                console.error('API请求详情:', {
                    url: `/api/datasets/${datasetId}/variables`,
                    datasetId: datasetId,
                    toolType: toolType,
                    errorMessage: error.message,
                    errorStack: error.stack
                });
                
                reject(error);
            });
        });
    }
};

// 工具函数
const AnalysisUtils = {
    // 格式化统计值
    formatStatValue(value) {
        if (value === null || value === undefined) {
            return 'N/A';
        }
        
        if (typeof value === 'number') {
            // 检查是否为整数
            if (Number.isInteger(value)) {
                return value.toString();
            }
            
            // 如果是小数，保留两位小数
            return value.toFixed(2);
        }
        
        return value;
    },
    
    // 获取统计量的显示名称
    getStatDisplayName(stat) {
        const statNames = {
            'mean': '均值',
            'median': '中位数',
            'sd': '标准差',
            'var': '方差',
            'min': '最小值',
            'max': '最大值',
            'q1': '第一四分位数',
            'q3': '第三四分位数',
            'skewness': '偏度',
            'kurtosis': '峰度',
            'count': '计数',
            'missing': '缺失值'
        };
        return statNames[stat] || stat;
    },
    
    // 生成随机ID
    generateId(prefix = 'id') {
        return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    // 深拷贝对象
    deepCopy(obj) {
        return JSON.parse(JSON.stringify(obj));
    }
};

// 导出模块
window.AnalysisCore = {
    State: AnalysisState,
    DatasetManager,
    Utils: AnalysisUtils
}; 