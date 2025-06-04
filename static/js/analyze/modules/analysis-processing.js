/**
 * GeniusMed Vault - 统计分析处理模块
 * 提供各种统计分析功能的实现
 */

// 统计分析功能
const StatisticalAnalysis = {
    // 执行描述性统计
    performDescriptiveStatistics(datasetId, variables, stats) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            if (!variables || variables.length === 0) {
                reject(new Error('未选择变量'));
                return;
            }
            
            if (!stats || stats.length === 0) {
                reject(new Error('未指定统计指标'));
                return;
            }
            
            // 构建请求参数
            const requestData = {
                dataset_ids: [parseInt(datasetId)],
                variables: variables,
                stats: stats
            };
            
            // 发送API请求
            fetch('/api/analysis/descriptive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取数据失败: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '分析失败');
                }
                
                resolve(data.results);
            })
            .catch(error => {
                console.error('分析请求失败:', error);
                reject(error);
            });
        });
    },
    
    // 执行假设检验
    performHypothesisTest(datasetId, testType, variables, groupVariable, alpha, hypothesis) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            if (!variables || variables.length === 0) {
                reject(new Error('未选择变量'));
                return;
            }
            
            if (!testType) {
                reject(new Error('未指定检验类型'));
                return;
            }
            
            // 对于需要分组变量的检验类型，检查是否提供了分组变量
            const needsGroupVar = ['ttest', 'anova', 'chi2', 'fisher', 'wilcoxon', 'kruskal'].includes(testType);
            if (needsGroupVar && !groupVariable) {
                reject(new Error('未指定分组变量'));
                return;
            }
            
            // 构建请求参数
            const requestData = {
                dataset_id: parseInt(datasetId),
                test_type: testType,
                variables: variables,
                group_variable: groupVariable,
                alpha: alpha || 0.05,
                hypothesis: hypothesis || 'two-sided'
            };
            
            // 发送API请求
            fetch('/api/analysis/hypothesis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取数据失败: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '分析失败');
                }
                
                resolve(data);
            })
            .catch(error => {
                console.error('假设检验请求失败:', error);
                reject(error);
            });
        });
    },
    
    // 执行相关性分析
    performCorrelationAnalysis(datasetId, correlationType, variables, significanceTest) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            if (!variables || variables.length < 2) {
                reject(new Error('至少需要选择两个变量'));
                return;
            }
            
            if (!correlationType) {
                reject(new Error('未指定相关系数类型'));
                return;
            }
            
            // 构建请求参数
            const requestData = {
                dataset_id: parseInt(datasetId),
                correlation_type: correlationType,
                variables: variables,
                significance_test: !!significanceTest
            };
            
            // 发送API请求
            fetch('/api/analysis/correlation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取数据失败: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '分析失败');
                }
                
                resolve(data);
            })
            .catch(error => {
                console.error('相关性分析请求失败:', error);
                reject(error);
            });
        });
    },
    
    // 执行回归分析
    performRegressionAnalysis(datasetId, regressionType, dependentVariable, independentVariables) {
        // 构建请求参数
        const requestData = {
            dataset_id: datasetId,
            regression_type: regressionType,
            dependent_variable: dependentVariable,
            independent_variables: independentVariables
        };

        // 发送请求到后端
        return fetch('/api/analysis/regression', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.message || '回归分析请求失败');
            }
            return data;
        })
        .catch(error => {
            console.error('回归分析请求失败:', error);
            // 如果API未实现或出错，提供更有意义的错误信息
            return {
                success: false,
                message: `回归分析API请求失败: ${error.message}`,
                error: error.toString()
            };
        });
    }
};

// 临床分析功能
const ClinicalAnalysis = {
    // 执行生存分析
    performSurvivalAnalysis(datasetId, survivalMethod, timeVariable, eventVariable, groupVariable, covariates) {
        // 构建请求参数
        const requestData = {
            dataset_id: datasetId,
            survival_method: survivalMethod,
            time_variable: timeVariable,
            event_variable: eventVariable
        };

        // 添加可选参数
        if (groupVariable) {
            requestData.group_variable = groupVariable;
        }
        
        if (covariates && covariates.length > 0) {
            requestData.covariates = covariates;
        }

        // 发送请求到后端
        return fetch('/api/analysis/survival', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.message || '生存分析请求失败');
            }
            return data;
        })
        .catch(error => {
            console.error('生存分析请求失败:', error);
            // 如果API未实现或出错，提供更有意义的错误信息
            return {
                success: false,
                message: `生存分析API请求失败: ${error.message}`,
                error: error.toString()
            };
        });
    },
    
    // 执行风险评估
    performRiskAssessment(datasetId, modelType, targetVariable) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            if (!modelType) {
                reject(new Error('未指定模型类型'));
                return;
            }
            
            if (!targetVariable) {
                reject(new Error('未选择目标变量'));
                return;
            }
            
            // 构建请求参数
            const requestData = {
                dataset_id: parseInt(datasetId),
                model_type: modelType,
                target_variable: targetVariable
            };
            
            // 发送API请求
            fetch('/api/analysis/risk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取数据失败: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '分析失败');
                }
                
                resolve(data);
            })
            .catch(error => {
                console.error('风险评估请求失败:', error);
                reject(new Error('风险评估API尚未实现'));
            });
        });
    },
    
    // 执行结局预测
    performOutcomePrediction(datasetId, outcomeType) {
        return new Promise((resolve, reject) => {
            if (!datasetId) {
                reject(new Error('未指定数据集ID'));
                return;
            }
            
            if (!outcomeType) {
                reject(new Error('未指定预测结局类型'));
                return;
            }
            
            // 构建请求参数
            const requestData = {
                dataset_id: parseInt(datasetId),
                outcome_type: outcomeType
            };
            
            // 发送API请求
            fetch('/api/analysis/outcome', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取数据失败: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || '分析失败');
                }
                
                resolve(data);
            })
            .catch(error => {
                console.error('结局预测请求失败:', error);
                reject(new Error('结局预测API尚未实现'));
            });
        });
    }
};

// 导出模块
window.AnalysisProcessing = {
    StatisticalAnalysis,
    ClinicalAnalysis
}; 