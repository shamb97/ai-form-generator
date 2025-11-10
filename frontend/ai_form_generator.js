/**
 * AI Form Generator - Chat Interface
 * Handles communication with Form Designer Agent
 */

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const suggestions = document.getElementById('suggestions');

// State
let conversationHistory = [];
let currentFormSchema = null;
let conversationMode = 'create'; // 'create' or 'refine'

// API Configuration
const API_BASE = 'http://localhost:8000';

// Add CSS animation for save confirmation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);

/**
 * Initialize the chat interface
 */
function init() {
    // Send button click
    sendButton.addEventListener('click', handleSendMessage);
    
    // Enter key in input
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chatInput.value = chip.dataset.text;
            chatInput.focus();
        });
    });
    
    console.log('🤖 AI Form Generator initialized');
}

/**
 * Handle sending a message
 */
async function handleSendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input while processing
    setInputState(false);
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    chatInput.value = '';
    
    // Show loading
    showLoading(true);
    
    // Call AI agent based on mode
    try {
        let response;
        
        if (conversationMode === 'refine' && currentFormSchema) {
            // Refining existing form
            response = await callRefineFormAgent(currentFormSchema, message);
        } else {
            // Creating new form
            conversationMode = 'create';
            response = await callFormDesignerAgent(message);
        }
        
        if (response.success) {
            // Store the form schema
            currentFormSchema = response.form_schema;
            
            // Add AI response with form preview
            addFormMessage(response.form_schema);
            
            // Switch to create mode for next message
            conversationMode = 'create';
            updateInputPlaceholder('create');
            
        } else {
            addMessage('ai', `❌ Error: ${response.error || 'Failed to generate form'}`);
        }
        
    } catch (error) {
        console.error('Error calling agent:', error);
        addMessage('ai', `❌ Error: ${error.message}`);
    } finally {
        showLoading(false);
        setInputState(true);
    }
}

/**
 * Call the Form Designer Agent API
 */
async function callFormDesignerAgent(description) {
    const response = await fetch(`${API_BASE}/api/v1/ai/design-form`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            description: description
        })
    });
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Call the Form Refine Agent API
 */
async function callRefineFormAgent(formSchema, refinement) {
    const response = await fetch(`${API_BASE}/api/v1/ai/refine-form`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            form_schema: formSchema,
            refinement: refinement
        })
    });
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Add a text message to the chat
 */
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = role === 'user' ? '👤 You' : '🤖 Form Designer Agent';
    
    const text = document.createElement('div');
    text.innerHTML = formatMessage(content);
    
    contentDiv.appendChild(label);
    contentDiv.appendChild(text);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add a form preview message
 */
function addFormMessage(formSchema) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.style.maxWidth = '90%';
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = '🤖 Form Designer Agent';
    
    const text = document.createElement('div');
    text.innerHTML = `
        <p><strong>✅ Form Created Successfully!</strong></p>
        <p>I've designed a form based on your description.</p>
    `;
    
    contentDiv.appendChild(label);
    contentDiv.appendChild(text);

    // Then add form preview - pass FULL schema for buttons to use
    const preview = createFormPreview(formSchema.form_schema || formSchema, formSchema);
    contentDiv.appendChild(preview);

    // Then metadata disclosure panel
    const metadataPanel = createMetadataPanel(formSchema);
    contentDiv.appendChild(metadataPanel);

    // Finally data model specification section
    const dataModelSection = createDataModelSection(formSchema);
    contentDiv.appendChild(dataModelSection);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Create metadata transparency disclosure panel
 */
function createMetadataPanel(schema) {
    const panel = document.createElement('div');
    panel.className = 'metadata-panel';
    panel.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    const metadata = schema.metadata_suggestions || {};
    const classification = schema.study_classification || {};
    
    panel.innerHTML = `
        <h3 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
            📊 Data Collection Transparency
        </h3>
        <p style="margin: 0 0 15px 0; opacity: 0.9; font-size: 14px;">
            Study Type: <strong>${classification.study_type || 'unknown'}</strong> | 
            Metadata Level: <strong>Tier ${classification.recommended_tier || 1}</strong>
        </p>
        <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px;">
            ${createMetadataSection('Required (Always Captured)', metadata.required || [], 'required', schema)}
            ${createMetadataSection('Recommended for Your Study', metadata.recommended || [], 'recommended', schema)}
            ${createMetadataSection('Optional (Your Choice)', metadata.optional || [], 'optional', schema)}
        </div>
    `;
    
    return panel;
}

/**
 * Create a metadata section (required/recommended/optional)
 */
function createMetadataSection(title, items, type, schema) {
    if (!items || items.length === 0) {
        return '';
    }
    
    const icon = type === 'required' ? '✓' : type === 'recommended' ? '☑' : '☐';
    const itemsHtml = items.map((item, index) => `
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            border-left: 3px solid ${type === 'required' ? '#4ade80' : type === 'recommended' ? '#fbbf24' : '#94a3b8'};
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 16px;">${icon}</span>
                <strong style="flex: 1;">${item.field || 'Unknown Field'}</strong>
                ${type === 'recommended' || type === 'optional' ? `
                    <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                        <input type="checkbox" 
                               id="metadata_${type}_${index}" 
                               class="metadata-toggle"
                               data-metadata-type="${type}"
                               data-metadata-field="${item.field}"
                               data-metadata-index="${index}"
                               style="cursor: pointer;" 
                               onchange="handleMetadataToggle()"
                               ${type === 'recommended' ? 'checked' : ''}>
                        <span style="font-size: 12px;">Enable</span>
                    </label>
                ` : ''}
            </div>
            <div style="font-size: 13px; opacity: 0.9; margin-left: 24px;">
                <div>📌 <strong>Why:</strong> ${item.why || 'Not specified'}</div>
                <div>⚙️ <strong>How:</strong> ${item.how || 'Not specified'}</div>
                ${item.example ? `<div>💡 <strong>Example:</strong> ${item.example}</div>` : ''}
                ${item.privacy ? `<div>🔒 <strong>Privacy:</strong> ${item.privacy}</div>` : ''}
            </div>
        </div>
    `).join('');
    
    return `
        <div style="margin: 15px 0;">
            <h4 style="margin: 0 0 10px 0; font-size: 15px; opacity: 0.95;">
                ${title}
            </h4>
            ${itemsHtml}
        </div>
    `;
}

/**
 * Handle metadata checkbox toggle
 */
function handleMetadataToggle() {
    // Find the data model section and update it
    const dataModelSection = document.querySelector('.data-model-section');
    if (dataModelSection && currentFormSchema) {
        // Get the parent message div
        const messageDiv = dataModelSection.closest('.message');
        
        // Recreate the data model section
        const newDataModelSection = createDataModelSection(currentFormSchema);
        dataModelSection.replaceWith(newDataModelSection);
    }
}

/**
 * Determine metadata capture feasibility from "how" text
 */
function getCaptureFeasibility(howText) {
    if (!howText) return { type: 'unknown', icon: '❓', color: '#94a3b8' };
    
    const autoKeywords = ['auto', 'automatic', 'calculated', 'detected', 'system', 'capture'];
    const manualKeywords = ['user', 'manual', 'researcher', 'select', 'enter', 'input', 'choose'];
    
    const lower = howText.toLowerCase();
    
    if (autoKeywords.some(kw => lower.includes(kw))) {
        return { type: 'automatic', icon: '🤖', color: '#4ade80' };
    }
    if (manualKeywords.some(kw => lower.includes(kw))) {
        return { type: 'manual', icon: '👤', color: '#fbbf24' };
    }
    return { type: 'unknown', icon: '❓', color: '#94a3b8' };
}

/**
 * Check if metadata item is enabled
 */
function isMetadataEnabled(type, index) {
    const checkbox = document.querySelector(`#metadata_${type}_${index}`);
    return checkbox ? checkbox.checked : (type === 'required' || type === 'recommended');
}

/**
 * Create data model specification section showing all database fields
 */
function createDataModelSection(schema) {
    const section = document.createElement('div');
    section.className = 'data-model-section';
    section.style.cssText = `
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    const metadata = schema.metadata_suggestions || {};
    const formSchema = schema.form_schema || schema;
    const fields = formSchema.fields || [];
    
    // Collect all metadata fields with their types
    const allMetadata = [
        ...(metadata.required || []).map((item, idx) => ({ ...item, type: 'required', index: idx })),
        ...(metadata.recommended || []).map((item, idx) => ({ ...item, type: 'recommended', index: idx })),
        ...(metadata.optional || []).map((item, idx) => ({ ...item, type: 'optional', index: idx }))
    ];
    
    section.innerHTML = `
        <h3 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
            🗄️ Data Model Specification
        </h3>
        <p style="margin: 0 0 15px 0; opacity: 0.9; font-size: 14px;">
            Review database structure and customize field names before finalizing
        </p>
        
        <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px;">
            <!-- Metadata Fields -->
            <div style="margin-bottom: 20px;">
                <h4 style="margin: 0 0 10px 0; font-size: 15px; opacity: 0.95;">
                    📊 Metadata Fields (System-Generated)
                </h4>
                <div style="background: rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                    ${allMetadata.map((item) => {
                        const enabled = isMetadataEnabled(item.type, item.index);
                        const feasibility = getCaptureFeasibility(item.how);
                        const opacity = enabled ? '1' : '0.4';
                        const disabledText = enabled ? '' : ' (disabled)';
                        
                        return `
                        <div style="
                            display: flex;
                            align-items: center;
                            padding: 8px;
                            margin: 4px 0;
                            background: rgba(255,255,255,0.05);
                            border-radius: 4px;
                            opacity: ${opacity};
                        ">
                            <input 
                                type="text" 
                                value="${item.field}"
                                data-metadata-type="${item.type}"
                                data-metadata-index="${item.index}"
                                class="metadata-name-input"
                                ${!enabled ? 'disabled' : ''}
                                style="
                                    flex: 1;
                                    background: rgba(255,255,255,0.2);
                                    border: 1px solid rgba(255,255,255,0.3);
                                    color: #ffd700;
                                    padding: 6px 10px;
                                    border-radius: 4px;
                                    font-family: 'Courier New', monospace;
                                    font-size: 13px;
                                "
                                placeholder="field_name"
                            />
                            <span style="
                                padding: 2px 8px;
                                background: ${feasibility.color};
                                border-radius: 4px;
                                font-size: 18px;
                                margin-left: 10px;
                                min-width: 35px;
                                text-align: center;
                                " title="${feasibility.type}">${feasibility.icon}</span>
                            ${!enabled ? `<span style="
                                padding: 2px 8px;
                                background: rgba(255,255,255,0.2);
                                border-radius: 4px;
                                font-size: 11px;
                                margin-left: 5px;
                            ">disabled</span>` : ''}
                        </div>
                    `}).join('')}
                </div>
                <div style="
                    margin-top: 10px;
                    padding: 8px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    font-size: 11px;
                    opacity: 0.9;
                ">
                    <strong>Legend:</strong> 
                    🤖 = Automatic capture | 
                    👤 = User input required | 
                    ❓ = Unknown method
                </div>
            </div>
            
            <!-- Form Fields -->
            <div>
                <h4 style="margin: 0 0 10px 0; font-size: 15px; opacity: 0.95;">
                    📝 Form Fields (Editable)
                </h4>
                <div style="background: rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                    ${fields.map((field, index) => {
                        const fieldId = field.field_id || field.field_name?.toLowerCase().replace(/\s+/g, '_') || `field_${index}`;
                        const fieldType = field.field_type || field.type || 'text';
                        const dataType = getDataType(fieldType);
                        
                        return `
                        <div style="
                            display: flex;
                            align-items: center;
                            padding: 8px;
                            margin: 4px 0;
                            background: rgba(255,255,255,0.05);
                            border-radius: 4px;
                        ">
                            <input 
                                type="text" 
                                value="${fieldId}"
                                data-field-index="${index}"
                                class="field-name-input"
                                style="
                                    flex: 1;
                                    background: rgba(255,255,255,0.2);
                                    border: 1px solid rgba(255,255,255,0.3);
                                    color: white;
                                    padding: 6px 10px;
                                    border-radius: 4px;
                                    font-family: 'Courier New', monospace;
                                    font-size: 13px;
                                "
                                placeholder="field_name"
                            />
                            <span style="
                                padding: 2px 8px;
                                background: rgba(255,255,255,0.2);
                                border-radius: 4px;
                                font-size: 11px;
                                margin-left: 10px;
                                min-width: 60px;
                                text-align: center;
                            ">${dataType}</span>
                            <span style="
                                margin-left: 10px;
                                font-size: 12px;
                                opacity: 0.8;
                            ">${field.field_name || field.label || 'Field'}</span>
                        </div>
                    `}).join('')}
                </div>
            </div>
            
            <div style="
                margin-top: 15px;
                padding: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 12px;
                opacity: 0.9;
            ">
                💡 <strong>Tip:</strong> Edit field names to match your database conventions. 
                Use snake_case (e.g., water_intake_ml) for best compatibility.
            </div>
        </div>
    `;
    
    // Add event listeners for field name changes
    setTimeout(() => {
        // Form field inputs
        const formInputs = section.querySelectorAll('.field-name-input');
        formInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const fieldIndex = parseInt(e.target.dataset.fieldIndex);
                const rawValue = e.target.value.trim();
                let cleanedName = rawValue.toLowerCase().replace(/\s+/g, '_');
                
                // Validate the cleaned name
                if (validateFieldName(cleanedName, e.target)) {
                    // Update the field name in the schema
                    // Handle both nested and flat schema structures
                    const schema = currentFormSchema.form_schema || currentFormSchema;
                    if (schema && schema.fields) {
                        schema.fields[fieldIndex].field_id = cleanedName;
                        
                        // Update the input to show cleaned value
                        e.target.value = cleanedName;
                        
                        // Show different message if we auto-corrected
                        if (rawValue !== cleanedName) {
                            showSaveConfirmation(e.target, `Auto-corrected to: ${cleanedName}`);
                        } else {
                            showSaveConfirmation(e.target, 'Form field updated');
                        }
                        console.log(`✏️ Updated form field ${fieldIndex} to: ${cleanedName}`);
                    }
                } else {
                    // Validation failed - revert to original value
                    const schema = currentFormSchema.form_schema || currentFormSchema;
                    e.target.value = schema?.fields[fieldIndex]?.field_id || '';                }
            });
        });
        
        // Metadata field inputs
        const metadataInputs = section.querySelectorAll('.metadata-name-input:not([disabled])');
        metadataInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const metadataType = e.target.dataset.metadataType;
                const metadataIndex = parseInt(e.target.dataset.metadataIndex);
                const rawValue = e.target.value.trim();
                let cleanedName = rawValue.toLowerCase().replace(/\s+/g, '_');
                
                // Validate the cleaned name
                if (validateFieldName(cleanedName, e.target)) {
                    // Update the input to show cleaned value
                    e.target.value = cleanedName;
                    
                    // Show different message if we auto-corrected
                    if (rawValue !== cleanedName) {
                        showSaveConfirmation(e.target, `Auto-corrected to: ${cleanedName}`);
                    } else {
                        showSaveConfirmation(e.target, 'Metadata field updated');
                    }
                    console.log(`✏️ Updated metadata field ${metadataType}[${metadataIndex}] to: ${cleanedName}`);
                } else {
                    // Validation failed - revert to original value
                    const allMeta = [
                        ...(schema.metadata_suggestions?.required || []).map(item => ({ ...item, type: 'required' })),
                        ...(schema.metadata_suggestions?.recommended || []).map(item => ({ ...item, type: 'recommended' })),
                        ...(schema.metadata_suggestions?.optional || []).map(item => ({ ...item, type: 'optional' }))
                    ];
                    const original = allMeta.find(m => m.type === metadataType);
                    e.target.value = original?.field || '';
                }
            });
        });
    }, 100);
    
    // VALIDATION FUNCTIONS 
    function validateFieldName(fieldName, inputElement) {
        const errors = [];
        
        // Rule 1: Must not be empty
        if (!fieldName || fieldName.trim() === '') {
            errors.push('Field name cannot be empty');
        }
        
        // Rule 2: Only lowercase letters, numbers, underscores
        if (!/^[a-z_][a-z0-9_]*$/.test(fieldName)) {
            errors.push('Use only lowercase letters, numbers, and underscores');
        }
        
        // Rule 3: Must start with letter or underscore
        if (fieldName && !/^[a-z_]/.test(fieldName)) {
            errors.push('Must start with a letter or underscore');
        }
        
        // Rule 4: Max length 64 characters
        if (fieldName.length > 64) {
            errors.push('Maximum 64 characters');
        }
        
        // Rule 5: Check for SQL reserved keywords
        const sqlKeywords = ['select', 'insert', 'update', 'delete', 'drop', 'create', 
                             'alter', 'table', 'from', 'where', 'order', 'group'];
        if (sqlKeywords.includes(fieldName.toLowerCase())) {
            errors.push('Cannot use SQL reserved keyword');
        }
        
        // Show errors or success
        if (errors.length > 0) {
            showValidationError(inputElement, errors);
            return false;
        } else {
            showValidationSuccess(inputElement);
            return true;
        }
    }
    
    function showValidationError(element, errors) {
        // Preserve original color, just change border and add light red tint
        const isMetadata = element.classList.contains('metadata-name-input');
        const textColor = isMetadata ? '#ffd700' : 'white';
        
        element.style.border = '2px solid #ef4444';
        element.style.background = 'rgba(239, 68, 68, 0.15)';
        element.style.color = textColor; // Keep text visible!
        
        // Create error message
        const errorMsg = document.createElement('div');
        errorMsg.innerHTML = `
            <div style="
                position: absolute;
                background: #ef4444;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
                margin-top: 4px;
                z-index: 1000;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                max-width: 250px;
            ">
                ❌ ${errors.join('<br>❌ ')}
            </div>
        `;
        
        element.parentElement.style.position = 'relative';
        
        // Remove any existing error
        const existing = element.parentElement.querySelector('.validation-error');
        if (existing) existing.remove();
        
        errorMsg.className = 'validation-error';
        element.parentElement.appendChild(errorMsg);
    }
    
    function showValidationSuccess(element) {
        // Preserve original color, just change border and add light green tint
        const isMetadata = element.classList.contains('metadata-name-input');
        const textColor = isMetadata ? '#ffd700' : 'white';
        
        element.style.border = '2px solid #4ade80';
        element.style.background = 'rgba(74, 222, 128, 0.15)';
        element.style.color = textColor; // Keep text visible!
        
        // Remove any existing error
        const existing = element.parentElement.querySelector('.validation-error');
        if (existing) existing.remove();
        
        // Reset after 2 seconds
        setTimeout(() => {
            element.style.border = '1px solid rgba(255,255,255,0.3)';
            element.style.background = 'rgba(255,255,255,0.2)';
            element.style.color = textColor;
        }, 2000);
    }

    // Helper function to show save confirmation
    function showSaveConfirmation(element, message) {
        // Change border to green briefly
        const originalBorder = element.style.border;
        element.style.border = '2px solid #4ade80';
        
        // Create floating message
        const confirmMsg = document.createElement('div');
        confirmMsg.textContent = `💾 ${message}`;
        confirmMsg.style.cssText = `
            position: absolute;
            background: #4ade80;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            pointer-events: none;
            animation: fadeInOut 2s ease;
            z-index: 1000;
        `;
        
        // Position near the input
        element.parentElement.style.position = 'relative';
        element.parentElement.appendChild(confirmMsg);
        
        // Remove after animation
        setTimeout(() => {
            element.style.border = originalBorder;
            confirmMsg.remove();
        }, 2000);
    }
    
    return section;
}

/**
 * Helper: Map field types to database data types
 */
function getDataType(fieldType) {
    const typeMap = {
        'text': 'string',
        'textarea': 'text',
        'number': 'integer',
        'scale': 'integer',
        'slider': 'integer',
        'radio': 'enum',
        'dropdown': 'enum',
        'checkbox': 'array',
        'date': 'date',
        'time': 'time',
        'datetime': 'datetime'
    };
    return typeMap[fieldType] || 'string';
}

/**
 * Create a form preview card with interactive fields
 */
function createFormPreview(schema, fullSchema = null) {
    const preview = document.createElement('div');
    preview.className = 'form-preview';
    
    preview.innerHTML = `
        <h3>📋 ${schema.form_name || schema.title || 'New Form'}</h3>
        <p style="color: #666; margin: 10px 0;">${schema.description || 'No description provided'}</p>
    `;
    
    // Create interactive form
    const formContainer = document.createElement('div');
    formContainer.style.cssText = 'background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0;';
    
    // Render each field
    schema.fields.forEach(field => {
        const fieldDiv = document.createElement('div');
        fieldDiv.style.cssText = 'margin-bottom: 20px;';
        
        // Field label
        const label = document.createElement('label');
        label.style.cssText = 'display: block; font-weight: 600; margin-bottom: 8px; color: #333;';
        label.innerHTML = `
            ${field.field_name || field.label}
            ${field.required ? '<span style="color: #dc3545;">*</span>' : ''}
        `;
        if (field.description) {
            const desc = document.createElement('div');
            desc.style.cssText = 'font-size: 0.85em; color: #666; font-weight: normal; margin-top: 4px;';
            desc.textContent = field.description;
            label.appendChild(desc);
        }
        fieldDiv.appendChild(label);
        
        // Render field based on type
        const fieldType = field.field_type || field.type;
        let input;
        
        switch(fieldType) {
            case 'text':
                input = document.createElement('input');
                input.type = 'text';
                input.placeholder = `Enter ${field.field_name || field.label}`;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                break;
                
            case 'textarea':
                input = document.createElement('textarea');
                input.placeholder = `Enter ${field.field_name || field.label}`;
                input.rows = 4;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em; font-family: inherit;';
                if (field.validation?.max_length) {
                    input.maxLength = field.validation.max_length;
                }
                break;
                
            case 'number':
                input = document.createElement('input');
                input.type = 'number';
                if (field.validation?.min !== undefined) input.min = field.validation.min;
                if (field.validation?.max !== undefined) input.max = field.validation.max;
                if (field.validation?.step !== undefined) input.step = field.validation.step;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                break;
                
            case 'scale':
            case 'slider':
                const sliderContainer = document.createElement('div');
                input = document.createElement('input');
                input.type = 'range';
                input.min = field.validation?.min || 0;
                input.max = field.validation?.max || 10;
                input.value = input.min;
                input.style.cssText = 'width: 100%; margin: 10px 0;';
                
                const valueDisplay = document.createElement('div');
                valueDisplay.style.cssText = 'text-align: center; font-size: 1.5em; font-weight: bold; color: #667eea; margin-top: 8px;';
                valueDisplay.textContent = input.value;
                
                input.addEventListener('input', (e) => {
                    valueDisplay.textContent = e.target.value;
                });
                
                const rangeLabel = document.createElement('div');
                rangeLabel.style.cssText = 'display: flex; justify-content: space-between; font-size: 0.85em; color: #666; margin-top: 4px;';
                rangeLabel.innerHTML = `<span>${input.min}</span><span>${input.max}</span>`;
                
                sliderContainer.appendChild(input);
                sliderContainer.appendChild(valueDisplay);
                sliderContainer.appendChild(rangeLabel);
                input = sliderContainer;
                break;
                
            case 'date':
                input = document.createElement('input');
                input.type = 'date';
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                break;
                
            case 'time':
                input = document.createElement('input');
                input.type = 'time';
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                break;
                
            case 'radio':
                const radioContainer = document.createElement('div');
                radioContainer.style.cssText = 'display: flex; flex-direction: column; gap: 8px;';
                (field.options || []).forEach((option, idx) => {
                    const radioDiv = document.createElement('div');
                    radioDiv.style.cssText = 'display: flex; align-items: center; gap: 8px;';
                    
                    const radio = document.createElement('input');
                    radio.type = 'radio';
                    radio.name = field.field_id || field.id;
                    radio.value = option;
                    radio.id = `${field.field_id}_${idx}`;
                    
                    const radioLabel = document.createElement('label');
                    radioLabel.htmlFor = radio.id;
                    radioLabel.textContent = option;
                    radioLabel.style.cursor = 'pointer';
                    
                    radioDiv.appendChild(radio);
                    radioDiv.appendChild(radioLabel);
                    radioContainer.appendChild(radioDiv);
                });
                input = radioContainer;
                break;
                
            case 'checkbox':
                const checkboxContainer = document.createElement('div');
                checkboxContainer.style.cssText = 'display: flex; flex-direction: column; gap: 8px;';
                (field.options || []).forEach((option, idx) => {
                    const checkDiv = document.createElement('div');
                    checkDiv.style.cssText = 'display: flex; align-items: center; gap: 8px;';
                    
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = option;
                    checkbox.id = `${field.field_id}_${idx}`;
                    
                    const checkLabel = document.createElement('label');
                    checkLabel.htmlFor = checkbox.id;
                    checkLabel.textContent = option;
                    checkLabel.style.cursor = 'pointer';
                    
                    checkDiv.appendChild(checkbox);
                    checkDiv.appendChild(checkLabel);
                    checkboxContainer.appendChild(checkDiv);
                });
                input = checkboxContainer;
                break;
                
            case 'dropdown':
                input = document.createElement('select');
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = `Select ${field.field_name || field.label}`;
                input.appendChild(defaultOption);
                
                (field.options || []).forEach(option => {
                    const opt = document.createElement('option');
                    opt.value = option;
                    opt.textContent = option;
                    input.appendChild(opt);
                });
                break;
                
            default:
                input = document.createElement('input');
                input.type = 'text';
                input.placeholder = `Enter ${field.field_name || field.label}`;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
        }
        
        if (input) {
            fieldDiv.appendChild(input);
        }
        
        formContainer.appendChild(fieldDiv);
    });
    
    preview.appendChild(formContainer);
    
    // JSON viewer (collapsed by default)
    const jsonDetails = document.createElement('details');
    jsonDetails.style.cssText = 'margin-top: 15px;';
    jsonDetails.innerHTML = `
        <summary style="cursor: pointer; font-weight: 600; color: #667eea;">View JSON Schema</summary>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; margin-top: 10px; font-size: 0.85em;">${JSON.stringify(schema, null, 2)}</pre>
    `;
    preview.appendChild(jsonDetails);
    
    // Add action buttons
    const actions = document.createElement('div');
    actions.className = 'form-actions';
    
    const approveButton = document.createElement('button');
    approveButton.className = 'action-button primary';
    approveButton.innerHTML = '✅ Approve Form + Data Configuration';
    approveButton.onclick = () => handleApproveForm(fullSchema || schema);    
    const refineButton = document.createElement('button');
    refineButton.className = 'action-button secondary';
    refineButton.innerHTML = '🔧 Request Changes';
    refineButton.onclick = () => handleRefineForm(fullSchema || schema);    
    const downloadButton = document.createElement('button');
    downloadButton.className = 'action-button secondary';
    downloadButton.innerHTML = '💾 Download JSON';
    downloadButton.onclick = () => downloadFormJSON(schema);
    
    actions.appendChild(approveButton);
    actions.appendChild(refineButton);
    actions.appendChild(downloadButton);
    
    preview.appendChild(actions);
    
    return preview;
}

/**
 * Handle approve form action
 */
function handleApproveForm(schema) {
addMessage('ai', `✅ Great! I'll save this form with your configured metadata and field names. The form "${schema.form_name || schema.title}" is ready to use!`);    
    // You could add API call here to save the form to a study
    console.log('Form approved:', schema);
    
    // Show success and ask what's next
    setTimeout(() => {
        addMessage('ai', 'Would you like to create another form, or modify this one?');
    }, 1000);
}

/**
 * Handle refine form action
 */
function handleRefineForm(schema) {
    // Switch to refine mode
    conversationMode = 'refine';
    currentFormSchema = schema;
    
    // Update placeholder
    updateInputPlaceholder('refine');
    
    // Show message
    addMessage('ai', 'Sure! What changes would you like me to make? For example:\n\n• "Add a date field that auto-populates with today\'s date"\n• "Change the pain scale to 1-5"\n• "Make the notes field optional"\n• "Add skip logic: if pain > 5, show medication field"');
    
    // Focus input
    chatInput.focus();
}

/**
 * Download form JSON
 */
function downloadFormJSON(schema) {
    const dataStr = JSON.stringify(schema, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${schema.form_id || 'form'}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    addMessage('ai', '💾 Form JSON downloaded! You can import it anytime.');
}

/**
 * Format message text
 */
function formatMessage(text) {
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Convert bullet points
    text = text.replace(/^• /gm, '&bull; ');
    
    return text;
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    loadingIndicator.classList.toggle('active', show);
    if (show) {
        scrollToBottom();
    }
}

/**
 * Enable/disable input
 */
function setInputState(enabled) {
    chatInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Update input placeholder based on mode
 */
function updateInputPlaceholder(mode) {
    if (mode === 'refine') {
        chatInput.placeholder = 'What changes would you like to make?';
    } else {
        chatInput.placeholder = 'Describe the form you want to create...';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

console.log('🚀 AI Form Generator JS loaded');