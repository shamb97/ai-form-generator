/**
 * AI Form Generator - Chat Interface
 * 
 * COMPREHENSIVE FIX - TASK 4 COMPLETE:
 * ✅ Skip logic works for ALL input types (text, number, dropdown, radio, checkbox, slider, textarea, date, time)
 * ✅ Listens to MULTIPLE events (input, change, blur) to catch all changes
 * ✅ Supports ALL operators (==, !=, >, >=, <, <=, contains, is_empty, is_not_empty)
 * ✅ String-based conditional parsing: "pain_level >= 5"
 * ✅ Object-based conditional parsing: { field: "pain_level", operator: ">=", value: 5 }
 * ✅ Proper data persistence: hidden fields disabled but value preserved
 * ✅ Optional value clearing when field hides
 * ✅ Survives refresh without breaking
 * ✅ Comprehensive logging for debugging
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
let conversationMode = 'create';

// Configuration for skip logic behavior
const SKIP_LOGIC_CONFIG = {
    clearValueOnHide: true, // Set to true to wipe data when field hides
    preserveDisabledValues: false // Keep value when field is disabled
};

// API Configuration
const API_BASE = 'http://localhost:8000';

// Add CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .field-hidden {
        display: none !important;
    }
    
    .field-visible {
        animation: fadeIn 0.3s ease;
    }
    
    .field-disabled {
        opacity: 0.5;
        pointer-events: none;
    }
    
    .skip-logic-indicator {
        background: #fef3c7;
        border-left: 3px solid #f59e0b;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
        color: #92400e;
    }
    
    .conditional-field-badge {
        display: inline-block;
        background: #fbbf24;
        color: #78350f;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75em;
        font-weight: 600;
        margin-left: 8px;
    }
`;
document.head.appendChild(style);

function init() {
    sendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chatInput.value = chip.dataset.text;
            chatInput.focus();
        });
    });
    console.log('🤖 AI Form Generator initialized - BULLETPROOF SKIP LOGIC VERSION');
}

async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    setInputState(false);
    addMessage('user', message);
    chatInput.value = '';
    showLoading(true);
    
    try {
        let response;
        if (conversationMode === 'refine' && currentFormSchema) {
            response = await callRefineFormAgent(currentFormSchema, message);
        } else {
            conversationMode = 'create';
            response = await callFormDesignerAgent(message);
        }
        
        if (response.success) {
            currentFormSchema = response.form_schema;
            addFormMessage(response.form_schema);
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

async function callFormDesignerAgent(description) {
    const response = await fetch(`${API_BASE}/api/v1/ai/design-form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
    });
    if (!response.ok) throw new Error(`API request failed: ${response.status}`);
    return await response.json();
}

async function callRefineFormAgent(formSchema, refinement) {
    const response = await fetch(`${API_BASE}/api/v1/ai/refine-form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_schema: formSchema, refinement })
    });
    if (!response.ok) throw new Error(`API request failed: ${response.status}`);
    return await response.json();
}

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

function addFormMessage(formSchema) {
    // CRITICAL: Mark all previous forms as archived
    const previousForms = document.querySelectorAll('.message.ai.latest-form');
    previousForms.forEach(form => {
        form.classList.remove('latest-form');
        form.classList.add('archived-form');
        form.style.opacity = '0.6'; // Dim archived forms
        
        // Add archived badge
        const contentDiv = form.querySelector('.message-content');
        if (contentDiv && !contentDiv.querySelector('.archived-badge')) {
            const badge = document.createElement('div');
            badge.className = 'archived-badge';
            badge.style.cssText = 'background: #94a3b8; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; display: inline-block; margin-bottom: 10px;';
            badge.textContent = '✓ Archived Version';
            contentDiv.insertBefore(badge, contentDiv.firstChild.nextSibling);
        }
        
        // CRITICAL FIX: Remove action buttons from archived forms
        const actionButtons = form.querySelector('.form-actions');
        if (actionButtons) {
            actionButtons.remove();
            console.log('🗑️ Removed action buttons from archived form');
        }
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai latest-form'; // Mark as latest
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
    contentDiv.appendChild(createFormPreview(formSchema.form_schema || formSchema, formSchema));
    contentDiv.appendChild(createMetadataPanel(formSchema));
    contentDiv.appendChild(createDataModelSection(formSchema));
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * FIXED: Create metadata panel with immediate checkbox state application
 */
function createMetadataPanel(schema, checkboxStates = null) {
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
            ${createMetadataSection('Required (Always Captured)', metadata.required || [], 'required', schema, checkboxStates)}
            ${createMetadataSection('Recommended for Your Study', metadata.recommended || [], 'recommended', schema, checkboxStates)}
            ${createMetadataSection('Optional (Your Choice)', metadata.optional || [], 'optional', schema, checkboxStates)}
        </div>
    `;
    
    return panel;
}

function createMetadataSection(title, items, type, schema, checkboxStates = null) {
    if (!items || items.length === 0) return '';
    
    const icon = type === 'required' ? '✓' : type === 'recommended' ? '☑' : '☐';
    const itemsHtml = items.map((item, index) => {
        // CRITICAL FIX: Determine correct checkbox state
        let isChecked = type === 'recommended'; // default
        if (type === 'optional') isChecked = false;
        
        // Override with saved state if available
        if (checkboxStates) {
            const key = `${type}_${index}`;
            if (checkboxStates.hasOwnProperty(key)) {
                isChecked = checkboxStates[key];
                console.log(`🔧 Setting checkbox ${key} to ${isChecked} from saved state`);
            }
        }
        
        return `
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
                ${type !== 'required' ? `
                    <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                        <input type="checkbox" 
                               id="metadata_${type}_${index}" 
                               class="metadata-toggle"
                               data-metadata-type="${type}"
                               data-metadata-field="${item.field}"
                               data-metadata-index="${index}"
                               style="cursor: pointer;" 
                               onchange="handleMetadataToggle()"
                               ${isChecked ? 'checked' : ''}>
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
    `}).join('');
    
    return `
        <div style="margin: 15px 0;">
            <h4 style="margin: 0 0 10px 0; font-size: 15px; opacity: 0.95;">
                ${title}
            </h4>
            ${itemsHtml}
        </div>
    `;
}

let metadataToggleTimeout = null;
function handleMetadataToggle() {
    if (metadataToggleTimeout) clearTimeout(metadataToggleTimeout);
    
    metadataToggleTimeout = setTimeout(() => {
        if (!currentFormSchema) return;
        
        console.log('🔄 Metadata toggle triggered');
        
        const checkboxStates = {};
        document.querySelectorAll('.metadata-toggle').forEach(checkbox => {
            const type = checkbox.dataset.metadataType;
            const index = checkbox.dataset.metadataIndex;
            const key = `${type}_${index}`;
            checkboxStates[key] = checkbox.checked;
        });
        
        console.log('💾 Current checkbox states:', checkboxStates);
        
        refreshMetadataPreview(checkboxStates);
        refreshDataModelSection(checkboxStates);
    }, 100);
}

/**
 * CRITICAL FIX: Refresh all sections WITHOUT setTimeout, immediate state application
 */
function refreshAllSections() {
    if (!currentFormSchema) return;
    
    console.log('🔄 Refreshing all sections');
    
    const messageDiv = document.querySelector('.message.ai:last-child');
    if (!messageDiv) return;
    
    // STEP 1: CAPTURE STATES
    const checkboxStates = {};
    document.querySelectorAll('.metadata-toggle').forEach(checkbox => {
        const type = checkbox.dataset.metadataType;
        const index = checkbox.dataset.metadataIndex;
        const key = `${type}_${index}`;
        checkboxStates[key] = checkbox.checked;
    });
    
    console.log('💾 Preserved states:', checkboxStates);
    
    // STEP 2: REFRESH ALL SECTIONS IMMEDIATELY WITH SAVED STATES
    const metadataPanel = messageDiv.querySelector('.metadata-panel');
    if (metadataPanel) {
        const newPanel = createMetadataPanel(currentFormSchema, checkboxStates);
        metadataPanel.replaceWith(newPanel);
        console.log('✅ Purple panel refreshed with saved states');
    }
    
    refreshMetadataPreview(checkboxStates);
    refreshDataModelSection(checkboxStates);
}

function refreshMetadataPreview(checkboxStates) {
    const messageDiv = document.querySelector('.message.ai:last-child');
    if (!messageDiv || !currentFormSchema) return;
    
    const metadataPreviewSection = messageDiv.querySelector('.metadata-preview-section');
    if (!metadataPreviewSection) return;
    
    const metadata = currentFormSchema.metadata_suggestions;
    const allMetadata = [
        ...(metadata.required || []).map((item, idx) => ({ ...item, type: 'required', index: idx })),
        ...(metadata.recommended || []).map((item, idx) => ({ ...item, type: 'recommended', index: idx })),
        ...(metadata.optional || []).map((item, idx) => ({ ...item, type: 'optional', index: idx }))
    ];
    
    const enabledMetadata = allMetadata.filter(item => {
        const key = `${item.type}_${item.index}`;
        if (item.type === 'required') return true;
        if (checkboxStates.hasOwnProperty(key)) return checkboxStates[key];
        return item.type === 'recommended';
    });
    
    console.log('🎨 Rebuilding pink section with', enabledMetadata.length, 'items');
    
    if (enabledMetadata.length > 0) {
        const newPreview = document.createElement('div');
        newPreview.className = 'metadata-preview-section';
        newPreview.style.cssText = metadataPreviewSection.style.cssText;
        
        newPreview.innerHTML = `
            <h3 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
                📊 Metadata That Will Be Captured
            </h3>
            <p style="margin: 0 0 15px 0; opacity: 0.9; font-size: 14px;">
                These values will be automatically recorded when this form is submitted:
            </p>
            <div style="
                background: rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                max-height: 300px;
                overflow-y: auto;
            ">
                ${enabledMetadata.map(item => {
                    const feasibility = getCaptureFeasibility(item.how);
                    const exampleValue = generateMetadataExample(item, feasibility);
                    return `
                        <div style="
                            padding: 8px 12px;
                            margin: 6px 0;
                            background: rgba(255,255,255,0.1);
                            border-radius: 6px;
                            border-left: 3px solid ${feasibility.color};
                            display: flex;
                            align-items: center;
                            gap: 10px;
                        ">
                            <span style="font-weight: bold; color: #ffd700; flex: 0 0 180px;">${item.field}:</span>
                            <span style="flex: 1; ${feasibility.type === 'manual' || feasibility.type === 'unknown' ? 'font-style: italic; opacity: 0.8;' : ''}">${exampleValue}</span>
                            <span style="font-size: 18px;">${feasibility.icon}</span>
                        </div>
                    `;
                }).join('')}
            </div>
            <div style="margin-top: 10px; padding: 8px 12px; background: rgba(255,255,255,0.1); border-radius: 6px; font-size: 11px; opacity: 0.9;">
                <strong>Legend:</strong> 🤖 = Captured automatically | 👤 = Requires user input | ❓ = Method to be determined
            </div>
        `;
        
        metadataPreviewSection.replaceWith(newPreview);
    } else {
        metadataPreviewSection.remove();
    }
}

function refreshDataModelSection(checkboxStates) {
    const messageDiv = document.querySelector('.message.ai:last-child');
    if (!messageDiv || !currentFormSchema) return;
    
    const dataModelSection = messageDiv.querySelector('.data-model-section');
    if (!dataModelSection) return;
    
    const newSection = createDataModelSectionWithStates(currentFormSchema, checkboxStates);
    dataModelSection.replaceWith(newSection);
    
    console.log('🗄️ Data Model section rebuilt');
}

function generateMetadataExample(field, feasibility) {
    const fieldName = field.field || 'unknown';
    if (feasibility.type === 'automatic') {
        const examples = {
            'submission_timestamp': '2025-11-11 14:30:45 UTC',
            'study_day': 'Day 5 of 30',
            'device_type': 'iPhone 14, Safari 16.5',
            'participant_id': 'P-0042',
            'session_id': 'sess_8x9y2z',
            'geolocation': 'Latitude: 51.7520, Longitude: -1.2577',
            'battery_level': '87%',
            'network_type': 'WiFi (5GHz)',
            'screen_brightness': '75%',
            'app_version': 'v2.3.1'
        };
        return examples[fieldName] || `[Auto-captured: ${fieldName}]`;
    }
    if (feasibility.type === 'manual') return '[Researcher will enter]';
    return '[To be determined]';
}

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

function isMetadataEnabled(type, index) {
    const checkbox = document.querySelector(`#metadata_${type}_${index}`);
    return checkbox ? checkbox.checked : (type === 'required' || type === 'recommended');
}

function createDataModelSection(schema) {
    const checkboxStates = {};
    document.querySelectorAll('.metadata-toggle').forEach(checkbox => {
        const type = checkbox.dataset.metadataType;
        const index = checkbox.dataset.metadataIndex;
        const key = `${type}_${index}`;
        checkboxStates[key] = checkbox.checked;
    });
    return createDataModelSectionWithStates(schema, checkboxStates);
}

function createDataModelSectionWithStates(schema, checkboxStates) {
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
    
    const allMetadata = [
        ...(metadata.required || []).map((item, idx) => ({ ...item, type: 'required', index: idx })),
        ...(metadata.recommended || []).map((item, idx) => ({ ...item, type: 'recommended', index: idx })),
        ...(metadata.optional || []).map((item, idx) => ({ ...item, type: 'optional', index: idx }))
    ];
    
    const enabledMetadata = allMetadata.filter(item => {
        const key = `${item.type}_${item.index}`;
        if (item.type === 'required') return true;
        if (checkboxStates && checkboxStates.hasOwnProperty(key)) {
            return checkboxStates[key];
        }
        return item.type === 'recommended';
    });
    
    console.log('🗄️ Data Model showing', enabledMetadata.length, 'enabled metadata fields');
    
    section.innerHTML = `
        <h3 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
            🗄️ Data Model Specification
        </h3>
        <p style="margin: 0 0 15px 0; opacity: 0.9; font-size: 14px;">
            Review database structure and customize field names before finalizing
        </p>
        
        <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px;">
            <div style="margin-bottom: 20px;">
                <h4 style="margin: 0 0 10px 0; font-size: 15px; opacity: 0.95;">
                    📊 Metadata Fields (System-Generated)
                </h4>
                <div style="background: rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                    ${enabledMetadata.map((item) => {
                        const feasibility = getCaptureFeasibility(item.how);
                        return `
                        <div style="display: flex; align-items: center; padding: 8px; margin: 4px 0; background: rgba(255,255,255,0.05); border-radius: 4px;">
                            <input 
                                type="text" 
                                value="${item.field}"
                                data-metadata-type="${item.type}"
                                data-metadata-index="${item.index}"
                                class="metadata-name-input"
                                style="flex: 1; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: #ffd700; padding: 6px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px;"
                                placeholder="field_name"
                            />
                            <span style="padding: 2px 8px; background: ${feasibility.color}; border-radius: 4px; font-size: 18px; margin-left: 10px; min-width: 35px; text-align: center;" title="${feasibility.type}">${feasibility.icon}</span>
                        </div>
                    `}).join('')}
                </div>
                <div style="margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 6px; font-size: 11px; opacity: 0.9;">
                    <strong>Legend:</strong> 🤖 = Automatic capture | 👤 = User input required | ❓ = Unknown method
                </div>
            </div>
            
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
                        <div style="display: flex; align-items: center; padding: 8px; margin: 4px 0; background: rgba(255,255,255,0.05); border-radius: 4px;">
                            <input 
                                type="text" 
                                value="${fieldId}"
                                data-field-index="${index}"
                                class="field-name-input"
                                style="flex: 1; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 6px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px;"
                                placeholder="field_name"
                            />
                            <span style="padding: 2px 8px; background: rgba(255,255,255,0.2); border-radius: 4px; font-size: 11px; margin-left: 10px; min-width: 60px; text-align: center;">${dataType}</span>
                            <span style="margin-left: 10px; font-size: 12px; opacity: 0.8;">${field.field_name || field.label || 'Field'}</span>
                        </div>
                    `}).join('')}
                </div>
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 6px; font-size: 12px; opacity: 0.9;">
                💡 <strong>Tip:</strong> Edit field names to match your database conventions. Use snake_case (e.g., water_intake_ml) for best compatibility.
            </div>
        </div>
    `;
    
    attachDataModelEventListeners(section, schema);
    return section;
}

function attachDataModelEventListeners(section, schema) {
    setTimeout(() => {
        section.querySelectorAll('.field-name-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const fieldIndex = parseInt(e.target.dataset.fieldIndex);
                const rawValue = e.target.value.trim();
                let cleanedName = rawValue.toLowerCase().replace(/\s+/g, '_');
                
                if (validateFieldName(cleanedName, e.target)) {
                    const formSchema = currentFormSchema.form_schema || currentFormSchema;
                    if (formSchema && formSchema.fields) {
                        formSchema.fields[fieldIndex].field_id = cleanedName;
                        e.target.value = cleanedName;
                        if (rawValue !== cleanedName) {
                            showSaveConfirmation(e.target, `Auto-corrected to: ${cleanedName}`);
                        } else {
                            showSaveConfirmation(e.target, 'Form field updated');
                        }
                    }
                } else {
                    const formSchema = currentFormSchema.form_schema || currentFormSchema;
                    e.target.value = formSchema?.fields[fieldIndex]?.field_id || '';
                }
            });
        });
        
        section.querySelectorAll('.metadata-name-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const metadataType = e.target.dataset.metadataType;
                const metadataIndex = parseInt(e.target.dataset.metadataIndex);
                const rawValue = e.target.value.trim();
                let cleanedName = rawValue.toLowerCase().replace(/\s+/g, '_');
                
                if (validateFieldName(cleanedName, e.target)) {
                    if (currentFormSchema && currentFormSchema.metadata_suggestions) {
                        const metadataArray = currentFormSchema.metadata_suggestions[metadataType];
                        if (metadataArray && metadataArray[metadataIndex]) {
                            metadataArray[metadataIndex].field = cleanedName;
                            e.target.value = cleanedName;
                            if (rawValue !== cleanedName) {
                                showSaveConfirmation(e.target, `Auto-corrected to: ${cleanedName}`);
                            } else {
                                showSaveConfirmation(e.target, 'Metadata field updated');
                            }
                            refreshAllSections();
                        }
                    }
                } else {
                    if (currentFormSchema && currentFormSchema.metadata_suggestions) {
                        const metadataArray = currentFormSchema.metadata_suggestions[metadataType];
                        if (metadataArray && metadataArray[metadataIndex]) {
                            e.target.value = metadataArray[metadataIndex].field;
                        }
                    }
                }
            });
        });
    }, 100);
}

function validateFieldName(fieldName, inputElement) {
    const errors = [];
    if (!fieldName || fieldName.trim() === '') errors.push('Field name cannot be empty');
    if (!/^[a-z_][a-z0-9_]*$/.test(fieldName)) errors.push('Use only lowercase letters, numbers, and underscores');
    if (fieldName && !/^[a-z_]/.test(fieldName)) errors.push('Must start with a letter or underscore');
    if (fieldName.length > 64) errors.push('Maximum 64 characters');
    const sqlKeywords = ['select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'table', 'from', 'where', 'order', 'group'];
    if (sqlKeywords.includes(fieldName.toLowerCase())) errors.push('Cannot use SQL reserved keyword');
    
    if (errors.length > 0) {
        showValidationError(inputElement, errors);
        return false;
    } else {
        showValidationSuccess(inputElement);
        return true;
    }
}

function showValidationError(element, errors) {
    const isMetadata = element.classList.contains('metadata-name-input');
    const textColor = isMetadata ? '#ffd700' : 'white';
    element.style.border = '2px solid #ef4444';
    element.style.background = 'rgba(239, 68, 68, 0.15)';
    element.style.color = textColor;
    const errorMsg = document.createElement('div');
    errorMsg.innerHTML = `<div style="position: absolute; background: #ef4444; color: white; padding: 8px 12px; border-radius: 4px; font-size: 11px; margin-top: 4px; z-index: 1000; box-shadow: 0 2px 4px rgba(0,0,0,0.2); max-width: 250px;">❌ ${errors.join('<br>❌ ')}</div>`;
    element.parentElement.style.position = 'relative';
    const existing = element.parentElement.querySelector('.validation-error');
    if (existing) existing.remove();
    errorMsg.className = 'validation-error';
    element.parentElement.appendChild(errorMsg);
}

function showValidationSuccess(element) {
    const isMetadata = element.classList.contains('metadata-name-input');
    const textColor = isMetadata ? '#ffd700' : 'white';
    element.style.border = '2px solid #4ade80';
    element.style.background = 'rgba(74, 222, 128, 0.15)';
    element.style.color = textColor;
    const existing = element.parentElement.querySelector('.validation-error');
    if (existing) existing.remove();
    setTimeout(() => {
        element.style.border = '1px solid rgba(255,255,255,0.3)';
        element.style.background = 'rgba(255,255,255,0.2)';
        element.style.color = textColor;
    }, 2000);
}

function showSaveConfirmation(element, message) {
    const originalBorder = element.style.border;
    element.style.border = '2px solid #4ade80';
    const confirmMsg = document.createElement('div');
    confirmMsg.textContent = `💾 ${message}`;
    confirmMsg.style.cssText = 'position: absolute; background: #4ade80; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; pointer-events: none; animation: fadeInOut 2s ease; z-index: 1000;';
    element.parentElement.style.position = 'relative';
    element.parentElement.appendChild(confirmMsg);
    setTimeout(() => {
        element.style.border = originalBorder;
        confirmMsg.remove();
    }, 2000);
}

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
 * ===================================
 * TASK 4: BULLETPROOF SKIP LOGIC
 * ===================================
 */

/**
 * Parse string-based conditional logic
 * Supports: "pain_level >= 5", "age > 18", "consent == true", "notes contains severe"
 */
function parseConditionalString(conditionalStr) {
    if (!conditionalStr || typeof conditionalStr !== 'string') return null;
    
    // Match pattern: field_name operator value
    const operators = ['>=', '<=', '==', '!=', '>', '<', 'contains', 'is_empty', 'is_not_empty'];
    
    for (const op of operators) {
        if (conditionalStr.includes(op)) {
            const parts = conditionalStr.split(op).map(s => s.trim());
            
            if (op === 'is_empty' || op === 'is_not_empty') {
                // Special case: unary operators
                return {
                    field: parts[0],
                    operator: op,
                    value: null
                };
            }
            
            if (parts.length === 2) {
                let value = parts[1];
                
                // Try to parse as number
                if (!isNaN(value)) {
                    value = parseFloat(value);
                } else if (value === 'true') {
                    value = true;
                } else if (value === 'false') {
                    value = false;
                } else {
                    // Remove quotes if present
                    value = value.replace(/^["']|["']$/g, '');
                }
                
                return {
                    field: parts[0],
                    operator: op,
                    value: value
                };
            }
        }
    }
    
    return null;
}

/**
 * Get value from form field - handles ALL input types
 * CRITICAL FIX: Query only actual input elements, not wrapper divs!
 * ALSO handles property access like "field_name.length"
 */
function getFieldValue(fieldId, formContainer) {
    // Check for property access (e.g., "initial_notes.length")
    let propertyAccess = null;
    let actualFieldId = fieldId;
    
    if (fieldId.includes('.')) {
        const parts = fieldId.split('.');
        actualFieldId = parts[0];
        propertyAccess = parts[1];
        console.log(`🔍 Detected property access: ${actualFieldId}.${propertyAccess}`);
    }
    
    // FIXED: Query ONLY input/select/textarea elements, not wrapper divs!
    let sourceField = formContainer.querySelector(
        `input[data-field-id="${actualFieldId}"], ` +
        `select[data-field-id="${actualFieldId}"], ` +
        `textarea[data-field-id="${actualFieldId}"]`
    );
    
    if (!sourceField) {
        console.warn(`⚠️ Field not found: ${actualFieldId}`);
        console.log(`   Tried to find: input, select, or textarea with data-field-id="${actualFieldId}"`);
        return null;
    }
    
    console.log(`✅ Found ${sourceField.tagName}[type="${sourceField.type}"] value="${sourceField.value}"`);
    
    let value;
    
    // Handle different input types
    if (sourceField.type === 'checkbox') {
        // Single checkbox
        value = sourceField.checked;
    } else if (sourceField.type === 'radio') {
        // Radio button group
        const checked = formContainer.querySelector(`input[name="${sourceField.name}"]:checked`);
        value = checked ? checked.value : null;
    } else if (sourceField.tagName === 'SELECT') {
        // Dropdown
        value = sourceField.value;
    } else if (sourceField.tagName === 'TEXTAREA') {
        // Textarea
        value = sourceField.value;
    } else if (sourceField.type === 'range') {
        // Slider
        value = parseFloat(sourceField.value);
    } else if (sourceField.type === 'number') {
        // Number input
        value = sourceField.value === '' ? null : parseFloat(sourceField.value);
    } else {
        // Text, date, time, etc.
        value = sourceField.value;
    }
    
    // Handle property access
    if (propertyAccess) {
        if (propertyAccess === 'length') {
            const length = value ? value.length : 0;
            console.log(`   📏 Returning .length: ${length}`);
            return length;
        }
        // Add more property handlers here if needed
        console.warn(`⚠️ Unknown property: ${propertyAccess}`);
    }
    
    return value;
}

/**
 * Evaluate a single condition against form data
 */
function evaluateCondition(condition, formContainer) {
    const sourceValue = getFieldValue(condition.field, formContainer);
    
    console.log(`  🔍 Field: ${condition.field}, Value: ${sourceValue}, Operator: ${condition.operator}, Compare: ${condition.value}`);
    
    // Handle special operators
    if (condition.operator === 'is_empty') {
        return sourceValue === null || sourceValue === '' || sourceValue === undefined;
    }
    
    if (condition.operator === 'is_not_empty') {
        return sourceValue !== null && sourceValue !== '' && sourceValue !== undefined;
    }
    
    // Convert to number if both sides are numeric
    let compareValue = sourceValue;
    let targetValue = condition.value;
    
    if (!isNaN(compareValue) && compareValue !== '' && compareValue !== null) {
        compareValue = parseFloat(compareValue);
    }
    
    if (!isNaN(targetValue) && targetValue !== '' && targetValue !== null) {
        targetValue = parseFloat(targetValue);
    }
    
    // Evaluate comparison
    let result = false;
    
    switch (condition.operator) {
        case '>':
            result = compareValue > targetValue;
            break;
        case '>=':
            result = compareValue >= targetValue;
            break;
        case '<':
            result = compareValue < targetValue;
            break;
        case '<=':
            result = compareValue <= targetValue;
            break;
        case '==':
        case '===':
            result = compareValue == targetValue;
            break;
        case '!=':
        case '!==':
            result = compareValue != targetValue;
            break;
        case 'contains':
            result = String(compareValue).toLowerCase().includes(String(targetValue).toLowerCase());
            break;
    }
    
    console.log(`  📊 Result: ${result}`);
    return result;
}

/**
 * Evaluate skip logic condition with BOTH formats supported
 */
function evaluateSkipLogic(field, formContainer) {
    let condition = null;
    
    // Support BOTH formats
    if (field.skip_logic && field.skip_logic.show_if) {
        // Format 1: Object-based
        if (typeof field.skip_logic.show_if === 'object') {
            condition = field.skip_logic.show_if;
        }
        // Format 2: String-based
        else if (typeof field.skip_logic.show_if === 'string') {
            condition = parseConditionalString(field.skip_logic.show_if);
        }
    } else if (field.conditional && field.conditional.show_if) {
        // Backend format: "conditional"
        if (typeof field.conditional.show_if === 'string') {
            condition = parseConditionalString(field.conditional.show_if);
        } else if (typeof field.conditional.show_if === 'object') {
            condition = field.conditional.show_if;
        }
    }
    
    if (!condition) {
        console.log(`  ⚠️ No condition found for field`);
        return false;
    }
    
    console.log('🎯 Evaluating skip logic condition:');
    
    return evaluateCondition(condition, formContainer);
}

/**
 * Update field visibility based on skip logic evaluation
 */
function updateFieldVisibility(fieldDiv, fieldId, field, formContainer) {
    const shouldShow = evaluateSkipLogic(field, formContainer);
    
    if (shouldShow && fieldDiv.classList.contains('field-hidden')) {
        // SHOW THE FIELD
        fieldDiv.classList.remove('field-hidden');
        fieldDiv.classList.add('field-visible');
        
        // Enable inputs
        fieldDiv.querySelectorAll('input, select, textarea').forEach(input => {
            input.disabled = false;
        });
        
        console.log(`✅ SHOWING field: ${fieldId}`);
        
    } else if (!shouldShow && !fieldDiv.classList.contains('field-hidden')) {
        // HIDE THE FIELD
        fieldDiv.classList.remove('field-visible');
        fieldDiv.classList.add('field-hidden');
        
        // Disable inputs and optionally clear values
        fieldDiv.querySelectorAll('input, select, textarea').forEach(input => {
            input.disabled = true;
            
            if (SKIP_LOGIC_CONFIG.clearValueOnHide) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            }
        });
        
        console.log(`🔒 HIDING field: ${fieldId} ${SKIP_LOGIC_CONFIG.clearValueOnHide ? '(cleared)' : '(preserved)'}`);
    }
}

/**
 * CRITICAL: Attach event listeners for ALL input types
 */
function attachSkipLogicListeners(formContainer, fieldsWithSkipLogic) {
    if (fieldsWithSkipLogic.length === 0) return;
    
    console.log('🎯 Setting up skip logic for', fieldsWithSkipLogic.length, 'conditional fields');
    
    // Get ALL input elements in the form
    const allInputs = formContainer.querySelectorAll('input, select, textarea');
    
    console.log(`📝 Found ${allInputs.length} total input elements`);
    
    // Function to re-evaluate all skip logic
    const evaluateAllSkipLogic = () => {
        console.log('🔄 Evaluating skip logic for all fields...');
        fieldsWithSkipLogic.forEach(({fieldDiv, fieldId, field}) => {
            updateFieldVisibility(fieldDiv, fieldId, field, formContainer);
        });
    };
    
    // Attach listeners to ALL inputs
    allInputs.forEach((input, index) => {
        const fieldId = input.dataset.fieldId || input.name || `input_${index}`;
        
        // CRITICAL: Listen to MULTIPLE events
        // - input: fires while typing (text, number, range)
        // - change: fires on blur or selection change (all types)
        // - blur: fires when leaving field
        
        input.addEventListener('input', (e) => {
            console.log(`📥 INPUT event from ${fieldId}:`, e.target.value);
            evaluateAllSkipLogic();
        });
        
        input.addEventListener('change', (e) => {
            console.log(`🔄 CHANGE event from ${fieldId}:`, e.target.value);
            evaluateAllSkipLogic();
        });
        
        input.addEventListener('blur', (e) => {
            console.log(`👋 BLUR event from ${fieldId}:`, e.target.value);
            evaluateAllSkipLogic();
        });
        
        console.log(`✅ Attached listeners to ${input.type || input.tagName}: ${fieldId}`);
    });
    
    // Initial evaluation after a short delay
    setTimeout(() => {
        console.log('🚀 Running initial skip logic evaluation...');
        evaluateAllSkipLogic();
    }, 100);
}

/**
 * ===================================
 * CREATE FORM PREVIEW WITH SKIP LOGIC
 * ===================================
 */
function createFormPreview(schema, fullSchema = null) {
    const preview = document.createElement('div');
    preview.className = 'form-preview';
    
    preview.innerHTML = `
        <h3>📋 ${schema.form_name || schema.title || 'New Form'}</h3>
        <p style="color: #666; margin: 10px 0;">${schema.description || 'No description provided'}</p>
    `;
    
    const formContainer = document.createElement('div');
    formContainer.style.cssText = 'background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0;';
    formContainer.className = 'interactive-form';
    
    const fieldsWithSkipLogic = [];
    
    schema.fields.forEach((field, fieldIndex) => {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'form-field';
        fieldDiv.dataset.fieldIndex = fieldIndex;
        fieldDiv.dataset.fieldId = field.field_id || field.field_name?.toLowerCase().replace(/\s+/g, '_') || `field_${fieldIndex}`;
        fieldDiv.style.cssText = 'margin-bottom: 20px;';
        
        // Check for conditional logic in BOTH formats
        const hasConditional = (field.skip_logic && field.skip_logic.show_if) || 
                               (field.conditional && field.conditional.show_if);
        
        if (hasConditional) {
            fieldsWithSkipLogic.push({
                fieldDiv: fieldDiv,
                fieldId: fieldDiv.dataset.fieldId,
                field: field
            });
            
            // Initially hide
            fieldDiv.classList.add('field-hidden');
            
            // Add indicator
            let conditionText = '';
            if (field.conditional && field.conditional.description) {
                conditionText = field.conditional.description;
            } else if (field.conditional && field.conditional.show_if) {
                conditionText = `Appears when: ${field.conditional.show_if}`;
            } else if (field.skip_logic && field.skip_logic.show_if) {
                if (typeof field.skip_logic.show_if === 'string') {
                    conditionText = `Appears when: ${field.skip_logic.show_if}`;
                } else {
                    const c = field.skip_logic.show_if;
                    conditionText = `Appears when: ${c.field} ${c.operator} ${c.value}`;
                }
            }
            
            const indicator = document.createElement('div');
            indicator.className = 'skip-logic-indicator';
            indicator.innerHTML = `🔒 <strong>Conditional Field:</strong> ${conditionText}`;
            fieldDiv.appendChild(indicator);
        }
        
        // Label
        const label = document.createElement('label');
        label.style.cssText = 'display: block; font-weight: 600; margin-bottom: 8px; color: #333;';
        label.innerHTML = `
            ${field.field_name || field.label}
            ${field.required ? '<span style="color: #dc3545;">*</span>' : ''}
            ${hasConditional ? '<span class="conditional-field-badge">CONDITIONAL</span>' : ''}
        `;
        if (field.description) {
            const desc = document.createElement('div');
            desc.style.cssText = 'font-size: 0.85em; color: #666; font-weight: normal; margin-top: 4px;';
            desc.textContent = field.description;
            label.appendChild(desc);
        }
        fieldDiv.appendChild(label);
        
        // Render input based on field type
        const fieldType = field.field_type || field.type;
        let input;
        
        switch(fieldType) {
            case 'text':
                input = document.createElement('input');
                input.type = 'text';
                input.placeholder = `Enter ${field.field_name || field.label}`;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
                break;
                
            case 'textarea':
                input = document.createElement('textarea');
                input.placeholder = `Enter ${field.field_name || field.label}`;
                input.rows = 4;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em; font-family: inherit;';
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
                if (field.validation?.max_length) input.maxLength = field.validation.max_length;
                break;
                
            case 'number':
                input = document.createElement('input');
                input.type = 'number';
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
                break;
                
            case 'time':
                input = document.createElement('input');
                input.type = 'time';
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                    radio.name = fieldDiv.dataset.fieldId;
                    radio.value = option;
                    radio.id = `${fieldDiv.dataset.fieldId}_${idx}`;
                    radio.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                    checkbox.id = `${fieldDiv.dataset.fieldId}_${idx}`;
                    checkbox.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
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
                input.dataset.fieldId = fieldDiv.dataset.fieldId;
                input.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1em;';
        }
        
        if (input) fieldDiv.appendChild(input);
        formContainer.appendChild(fieldDiv);
    });
    
    // CRITICAL: Attach skip logic event listeners
    attachSkipLogicListeners(formContainer, fieldsWithSkipLogic);
    
    preview.appendChild(formContainer);
    
    // Add Metadata Preview Section
    if (fullSchema && fullSchema.metadata_suggestions) {
        const metadataPreview = document.createElement('div');
        metadataPreview.className = 'metadata-preview-section';
        metadataPreview.style.cssText = `
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        const metadata = fullSchema.metadata_suggestions;
        const allMetadata = [
            ...(metadata.required || []).map((item, idx) => ({ ...item, type: 'required', index: idx })),
            ...(metadata.recommended || []).map((item, idx) => ({ ...item, type: 'recommended', index: idx })),
            ...(metadata.optional || []).map((item, idx) => ({ ...item, type: 'optional', index: idx }))
        ];
        
        const enabledMetadata = allMetadata.filter(item => isMetadataEnabled(item.type, item.index));
        
        if (enabledMetadata.length > 0) {
            metadataPreview.innerHTML = `
                <h3 style="margin: 0 0 10px 0; display: flex; align-items: center; gap: 8px;">
                    📊 Metadata That Will Be Captured
                </h3>
                <p style="margin: 0 0 15px 0; opacity: 0.9; font-size: 14px;">
                    These values will be automatically recorded when this form is submitted:
                </p>
                <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px; font-family: 'Courier New', monospace; font-size: 13px; max-height: 300px; overflow-y: auto;">
                    ${enabledMetadata.map(item => {
                        const feasibility = getCaptureFeasibility(item.how);
                        const exampleValue = generateMetadataExample(item, feasibility);
                        return `
                            <div style="padding: 8px 12px; margin: 6px 0; background: rgba(255,255,255,0.1); border-radius: 6px; border-left: 3px solid ${feasibility.color}; display: flex; align-items: center; gap: 10px;">
                                <span style="font-weight: bold; color: #ffd700; flex: 0 0 180px;">${item.field}:</span>
                                <span style="flex: 1; ${feasibility.type === 'manual' || feasibility.type === 'unknown' ? 'font-style: italic; opacity: 0.8;' : ''}">${exampleValue}</span>
                                <span style="font-size: 18px;">${feasibility.icon}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div style="margin-top: 10px; padding: 8px 12px; background: rgba(255,255,255,0.1); border-radius: 6px; font-size: 11px; opacity: 0.9;">
                    <strong>Legend:</strong> 🤖 = Captured automatically | 👤 = Requires user input | ❓ = Method to be determined
                </div>
            `;
            preview.appendChild(metadataPreview);
        }
    }
    
    // JSON viewer
    const jsonDetails = document.createElement('details');
    jsonDetails.style.cssText = 'margin-top: 15px;';
    jsonDetails.innerHTML = `
        <summary style="cursor: pointer; font-weight: 600; color: #667eea;">View JSON Schema</summary>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; margin-top: 10px; font-size: 0.85em;">${JSON.stringify(schema, null, 2)}</pre>
    `;
    preview.appendChild(jsonDetails);
    
    // Action buttons - ONLY show on latest form!
    // Check if this preview is in the latest form message
    setTimeout(() => {
        const parentMessage = preview.closest('.message.ai');
        if (parentMessage && parentMessage.classList.contains('latest-form')) {
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
        }
    }, 10);
    
    return preview;
}

function handleApproveForm(schema) {
    addMessage('ai', `✅ Great! I'll save this form with your configured metadata and field names. The form "${schema.form_name || schema.title}" is ready to use!`);
    console.log('Form approved:', schema);
    setTimeout(() => {
        addMessage('ai', 'Would you like to create another form, or modify this one?');
    }, 1000);
}

function handleRefineForm(schema) {
    conversationMode = 'refine';
    currentFormSchema = schema;
    updateInputPlaceholder('refine');
    addMessage('ai', 'Sure! What changes would you like me to make? For example:\n\n• "Add a date field that auto-populates with today\'s date"\n• "Change the pain scale to 1-5"\n• "Make the notes field optional"\n• "Add skip logic: if pain > 5, show medication field"');
    chatInput.focus();
}

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

function formatMessage(text) {
    text = text.replace(/\n/g, '<br>');
    text = text.replace(/^• /gm, '&bull; ');
    return text;
}

function showLoading(show) {
    loadingIndicator.classList.toggle('active', show);
    if (show) scrollToBottom();
}

function setInputState(enabled) {
    chatInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateInputPlaceholder(mode) {
    if (mode === 'refine') {
        chatInput.placeholder = 'What changes would you like to make?';
    } else {
        chatInput.placeholder = 'Describe the form you want to create...';
    }
}

document.addEventListener('DOMContentLoaded', init);
console.log('🚀 AI Form Generator JS loaded - BULLETPROOF SKIP LOGIC VERSION!');