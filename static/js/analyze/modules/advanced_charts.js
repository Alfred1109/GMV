/**
 * Advanced charts module for GeniusMed Vault
 * Implements specialized chart types for medical data analysis
 */

const AdvancedCharts = {
    /**
     * Create a box plot chart
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createBoxPlot(options) {
        if (!VisualizationCore.utils.validateOptions(options)) {
            return null;
        }

        try {
            const chartId = options.containerId || VisualizationCore.utils.generateChartId();
            const container = VisualizationCore.utils.createChartContainer(
                chartId,
                options.width,
                options.height
            );

            if (options.target) {
                document.querySelector(options.target).appendChild(container);
            }

            const chart = echarts.init(container);
            const formattedData = VisualizationCore.utils.formatData(options.data, options.format);

            // Process data for box plot
            const processBoxPlotData = (data, field) => {
                const values = data.map(item => Number(item[field])).filter(val => !isNaN(val));
                values.sort((a, b) => a - b);
                
                const q1 = values[Math.floor(values.length * 0.25)];
                const median = values[Math.floor(values.length * 0.5)];
                const q3 = values[Math.floor(values.length * 0.75)];
                const iqr = q3 - q1;
                const lower = Math.max(q1 - 1.5 * iqr, values[0]);
                const upper = Math.min(q3 + 1.5 * iqr, values[values.length - 1]);
                
                // Find outliers
                const outliers = values.filter(val => val < lower || val > upper);
                
                return {
                    boxData: [lower, q1, median, q3, upper],
                    outliers: outliers.map(val => [options.xField, val])
                };
            };

            const boxData = [];
            const outliers = [];
            options.yFields.forEach(field => {
                const result = processBoxPlotData(formattedData, field);
                boxData.push(result.boxData);
                outliers.push(...result.outliers);
            });

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '15%'
                },
                xAxis: {
                    type: 'category',
                    data: options.yFields,
                    boundaryGap: true,
                    nameGap: 30,
                    splitArea: {
                        show: false
                    },
                    axisLabel: {
                        rotate: options.xAxisLabelRotate || 0
                    }
                },
                yAxis: {
                    type: 'value',
                    name: options.yAxisName || '',
                    splitArea: {
                        show: true
                    }
                },
                series: [
                    {
                        name: 'boxplot',
                        type: 'boxplot',
                        data: boxData,
                        tooltip: {
                            formatter: function(param) {
                                return [
                                    `${param.name}: `,
                                    `上限: ${param.data[4].toFixed(2)}`,
                                    `Q3: ${param.data[3].toFixed(2)}`,
                                    `中位数: ${param.data[2].toFixed(2)}`,
                                    `Q1: ${param.data[1].toFixed(2)}`,
                                    `下限: ${param.data[0].toFixed(2)}`
                                ].join('<br/>');
                            }
                        }
                    },
                    {
                        name: '异常值',
                        type: 'scatter',
                        data: outliers
                    }
                ]
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createBoxPlot');
            return null;
        }
    },

    /**
     * Create a scatter plot with regression line
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createScatterWithRegression(options) {
        if (!VisualizationCore.utils.validateOptions(options)) {
            return null;
        }

        try {
            const chartId = options.containerId || VisualizationCore.utils.generateChartId();
            const container = VisualizationCore.utils.createChartContainer(
                chartId,
                options.width,
                options.height
            );

            if (options.target) {
                document.querySelector(options.target).appendChild(container);
            }

            const chart = echarts.init(container);
            const formattedData = VisualizationCore.utils.formatData(options.data, options.format);

            // Calculate regression line
            const calculateRegression = (data, xField, yField) => {
                const points = data.map(item => [Number(item[xField]), Number(item[yField])])
                    .filter(point => !isNaN(point[0]) && !isNaN(point[1]));
                
                const n = points.length;
                let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
                
                points.forEach(point => {
                    sumX += point[0];
                    sumY += point[1];
                    sumXY += point[0] * point[1];
                    sumX2 += point[0] * point[0];
                });
                
                const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
                const intercept = (sumY - slope * sumX) / n;
                
                // Get min and max x values for the line
                const minX = Math.min(...points.map(p => p[0]));
                const maxX = Math.max(...points.map(p => p[0]));
                
                return {
                    points: points,
                    regressionLine: [
                        [minX, slope * minX + intercept],
                        [maxX, slope * maxX + intercept]
                    ]
                };
            };

            const regressionData = calculateRegression(
                formattedData, 
                options.xField, 
                options.yField
            );

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: function(param) {
                        if (param.seriesType === 'scatter') {
                            return `${options.xField}: ${param.data[0]}<br/>${options.yField}: ${param.data[1]}`;
                        }
                        return '';
                    }
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '15%'
                },
                xAxis: {
                    type: 'value',
                    name: options.xAxisName || options.xField,
                    scale: true
                },
                yAxis: {
                    type: 'value',
                    name: options.yAxisName || options.yField,
                    scale: true
                },
                series: [
                    {
                        name: '散点',
                        type: 'scatter',
                        data: regressionData.points,
                        symbolSize: options.symbolSize || 8
                    },
                    {
                        name: '回归线',
                        type: 'line',
                        data: regressionData.regressionLine,
                        showSymbol: false,
                        lineStyle: {
                            type: 'solid'
                        }
                    }
                ]
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createScatterWithRegression');
            return null;
        }
    },

    /**
     * Create a survival curve (Kaplan-Meier)
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createSurvivalCurve(options) {
        if (!VisualizationCore.utils.validateOptions(options)) {
            return null;
        }

        try {
            const chartId = options.containerId || VisualizationCore.utils.generateChartId();
            const container = VisualizationCore.utils.createChartContainer(
                chartId,
                options.width,
                options.height
            );

            if (options.target) {
                document.querySelector(options.target).appendChild(container);
            }

            const chart = echarts.init(container);
            const formattedData = VisualizationCore.utils.formatData(options.data, options.format);

            // Calculate Kaplan-Meier estimate
            const calculateKM = (data, timeField, eventField, groupField) => {
                // Sort data by time
                const sortedData = [...data].sort((a, b) => a[timeField] - b[timeField]);
                
                const groups = groupField ? 
                    [...new Set(data.map(item => item[groupField]))] : 
                    ['all'];
                
                const results = {};
                groups.forEach(group => {
                    const groupData = groupField ? 
                        sortedData.filter(item => item[groupField] === group) : 
                        sortedData;
                    
                    let atRisk = groupData.length;
                    let survival = 1.0;
                    const survivalData = [[0, 1.0]];
                    
                    groupData.forEach(item => {
                        if (item[eventField]) {
                            survival *= (atRisk - 1) / atRisk;
                            survivalData.push([Number(item[timeField]), survival]);
                        }
                        atRisk--;
                    });
                    
                    results[group] = survivalData;
                });
                
                return results;
            };

            const kmData = calculateKM(
                formattedData,
                options.timeField,
                options.eventField,
                options.groupField
            );

            const series = Object.entries(kmData).map(([group, data], index) => ({
                name: group,
                type: 'line',
                data: data,
                step: 'end',
                showSymbol: false,
                lineStyle: {
                    width: 2
                }
            }));

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        const param = params[0];
                        return `时间: ${param.data[0]}<br/>生存率: ${(param.data[1] * 100).toFixed(2)}%`;
                    }
                },
                legend: {
                    data: Object.keys(kmData),
                    bottom: '5%'
                },
                grid: {
                    left: '10%',
                    right: '5%',
                    bottom: '15%'
                },
                xAxis: {
                    type: 'value',
                    name: options.xAxisName || '时间',
                    min: 0
                },
                yAxis: {
                    type: 'value',
                    name: options.yAxisName || '生存率',
                    min: 0,
                    max: 1,
                    axisLabel: {
                        formatter: '{value * 100}%'
                    }
                },
                series: series
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createSurvivalCurve');
            return null;
        }
    }
};

// Export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedCharts;
} else {
    window.AdvancedCharts = AdvancedCharts;
} 