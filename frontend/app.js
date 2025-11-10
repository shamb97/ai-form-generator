// ==================== CONFIGURATION ====================
const API_BASE_URL = 'http://127.0.0.1:8000';

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AI Form Generator initialized');
    
    // Initialize tab navigation
    initializeTabs();
    
    // Check backend status
    checkBackendStatus();
    
    // Load studies list
    loadStudies();
    
    // Setup form submission
    setupFormSubmission();
    
    // Populate study selector
    populateStudySelector();
});

// ==================== TAB NAVIGATION ====================
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.tab-panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panels
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding panel
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Load data for specific tabs
            if (tabName === 'studies') {
                loadStudies();
            }
        });
    });
}

// ==================== BACKEND STATUS ====================
async function checkBackendStatus() {
    const statusIndicator = document.getElementById('backend-status');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusIndicator.textContent = '● Online';
            statusIndicator.classList.add('online');
            statusIndicator.classList.remove('offline');
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        statusIndicator.textContent = '● Offline';
        statusIndicator.classList.add('offline');
        statusIndicator.classList.remove('online');
        console.error('Backend status check failed:', error);
    }
}

// ==================== FORM SUBMISSION ====================
function setupFormSubmission() {
    const form = document.getElementById('create-study-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form values
        const studyName = document.getElementById('study-name').value;
        const studyDescription = document.getElementById('study-description').value;
        const studyRequirements = document.getElementById('study-requirements').value;
        
        // Show loading status
        document.getElementById('generation-status').style.display = 'block';
        document.getElementById('generation-result').style.display = 'none';
        
        try {
            // Step 1: Create study in database
            const studyResponse = await fetch(`${API_BASE_URL}/api/v1/studies/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: studyName,
                    description: studyDescription
                })
            });
            
            if (!studyResponse.ok) {
                throw new Error('Failed to create study');
            }
            
            const studyData = await studyResponse.json();
            const studyId = studyData.study_id;
            
            console.log('✅ Study created:', studyData);
            
            // Step 2: Generate forms using AI
            const generateResponse = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: studyRequirements
                })
            });
            
            if (!generateResponse.ok) {
                throw new Error('Failed to generate forms');
            }
            
            const formsData = await generateResponse.json();
            console.log('✅ Forms generated:', formsData);
            
            // Step 3: Calculate schedule using LCM algorithm
            // (This would normally be done in the backend)
            // For now, we'll display success
            
            // Hide loading, show success
            document.getElementById('generation-status').style.display = 'none';
            
            const resultDiv = document.getElementById('generation-result');
            const infoDiv = document.getElementById('generated-info');
            
            infoDiv.innerHTML = `
                <p><strong>Study ID:</strong> ${studyId}</p>
                <p><strong>Study Name:</strong> ${studyName}</p>
                <p><strong>Forms Generated:</strong> ${formsData.forms ? formsData.forms.length : 'Processing...'}</p>
                <p><strong>Status:</strong> Ready for deployment</p>
            `;
            
            resultDiv.style.display = 'block';
            
            // Reset form
            form.reset();
            
            // Refresh studies list
            loadStudies();
            populateStudySelector();
            
        } catch (error) {
            console.error('❌ Error:', error);
            document.getElementById('generation-status').style.display = 'none';
            alert('Error generating study. Please check console and try again.');
        }
    });
}

// ==================== LOAD STUDIES ====================
async function loadStudies() {
    const studiesList = document.getElementById('studies-list');
    studiesList.innerHTML = '<p class="loading">Loading studies...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/studies`);
        
        if (!response.ok) {
            throw new Error('Failed to load studies');
        }
        
        const data = await response.json();
        console.log('📚 Studies loaded:', data);
        
        if (data.count === 0) {
            studiesList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #6b7280;">
                    <p style="font-size: 1.2rem; margin-bottom: 1rem;">No studies yet</p>
                    <p>Create your first study using the "Create Study" tab!</p>
                </div>
            `;
            return;
        }
        
        // Display studies
        studiesList.innerHTML = '';
        data.studies.forEach(study => {
            const studyCard = createStudyCard(study);
            studiesList.appendChild(studyCard);
        });
        
    } catch (error) {
        console.error('❌ Error loading studies:', error);
        studiesList.innerHTML = '<p class="loading" style="color: #dc2626;">Failed to load studies. Please check backend connection.</p>';
    }
}

function createStudyCard(study) {
    const card = document.createElement('div');
    card.className = 'study-card';
    
    const createdDate = new Date(study.created_at).toLocaleDateString();
    
    card.innerHTML = `
        <h3>${study.name}</h3>
        <p>${study.description}</p>
        <div class="study-meta">
            <span>📅 Created: ${createdDate}</span>
            <span>📝 Forms: ${study.form_count}</span>
        </div>
        <div class="study-actions">
            <button class="btn btn-primary" onclick="viewStudyDetails(${study.id})">View Details</button>
            <button class="btn btn-secondary" onclick="viewStudySchedule(${study.id})">Schedule</button>
        </div>
    `;
    
    return card;
}

// ==================== STUDY DETAILS ====================
async function viewStudyDetails(studyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/studies/${studyId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load study details');
        }
        
        const data = await response.json();
        const study = data.study;
        
        console.log('📖 Study details:', study);
        
        alert(`
Study: ${study.name}
Description: ${study.description}
Created: ${new Date(study.created_at).toLocaleString()}
Forms: ${study.form_count}
Completions: ${study.completion_count}
        `);
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to load study details');
    }
}

async function viewStudySchedule(studyId) {
    // Switch to schedule tab
    document.querySelector('.tab[data-tab="schedule"]').click();
    
    // Select the study
    document.getElementById('study-selector').value = studyId;
    
    // Load schedule
    loadSchedule();
}

// ==================== SCHEDULE VISUALIZATION ====================
async function populateStudySelector() {
    const selector = document.getElementById('study-selector');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/studies`);
        const data = await response.json();
        
        // Clear existing options (except first)
        selector.innerHTML = '<option value="">Select a study...</option>';
        
        // Add study options
        data.studies.forEach(study => {
            const option = document.createElement('option');
            option.value = study.id;
            option.textContent = study.name;
            selector.appendChild(option);
        });
        
    } catch (error) {
        console.error('❌ Error populating selector:', error);
    }
}

async function loadSchedule() {
    const studyId = document.getElementById('study-selector').value;
    
    if (!studyId) {
        alert('Please select a study first');
        return;
    }
    
    const scheduleDisplay = document.getElementById('schedule-display');
    scheduleDisplay.style.display = 'block';
    
    // For now, show a sample schedule
    // In production, this would fetch from backend
    displaySampleSchedule(studyId);
}

function displaySampleSchedule(studyId) {
    document.getElementById('schedule-study-name').textContent = `Study Schedule (ID: ${studyId})`;
    document.getElementById('schedule-cycle-info').textContent = 'Cycle Length: 21 days | Based on LCM(1, 7, 21)';
    
    // Generate sample calendar
    const calendarGrid = document.getElementById('calendar-grid');
    calendarGrid.innerHTML = '';
    
    // Sample schedule pattern (21-day cycle)
    const schedulePattern = [
        'abc', 'a', 'a', 'a', 'a', 'a', 'a',  // Week 1
        'ab', 'a', 'a', 'a', 'a', 'a', 'a',   // Week 2
        'ab', 'a', 'a', 'a', 'a', 'a', 'a'    // Week 3
    ];
    
    schedulePattern.forEach((dayType, index) => {
        const dayCell = document.createElement('div');
        dayCell.className = 'day-cell';
        
        let displayType = '';
        let className = '';
        
        switch(dayType) {
            case 'abc':
                displayType = 'ABC';
                className = 'day-type-abc';
                break;
            case 'ab':
                displayType = 'AB';
                className = 'day-type-ab';
                break;
            case 'a':
                displayType = 'A';
                className = 'day-type-a';
                break;
        }
        
        dayCell.innerHTML = `
            <div class="day-number">Day ${index + 1}</div>
            <span class="day-type ${className}">${displayType}</span>
        `;
        
        calendarGrid.appendChild(dayCell);
    });
    
    // Display legend
    displayLegend();
}

function displayLegend() {
    const legendList = document.getElementById('day-types-list');
    legendList.innerHTML = '';
    
    const dayTypes = [
        { name: 'ABC Day', color: '#fce7f3', forms: 'Forms A, B, C all due' },
        { name: 'AB Day', color: '#e0e7ff', forms: 'Forms A, B due' },
        { name: 'A Day', color: '#dbeafe', forms: 'Form A due' },
        { name: 'Baseline', color: '#d1fae5', forms: 'Special: Day 1 forms' },
        { name: 'End of Treatment', color: '#fef3c7', forms: 'Special: Final assessments' },
        { name: 'Free Day', color: '#f3f4f6', forms: 'No forms scheduled' }
    ];
    
    dayTypes.forEach(type => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${type.color};"></div>
            <span class="legend-label">${type.name}</span>
            <span class="legend-forms">${type.forms}</span>
        `;
        legendList.appendChild(item);
    });
}

// ==================== DEMO SCENARIOS ====================
function loadDemo1() {
    alert('Demo 1: Simple Daily Diary\n\nThis would create a 14-day study with a single daily symptom diary.\n\nFeature coming soon!');
}

function loadDemo2() {
    alert('Demo 2: Multi-Form Study\n\nThis would create a study with:\n- Daily diary\n- Weekly assessment\n- Biweekly survey\n\nFeature coming soon!');
}

function loadDemo3() {
    alert('Demo 3: Complex Clinical Trial\n\nThis would create a complete clinical trial with:\n- 5 different forms\n- 3 study phases\n- Event-triggered assessments\n- LCM scheduling\n\nFeature coming soon!');
}

// ==================== HELPER FUNCTIONS ====================
function viewSchedule() {
    document.querySelector('.tab[data-tab="schedule"]').click();
}

function viewStudies() {
    document.querySelector('.tab[data-tab="studies"]').click();
}

// ==================== PERIODIC STATUS CHECK ====================
// Check backend status every 30 seconds
setInterval(checkBackendStatus, 30000);