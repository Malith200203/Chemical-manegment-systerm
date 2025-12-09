// Laboratory Chemical Management System - JavaScript

// Utility Functions
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }, 300));
    }
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Delete chemical confirmation
function deleteChemical(id, name) {
    if (confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
        fetch(`/api/chemicals/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                setTimeout(() => {
                    window.location.href = '/inventory';
                }, 1500);
            } else {
                showAlert(data.error || 'Failed to delete chemical', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error deleting chemical: ' + error.message, 'danger');
        });
    }
}

// Form validation
function validateChemicalForm(form) {
    const name = form.querySelector('[name="name"]').value.trim();
    const formula = form.querySelector('[name="chemical_formula"]').value.trim();
    
    if (!name) {
        showAlert('Chemical name is required', 'danger');
        return false;
    }
    
    if (!formula) {
        showAlert('Chemical formula is required', 'danger');
        return false;
    }
    
    return true;
}

// Submit chemical form
function handleChemicalForm(event, isEdit = false) {
    event.preventDefault();
    
    const form = event.target;
    if (!validateChemicalForm(form)) {
        return;
    }
    
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        // Convert empty strings to null
        data[key] = value === '' ? null : value;
        
        // Convert numeric fields
        if (key === 'molecular_weight' || key === 'hazard_category_id') {
            data[key] = value ? parseFloat(value) : null;
        }
    });
    
    const method = isEdit ? 'PUT' : 'POST';
    const chemicalId = form.dataset.chemicalId;
    const url = isEdit ? `/api/chemicals/${chemicalId}` : '/api/chemicals';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                if (isEdit) {
                    window.location.href = `/chemical/${chemicalId}`;
                } else {
                    window.location.href = '/inventory';
                }
            }, 1500);
        } else {
            showAlert(data.error || 'Failed to save chemical', 'danger');
        }
    })
    .catch(error => {
        showAlert('Error saving chemical: ' + error.message, 'danger');
    });
}

// Update inventory quantity
function updateQuantity(inventoryId) {
    const quantity = prompt('Enter new quantity:');
    if (quantity !== null && quantity !== '') {
        fetch(`/api/inventory/${inventoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantity: parseFloat(quantity) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showAlert(data.error || 'Failed to update quantity', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error updating quantity: ' + error.message, 'danger');
        });
    }
}

// Delete inventory item
function deleteInventoryItem(inventoryId) {
    if (confirm('Are you sure you want to delete this inventory item?')) {
        fetch(`/api/inventory/${inventoryId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showAlert(data.error || 'Failed to delete item', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error deleting item: ' + error.message, 'danger');
        });
    }
}

// Add inventory item
function addInventoryItem(chemicalId) {
    // This would open a modal or redirect to a form
    // For simplicity, using prompt
    const quantity = prompt('Enter quantity:');
    const unit = prompt('Enter unit (L, kg, g, ml):');
    const batchNumber = prompt('Enter batch number:');
    
    if (quantity && unit) {
        const data = {
            chemical_id: chemicalId,
            quantity: parseFloat(quantity),
            unit: unit,
            batch_number: batchNumber || null,
            storage_location_id: null,
            expiry_date: null,
            received_date: new Date().toISOString().split('T')[0],
            cost: null,
            notes: null
        };
        
        fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showAlert(data.error || 'Failed to add inventory item', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error adding inventory item: ' + error.message, 'danger');
        });
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Check expiry dates and highlight
function checkExpiryDates() {
    const today = new Date();
    const thirtyDaysFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
    
    document.querySelectorAll('[data-expiry]').forEach(element => {
        const expiryDate = new Date(element.dataset.expiry);
        
        if (expiryDate < today) {
            element.classList.add('badge-danger');
            element.textContent = 'EXPIRED';
        } else if (expiryDate < thirtyDaysFromNow) {
            element.classList.add('badge-warning');
            element.textContent = 'Expiring Soon';
        } else {
            element.classList.add('badge-success');
            element.textContent = 'Valid';
        }
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

// Highlight active navigation
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Sort table
function sortTable(columnIndex) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Try to compare as numbers first
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }
        
        // Otherwise compare as strings
        return aValue.localeCompare(bValue);
    });
    
    // Remove existing rows
    rows.forEach(row => row.remove());
    
    // Append sorted rows
    sortedRows.forEach(row => tbody.appendChild(row));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    checkExpiryDates();
    highlightActiveNav();
    
    // Add click handlers to sortable headers
    document.querySelectorAll('th[data-sortable]').forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => sortTable(index));
    });
});

// Export functions for use in HTML
window.deleteChemical = deleteChemical;
window.handleChemicalForm = handleChemicalForm;
window.updateQuantity = updateQuantity;
window.deleteInventoryItem = deleteInventoryItem;
window.addInventoryItem = addInventoryItem;
