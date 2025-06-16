// Educational Form Generator - Form Builder JavaScript

class FormBuilder {
    constructor() {
        this.fieldCounter = 0;
        this.mandatoryFields = [
            { name: 'name', type: 'text', label: 'Full Name', required: true },
            { name: 'email', type: 'email', label: 'Email Address', required: true },
            { name: 'whatsapp_number', type: 'tel', label: 'WhatsApp Number', required: true }
        ];
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateFieldNames();
    }

    bindEvents() {
        // Event delegation for dynamic elements
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('field-type')) {
                this.handleFieldTypeChange(e.target);
            }
            if (e.target.classList.contains('field-label')) {
                this.updateFieldName(e.target);
            }
        });

        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('field-label') || 
                e.target.classList.contains('field-type') || 
                e.target.classList.contains('field-required') ||
                e.target.classList.contains('field-options')) {
                this.updatePreview();
            }
        });
    }

    handleFieldTypeChange(selectElement) {
        const fieldItem = selectElement.closest('.field-item');
        const cardBody = selectElement.closest('.card-body');
        
        // Remove existing options textarea
        const existingOptions = cardBody.querySelector('.field-options');
        if (existingOptions) {
            existingOptions.closest('.mt-2').remove();
        }

        // Add options textarea for select fields
        if (selectElement.value === 'select') {
            const optionsContainer = document.createElement('div');
            optionsContainer.className = 'mt-2';
            optionsContainer.innerHTML = `
                <textarea class="form-control form-control-sm field-options" 
                          rows="2" 
                          placeholder="Options (one per line)">Option 1
Option 2
Option 3</textarea>
            `;
            
            const row = selectElement.closest('.row');
            row.parentNode.insertBefore(optionsContainer, row.nextSibling);
        }

        this.updatePreview();
    }

    updateFieldName(labelInput) {
        const fieldItem = labelInput.closest('.field-item');
        const fieldNameInput = fieldItem.querySelector('.field-name');
        
        // Generate field name from label
        const fieldName = this.generateFieldName(labelInput.value);
        fieldNameInput.value = fieldName;
    }

    generateFieldName(label) {
        return label.toLowerCase()
                   .replace(/[^a-z0-9\s]/g, '')
                   .replace(/\s+/g, '_')
                   .substring(0, 50) || `field_${++this.fieldCounter}`;
    }

    addCustomField() {
        const customFieldsContainer = document.getElementById('customFields');
        const fieldTemplate = document.getElementById('fieldTemplate');
        
        if (!customFieldsContainer || !fieldTemplate) {
            console.error('Required elements not found');
            return;
        }

        // Clone template
        const newField = fieldTemplate.cloneNode(true);
        newField.removeAttribute('id');
        newField.classList.remove('d-none');
        
        // Set unique field name
        const fieldNameInput = newField.querySelector('.field-name');
        fieldNameInput.value = `custom_field_${++this.fieldCounter}`;
        
        // Set default label
        const labelInput = newField.querySelector('.field-label');
        labelInput.value = `Custom Field ${this.fieldCounter}`;
        labelInput.placeholder = 'Enter field label';

        // Add to container with animation
        newField.style.opacity = '0';
        newField.style.transform = 'translateY(20px)';
        customFieldsContainer.appendChild(newField);
        
        // Animate in
        setTimeout(() => {
            newField.style.transition = 'all 0.3s ease';
            newField.style.opacity = '1';
            newField.style.transform = 'translateY(0)';
        }, 50);

        // Focus on label input
        labelInput.focus();
        
        this.updatePreview();
    }

    removeField(button) {
        const fieldItem = button.closest('.field-item');
        
        // Animate out
        fieldItem.style.transition = 'all 0.3s ease';
        fieldItem.style.opacity = '0';
        fieldItem.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            fieldItem.remove();
            this.updatePreview();
        }, 300);
    }

    updateFieldNames() {
        // Update field names for all existing fields
        document.querySelectorAll('.field-label').forEach(labelInput => {
            if (!labelInput.closest('.field-item').querySelector('.field-name').value) {
                this.updateFieldName(labelInput);
            }
        });
    }

    collectFormData() {
        const title = document.getElementById('formTitle').value;
        const description = document.getElementById('formDescription').value;
        const maxSubmissions = document.getElementById('maxSubmissions').value;
        const templateType = document.getElementById('templateType').value;

        // Collect all fields
        const fields = [];
        
        // Add template fields
        document.querySelectorAll('#templateFields .field-item').forEach(item => {
            const field = this.extractFieldData(item);
            if (field) fields.push(field);
        });

        // Add custom fields
        document.querySelectorAll('#customFields .field-item').forEach(item => {
            const field = this.extractFieldData(item);
            if (field) fields.push(field);
        });

        return {
            title,
            description,
            max_submissions: parseInt(maxSubmissions) || 40,
            template_type: templateType,
            fields
        };
    }

    extractFieldData(fieldItem) {
        const label = fieldItem.querySelector('.field-label').value.trim();
        const type = fieldItem.querySelector('.field-type').value;
        const required = fieldItem.querySelector('.field-required').checked;
        const name = fieldItem.querySelector('.field-name').value;

        if (!label) return null;

        const field = { name, type, label, required };

        // Add options for select fields
        if (type === 'select') {
            const optionsTextarea = fieldItem.querySelector('.field-options');
            if (optionsTextarea) {
                const options = optionsTextarea.value
                    .split('\n')
                    .map(option => option.trim())
                    .filter(option => option.length > 0);
                field.options = options;
            }
        }

        return field;
    }

    updatePreview() {
        const preview = document.getElementById('formPreview');
        if (!preview) return;

        const formData = this.collectFormData();
        
        let previewHTML = `
            <div class="form-preview-content">
                <h4 class="text-primary mb-3">${formData.title || 'Form Title'}</h4>
                ${formData.description ? `<p class="text-muted mb-4">${formData.description}</p>` : ''}
                <form class="preview-form">
        `;

        // Add mandatory fields
        this.mandatoryFields.forEach(field => {
            previewHTML += this.generateFieldPreview(field);
        });

        // Add custom fields
        formData.fields.forEach(field => {
            previewHTML += this.generateFieldPreview(field);
        });

        previewHTML += `
                    <div class="d-grid mt-4">
                        <button type="button" class="btn btn-primary btn-lg" disabled>
                            <i class="fas fa-paper-plane me-2"></i>Submit (Preview)
                        </button>
                    </div>
                </form>
            </div>
        `;

        preview.innerHTML = previewHTML;
        preview.classList.add('has-content');
    }

    generateFieldPreview(field) {
        const required = field.required ? '<span class="text-danger">*</span>' : '';
        const placeholder = `Enter ${field.label.toLowerCase()}`;

        let input = '';
        switch (field.type) {
            case 'textarea':
                input = `<textarea class="form-control" placeholder="${placeholder}" disabled></textarea>`;
                break;
            case 'select':
                const options = field.options ? 
                    field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('') : 
                    '<option>Option 1</option><option>Option 2</option>';
                input = `<select class="form-select" disabled>
                    <option value="">Choose ${field.label.toLowerCase()}</option>
                    ${options}
                </select>`;
                break;
            case 'checkbox':
                input = `<div class="form-check">
                    <input type="checkbox" class="form-check-input" disabled>
                    <label class="form-check-label">${field.label}</label>
                </div>`;
                break;
            case 'number':
                input = `<input type="number" class="form-control" placeholder="${placeholder}" disabled>`;
                break;
            case 'date':
                input = `<input type="date" class="form-control" disabled>`;
                break;
            case 'tel':
                input = `<input type="tel" class="form-control" placeholder="${placeholder}" disabled>`;
                break;
            case 'url':
                input = `<input type="url" class="form-control" placeholder="https://example.com" disabled>`;
                break;
            case 'email':
                input = `<input type="email" class="form-control" placeholder="${placeholder}" disabled>`;
                break;
            default:
                input = `<input type="text" class="form-control" placeholder="${placeholder}" disabled>`;
        }

        if (field.type === 'checkbox') {
            return `<div class="mb-3">${input}</div>`;
        }

        return `
            <div class="mb-3">
                <label class="form-label fw-semibold">${field.label} ${required}</label>
                ${input}
            </div>
        `;
    }

    previewForm() {
        const formData = this.collectFormData();
        
        if (!formData.title.trim()) {
            this.showAlert('Please enter a form title', 'warning');
            document.getElementById('formTitle').focus();
            return;
        }

        // Update preview with animation
        this.updatePreview();
        
        // Scroll to preview
        const preview = document.getElementById('formPreview');
        if (preview) {
            preview.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Add highlight effect
            preview.style.border = '3px solid var(--success-color)';
            setTimeout(() => {
                preview.style.border = '';
            }, 2000);
        }

        this.showAlert('Form preview updated successfully!', 'success');
    }

    resetForm() {
        if (!confirm('Are you sure you want to reset the form? All changes will be lost.')) {
            return;
        }

        // Reset basic fields
        document.getElementById('formTitle').value = document.getElementById('formTitle').defaultValue;
        document.getElementById('formDescription').value = '';
        document.getElementById('maxSubmissions').value = '40';

        // Remove custom fields
        const customFields = document.getElementById('customFields');
        if (customFields) {
            customFields.innerHTML = '';
        }

        // Reset template fields to default
        document.querySelectorAll('#templateFields .field-item').forEach(item => {
            const labelInput = item.querySelector('.field-label');
            const typeSelect = item.querySelector('.field-type');
            const requiredCheck = item.querySelector('.field-required');
            
            labelInput.value = labelInput.defaultValue || '';
            typeSelect.value = typeSelect.defaultValue || 'text';
            requiredCheck.checked = requiredCheck.defaultChecked;
            
            // Remove options if any
            const optionsContainer = item.querySelector('.field-options')?.closest('.mt-2');
            if (optionsContainer) {
                optionsContainer.remove();
            }
        });

        this.fieldCounter = 0;
        this.updatePreview();
        this.showAlert('Form has been reset to defaults', 'info');
    }

    showAlert(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
        
        const iconClass = {
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'danger': 'fa-times-circle',
            'info': 'fa-info-circle'
        }[type] || 'fa-info-circle';

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${iconClass} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    }

    validateForm() {
        const formData = this.collectFormData();
        const errors = [];

        if (!formData.title.trim()) {
            errors.push('Form title is required');
        }

        if (formData.max_submissions < 1 || formData.max_submissions > 1000) {
            errors.push('Maximum submissions must be between 1 and 1000');
        }

        // Validate field names are unique
        const fieldNames = formData.fields.map(f => f.name);
        const duplicateNames = fieldNames.filter((name, index) => fieldNames.indexOf(name) !== index);
        if (duplicateNames.length > 0) {
            errors.push(`Duplicate field names found: ${duplicateNames.join(', ')}`);
        }

        // Validate select fields have options
        formData.fields.forEach(field => {
            if (field.type === 'select' && (!field.options || field.options.length === 0)) {
                errors.push(`Select field "${field.label}" must have at least one option`);
            }
        });

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Drag and drop functionality
    enableSortable() {
        const templateFields = document.getElementById('templateFields');
        const customFields = document.getElementById('customFields');

        if (typeof Sortable !== 'undefined') {
            // Enable sorting for template fields
            new Sortable(templateFields, {
                group: 'form-fields',
                animation: 150,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                onEnd: () => this.updatePreview()
            });

            // Enable sorting for custom fields
            new Sortable(customFields, {
                group: 'form-fields',
                animation: 150,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                onEnd: () => this.updatePreview()
            });
        }
    }

    // Export form configuration
    exportFormConfig() {
        const formData = this.collectFormData();
        const dataStr = JSON.stringify(formData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `${formData.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_config.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    // Import form configuration
    importFormConfig(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const config = JSON.parse(e.target.result);
                this.loadFormConfig(config);
                this.showAlert('Form configuration imported successfully!', 'success');
            } catch (error) {
                this.showAlert('Invalid configuration file', 'danger');
            }
        };
        reader.readAsText(file);
    }

    loadFormConfig(config) {
        // Load basic form data
        document.getElementById('formTitle').value = config.title || '';
        document.getElementById('formDescription').value = config.description || '';
        document.getElementById('maxSubmissions').value = config.max_submissions || 40;

        // Clear existing custom fields
        const customFields = document.getElementById('customFields');
        if (customFields) {
            customFields.innerHTML = '';
        }

        // Load custom fields
        if (config.fields && config.fields.length > 0) {
            config.fields.forEach(fieldConfig => {
                this.addFieldFromConfig(fieldConfig);
            });
        }

        this.updatePreview();
    }

    addFieldFromConfig(fieldConfig) {
        this.addCustomField();
        
        // Get the last added field
        const customFields = document.getElementById('customFields');
        const lastField = customFields.lastElementChild;
        
        if (lastField) {
            lastField.querySelector('.field-label').value = fieldConfig.label || '';
            lastField.querySelector('.field-type').value = fieldConfig.type || 'text';
            lastField.querySelector('.field-required').checked = fieldConfig.required || false;
            lastField.querySelector('.field-name').value = fieldConfig.name || '';

            // Handle select field options
            if (fieldConfig.type === 'select' && fieldConfig.options) {
                this.handleFieldTypeChange(lastField.querySelector('.field-type'));
                const optionsTextarea = lastField.querySelector('.field-options');
                if (optionsTextarea) {
                    optionsTextarea.value = fieldConfig.options.join('\n');
                }
            }
        }
    }
}

// Global functions for template usage
function initializeFormBuilder() {
    window.formBuilder = new FormBuilder();
    
    // Enable sortable if library is available
    if (typeof Sortable !== 'undefined') {
        window.formBuilder.enableSortable();
    }
}

function addCustomField() {
    if (window.formBuilder) {
        window.formBuilder.addCustomField();
    }
}

function removeField(button) {
    if (window.formBuilder) {
        window.formBuilder.removeField(button);
    }
}

function previewForm() {
    if (window.formBuilder) {
        window.formBuilder.previewForm();
    }
}

function resetForm() {
    if (window.formBuilder) {
        window.formBuilder.resetForm();
    }
}

function updatePreview() {
    if (window.formBuilder) {
        window.formBuilder.updatePreview();
    }
}

function collectFormData() {
    if (window.formBuilder) {
        return window.formBuilder.collectFormData();
    }
    return null;
}

// Utility functions
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy to clipboard', 'danger');
    }
    document.body.removeChild(textArea);
}

function showToast(message, type = 'info') {
    if (window.formBuilder) {
        window.formBuilder.showAlert(message, type);
    }
}

// Auto-save functionality (optional)
class AutoSave {
    constructor(formBuilder) {
        this.formBuilder = formBuilder;
        this.saveKey = 'eduform_autosave';
        this.saveInterval = 30000; // 30 seconds
        this.init();
    }

    init() {
        // Load auto-saved data on page load
        this.loadAutoSave();
        
        // Set up auto-save interval
        setInterval(() => {
            this.autoSave();
        }, this.saveInterval);

        // Save on page unload
        window.addEventListener('beforeunload', () => {
            this.autoSave();
        });
    }

    autoSave() {
        if (this.formBuilder) {
            const formData = this.formBuilder.collectFormData();
            if (formData.title || formData.description || formData.fields.length > 0) {
                localStorage.setItem(this.saveKey, JSON.stringify({
                    data: formData,
                    timestamp: Date.now()
                }));
            }
        }
    }

    loadAutoSave() {
        const saved = localStorage.getItem(this.saveKey);
        if (saved) {
            try {
                const { data, timestamp } = JSON.parse(saved);
                const age = Date.now() - timestamp;
                
                // Only load if less than 24 hours old
                if (age < 24 * 60 * 60 * 1000) {
                    if (confirm('Auto-saved form data found. Would you like to restore it?')) {
                        this.formBuilder.loadFormConfig(data);
                    }
                }
            } catch (error) {
                console.error('Error loading auto-saved data:', error);
            }
        }
    }

    clearAutoSave() {
        localStorage.removeItem(this.saveKey);
    }
}

// Initialize auto-save when form builder is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.formBuilder) {
        window.autoSave = new AutoSave(window.formBuilder);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormBuilder, AutoSave };
}
