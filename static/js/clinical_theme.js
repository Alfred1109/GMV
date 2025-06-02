/**
 * ZL-GeniusMedVault Clinical Theme JavaScript
 * Provides interactive functionality for the clinical theme interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar sections
    const sidebarTitles = document.querySelectorAll('.sidebar-title');
    sidebarTitles.forEach(title => {
        title.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.display === 'none') {
                content.style.display = 'block';
                this.classList.remove('collapsed');
            } else {
                content.style.display = 'none';
                this.classList.add('collapsed');
            }
        });
    });

    // Add hover effects to clinical tables
    const tableRows = document.querySelectorAll('.clinical-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('row-highlight');
        });
        row.addEventListener('mouseleave', function() {
            this.classList.remove('row-highlight');
        });
    });

    // Format any dates in the interface
    formatDates();

    // Add click handler for info boxes
    const infoBoxes = document.querySelectorAll('.clinical-info-box');
    infoBoxes.forEach(box => {
        box.addEventListener('click', function(e) {
            // Don't trigger if clicking on a button or link
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                const boxTitle = this.querySelector('.info-box-title').textContent.trim();
                console.log(`Info box clicked: ${boxTitle}`);
                // Could expand or navigate based on the box
            }
        });
    });
    
    // Initialize any tooltips
    initTooltips();
});

/**
 * Format dates in a more readable way
 */
function formatDates() {
    const dateElements = document.querySelectorAll('.date-format');
    dateElements.forEach(el => {
        const dateStr = el.textContent.trim();
        try {
            const date = new Date(dateStr);
            if (!isNaN(date)) {
                const options = { year: 'numeric', month: 'short', day: 'numeric' };
                el.textContent = date.toLocaleDateString('zh-CN', options);
            }
        } catch (e) {
            console.error('Error formatting date:', e);
        }
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

/**
 * Update the clinical-table sorting
 * @param {HTMLElement} headerCell - The header cell that was clicked
 * @param {string} tableId - The ID of the table to sort
 */
function sortTable(headerCell, tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headerIndex = Array.from(headerCell.parentNode.children).indexOf(headerCell);
    const isAscending = headerCell.classList.contains('sort-asc');
    
    // Reset all headers
    const headers = headerCell.parentNode.querySelectorAll('th');
    headers.forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Set new sort direction
    headerCell.classList.toggle('sort-desc', isAscending);
    headerCell.classList.toggle('sort-asc', !isAscending);
    
    // Get rows and convert to array for sorting
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort the rows
    rows.sort((a, b) => {
        const aValue = a.children[headerIndex].textContent.trim();
        const bValue = b.children[headerIndex].textContent.trim();
        
        // Check if it's a number
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return isAscending ? 
                parseFloat(bValue) - parseFloat(aValue) : 
                parseFloat(aValue) - parseFloat(bValue);
        }
        
        // Otherwise sort as strings
        return isAscending ? 
            bValue.localeCompare(aValue) : 
            aValue.localeCompare(bValue);
    });
    
    // Remove existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Add sorted rows
    rows.forEach(row => {
        tbody.appendChild(row);
    });
} 