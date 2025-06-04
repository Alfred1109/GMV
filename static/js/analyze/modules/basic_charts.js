/**
 * Basic charts module for GeniusMed Vault
 * Implements common chart types using ECharts
 */

const BasicCharts = {
    /**
     * Create a bar chart
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createBarChart(options) {
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

            // Extract categories and series data
            const categories = [...new Set(formattedData.map(item => item[options.xField]))];
            const series = options.yFields.map(field => ({
                name: field,
                type: 'bar',
                data: formattedData.map(item => item[field])
            }));

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: options.yFields,
                    bottom: '5%'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: categories,
                    axisLabel: {
                        rotate: options.xAxisLabelRotate || 0
                    }
                },
                yAxis: {
                    type: 'value',
                    name: options.yAxisName || ''
                },
                series: series,
                color: VisualizationCore.CONFIG.COLORS
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createBarChart');
            return null;
        }
    },

    /**
     * Create a line chart
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createLineChart(options) {
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

            // Extract categories and series data
            const categories = [...new Set(formattedData.map(item => item[options.xField]))];
            const series = options.yFields.map(field => ({
                name: field,
                type: 'line',
                data: formattedData.map(item => item[field]),
                smooth: options.smooth || false,
                symbol: options.symbol || 'circle',
                symbolSize: options.symbolSize || 4
            }));

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: options.yFields,
                    bottom: '5%'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: categories,
                    boundaryGap: false
                },
                yAxis: {
                    type: 'value',
                    name: options.yAxisName || ''
                },
                series: series,
                color: VisualizationCore.CONFIG.COLORS
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createLineChart');
            return null;
        }
    },

    /**
     * Create a pie chart
     * @param {Object} options - Chart options
     * @returns {Object} ECharts instance
     */
    createPieChart(options) {
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

            // Transform data for pie chart
            const seriesData = formattedData.map(item => ({
                name: item[options.nameField],
                value: item[options.valueField]
            }));

            const chartOptions = {
                title: {
                    text: options.title,
                    subtext: options.subtitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: seriesData.map(item => item.name)
                },
                series: [{
                    name: options.seriesName || '',
                    type: 'pie',
                    radius: options.radius || '50%',
                    center: ['50%', '60%'],
                    data: seriesData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }],
                color: VisualizationCore.CONFIG.COLORS
            };

            chart.setOption(chartOptions);
            return chart;
        } catch (error) {
            VisualizationCore.handleError(error, 'createPieChart');
            return null;
        }
    }
};

// Export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BasicCharts;
} else {
    window.BasicCharts = BasicCharts;
} 