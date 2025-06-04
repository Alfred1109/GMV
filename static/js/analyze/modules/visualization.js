/**
 * Core visualization module for GeniusMed Vault
 * Provides base visualization functionality and utilities
 */

const VisualizationCore = {
    // Configuration constants
    CONFIG: {
        CHART_CONTAINER_PREFIX: 'chart-container-',
        DEFAULT_CHART_WIDTH: '100%',
        DEFAULT_CHART_HEIGHT: '400px',
        ANIMATION_DURATION: 750,
        COLORS: [
            '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', 
            '#59a14f', '#edc949', '#af7aa1', '#ff9da7',
            '#9c755f', '#bab0ab'
        ]
    },

    // Utility functions
    utils: {
        /**
         * Generate a unique chart container ID
         * @returns {string} Unique container ID
         */
        generateChartId() {
            return VisualizationCore.CONFIG.CHART_CONTAINER_PREFIX + 
                   Math.random().toString(36).substr(2, 9);
        },

        /**
         * Create a container element for a chart
         * @param {string} containerId - ID for the container
         * @param {string} width - Container width (default: 100%)
         * @param {string} height - Container height (default: 400px)
         * @returns {HTMLElement} Created container element
         */
        createChartContainer(containerId, width, height) {
            const container = document.createElement('div');
            container.id = containerId;
            container.style.width = width || VisualizationCore.CONFIG.DEFAULT_CHART_WIDTH;
            container.style.height = height || VisualizationCore.CONFIG.DEFAULT_CHART_HEIGHT;
            return container;
        },

        /**
         * Format data for visualization
         * @param {Array} data - Raw data array
         * @param {Object} options - Formatting options
         * @returns {Array} Formatted data
         */
        formatData(data, options = {}) {
            if (!Array.isArray(data)) {
                console.error('Invalid data format: Expected array');
                return [];
            }

            return data.map(item => {
                // Deep clone to avoid modifying original data
                let formattedItem = JSON.parse(JSON.stringify(item));
                
                // Apply number formatting if specified
                if (options.numberFormat) {
                    Object.keys(formattedItem).forEach(key => {
                        if (typeof formattedItem[key] === 'number') {
                            formattedItem[key] = Number(formattedItem[key].toFixed(
                                options.numberFormat.decimals || 2
                            ));
                        }
                    });
                }

                // Apply date formatting if specified
                if (options.dateFormat && options.dateFields) {
                    options.dateFields.forEach(field => {
                        if (formattedItem[field]) {
                            formattedItem[field] = new Date(formattedItem[field])
                                .toLocaleDateString(options.dateFormat.locale || 'zh-CN');
                        }
                    });
                }

                return formattedItem;
            });
        },

        /**
         * Validate visualization options
         * @param {Object} options - Options to validate
         * @returns {boolean} Validation result
         */
        validateOptions(options) {
            const requiredFields = ['data', 'type'];
            for (const field of requiredFields) {
                if (!options[field]) {
                    console.error(`Missing required field: ${field}`);
                    return false;
                }
            }

            if (!Array.isArray(options.data) || options.data.length === 0) {
                console.error('Invalid or empty data array');
                return false;
            }

            return true;
        }
    },

    // Event handling system
    events: {
        listeners: {},

        /**
         * Add event listener
         * @param {string} event - Event name
         * @param {Function} callback - Event callback
         */
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        },

        /**
         * Remove event listener
         * @param {string} event - Event name
         * @param {Function} callback - Event callback to remove
         */
        off(event, callback) {
            if (!this.listeners[event]) return;
            this.listeners[event] = this.listeners[event]
                .filter(listener => listener !== callback);
        },

        /**
         * Trigger event
         * @param {string} event - Event name
         * @param {*} data - Event data
         */
        trigger(event, data) {
            if (!this.listeners[event]) return;
            this.listeners[event].forEach(callback => callback(data));
        }
    },

    // Error handling
    handleError(error, context = '') {
        console.error(`Visualization error ${context ? `in ${context}` : ''}: `, error);
        VisualizationCore.events.trigger('error', {
            message: error.message,
            context: context,
            timestamp: new Date().toISOString()
        });
    }
};

// Export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisualizationCore;
} else {
    window.VisualizationCore = VisualizationCore;
} 