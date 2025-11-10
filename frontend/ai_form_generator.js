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
    
    // Add form preview
    const preview = createFormPreview(formSchema);
    contentDiv.appendChild(preview);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Create a form preview card with interactive fields
 */
function createFormPreview(schema) {
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
    approveButton.innerHTML = '✅ Approve & Save Form';
    approveButton.onclick = () => handleApproveForm(schema);
    
    const refineButton = document.createElement('button');
    refineButton.className = 'action-button secondary';
    refineButton.innerHTML = '🔧 Request Changes';
    refineButton.onclick = () => handleRefineForm(schema);
    
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
    addMessage('ai', `✅ Great! I'll save this form to your study. The form "${schema.form_name || schema.title}" is ready to use!`);
    
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