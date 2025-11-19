// ==================== CONFIGURATION ====================
const API_URL = 'http://127.0.0.1:8000/api/v1';

// ==================== AUTHENTICATION ====================
let currentUser = null;
let authToken = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Dashboard initializing...');
    
    // Get token from localStorage
    authToken = localStorage.getItem('authToken');
    const userDataStr = localStorage.getItem('userData');
    
    if (!authToken || !userDataStr) {
        console.log('❌ No authentication found, redirecting to login...');
        window.location.href = 'login.html';
        return;
    }
    
    try {
        currentUser = JSON.parse(userDataStr);
        console.log('✅ User authenticated:', currentUser);
        
        // Update UI with user info
        updateUserInfo();
        
        // Load dashboard data
        await loadDashboard();
        
    } catch (error) {
        console.error('❌ Error initializing dashboard:', error);
        showAlert('Error loading dashboard. Please try logging in again.', 'error');
        setTimeout(() => {
            logout();
        }, 2000);
    }
});

// ==================== USER INFO ====================
function updateUserInfo() {
    document.getElementById('userName').textContent = currentUser.username;
    document.getElementById('welcomeTitle').textContent = `Welcome back, ${currentUser.username}!`;
    
    // Customize subtitle based on role
    let subtitle = 'Manage your research studies';
    if (currentUser.role === 'subject' || currentUser.role === 'participant') {
        subtitle = 'Complete your assigned forms and track progress';
    } else if (currentUser.role === 'study_designer' || currentUser.role === 'designer') {
        subtitle = 'Create and manage research studies';
    }
    document.getElementById('welcomeSubtitle').textContent = subtitle;
}

// ==================== LOAD DASHBOARD ====================
async function loadDashboard() {
    console.log('📊 Loading dashboard data...');
    
    // Determine what to load based on user role
    const isCreator = currentUser.role === 'study_designer' || currentUser.role === 'designer';
    const isSubject = currentUser.role === 'subject' || currentUser.role === 'participant';
    
    // Load studies created by this user
    if (isCreator) {
        await loadMyStudies();
    }
    
    // Load studies user is enrolled in
    if (isSubject) {
        await loadParticipatingStudies();
    }
    
    // If user has no role or data, show empty state
    if (!isCreator && !isSubject) {
        showAlert('Please complete your profile setup.', 'info');
    }
}

// ==================== LOAD MY STUDIES (as Creator) ====================
async function loadMyStudies() {
    const section = document.getElementById('myStudiesSection');
    const content = document.getElementById('myStudiesContent');
    const countBadge = document.getElementById('myStudiesCount');
    
    section.style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/studies`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load studies');
        }
        
        const data = await response.json();
        console.log('📚 My studies:', data);
        
        // Filter studies created by this user
        const myStudies = data.studies || [];
        countBadge.textContent = myStudies.length;
        
        if (myStudies.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <h3>No studies yet</h3>
                    <p>Create your first research study to get started!</p>
                    <button class="btn-primary" onclick="createNewStudy()">
                        <span>📝</span>
                        <span>Create New Study</span>
                    </button>
                </div>
            `;
            return;
        }
        
        // Render studies
        content.innerHTML = '<div class="studies-grid" id="myStudiesGrid"></div>';
        const grid = document.getElementById('myStudiesGrid');
        
        myStudies.forEach(study => {
            const card = createStudyCard(study, 'creator');
            grid.appendChild(card);
        });
        
    } catch (error) {
        console.error('❌ Error loading studies:', error);
        content.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error Loading Studies</h3>
                <p>${error.message}</p>
                <button class="btn-secondary" onclick="loadMyStudies()">Try Again</button>
            </div>
        `;
    }
}

// ==================== LOAD PARTICIPATING STUDIES (as Subject) ====================
async function loadParticipatingStudies() {
    const section = document.getElementById('participatingSection');
    const content = document.getElementById('participatingContent');
    const countBadge = document.getElementById('participatingCount');
    
    section.style.display = 'block';
    
    try {
        // Get enrollments for this user
        const response = await fetch(`${API_URL}/enrollments/my-studies`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            // If endpoint doesn't exist yet, show placeholder
            console.log('ℹ️ Enrollments endpoint not available yet');
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎯</div>
                    <h3>No enrollments yet</h3>
                    <p>Use an access code to enroll in a study!</p>
                    <button class="btn-secondary" onclick="enrollInStudy()">
                        <span>🎯</span>
                        <span>Enroll in Study</span>
                    </button>
                </div>
            `;
            countBadge.textContent = '0';
            return;
        }
        
        const data = await response.json();
        console.log('👤 My enrollments:', data);
        
        const enrollments = data.enrollments || [];
        countBadge.textContent = enrollments.length;
        
        if (enrollments.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎯</div>
                    <h3>No enrollments yet</h3>
                    <p>Use an access code to enroll in a study!</p>
                    <button class="btn-secondary" onclick="enrollInStudy()">
                        <span>🎯</span>
                        <span>Enroll in Study</span>
                    </button>
                </div>
            `;
            return;
        }
        
        // Render enrollments
        content.innerHTML = '<div class="studies-grid" id="participatingGrid"></div>';
        const grid = document.getElementById('participatingGrid');
        
        enrollments.forEach(enrollment => {
            const card = createStudyCard(enrollment.study, 'participant', enrollment);
            grid.appendChild(card);
        });
        
    } catch (error) {
        console.error('❌ Error loading enrollments:', error);
        content.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎯</div>
                <h3>No enrollments yet</h3>
                <p>Use an access code to enroll in a study!</p>
                <button class="btn-secondary" onclick="enrollInStudy()">
                    <span>🎯</span>
                    <span>Enroll in Study</span>
                </button>
            </div>
        `;
        countBadge.textContent = '0';
    }
}

// ==================== CREATE STUDY CARD ====================
function createStudyCard(study, context, enrollmentData = null) {
    const card = document.createElement('div');
    card.className = 'study-card';
    
    // Format dates
    const createdDate = new Date(study.created_at).toLocaleDateString();
    
    // Determine status
    const status = study.status || 'active';
    const statusClass = status === 'active' ? 'status-active' : 'status-draft';
    const statusText = status.charAt(0).toUpperCase() + status.slice(1);
    
    // Build card HTML
    if (context === 'creator') {
        // Card for studies user created
        card.innerHTML = `
            <div class="study-card-header">
                <div>
                    <h3>${study.name}</h3>
                    <span class="study-status ${statusClass}">${statusText}</span>
                </div>
            </div>
            <p>${study.description || 'No description provided'}</p>
            <div class="study-meta">
                <span>📅 Created ${createdDate}</span>
                <span>📝 ${study.form_count || 0} forms</span>
                <span>👥 ${study.participant_count || 0} participants</span>
            </div>
            <div class="study-actions">
                <button class="btn-small btn-view" onclick="viewStudy(${study.id})">
                    View Details
                </button>
                <button class="btn-small btn-data" onclick="viewStudyData(${study.id})">
                    View Data
                </button>
                <button class="btn-small btn-edit" onclick="editStudy(${study.id})">
                    Edit
                </button>
                <button class="btn-small btn-edit" onclick="generateAccessCode(${study.id})">
                    Access Codes
                </button>
            </div>
        `;
    } else {
        // Card for studies user is participating in
        const formsCompleted = enrollmentData?.forms_completed || 0;
        const totalForms = enrollmentData?.total_forms || study.form_count || 0;
        const formsDue = enrollmentData?.forms_due_today || 0;
        
        card.innerHTML = `
            <div class="study-card-header">
                <div>
                    <h3>${study.name}</h3>
                    <span class="study-status ${statusClass}">${statusText}</span>
                </div>
            </div>
            <p>${study.description || 'No description provided'}</p>
            <div class="study-meta">
                <span>📊 Progress: ${formsCompleted}/${totalForms}</span>
                <span>⏰ ${formsDue} due today</span>
            </div>
            <div class="study-actions">
                <button class="btn-small btn-view" onclick="completeForms(${study.id})">
                    Complete Forms
                </button>
                <button class="btn-small btn-data" onclick="viewMyProgress(${study.id})">
                    My Progress
                </button>
            </div>
        `;
    }
    
    return card;
}

// ==================== ACTION FUNCTIONS ====================

function createNewStudy() {
    // Open the study creation modal
    document.getElementById('createStudyModal').style.display = 'flex';
    // Reset the form
    document.getElementById('createStudyForm').reset();
}

function closeStudyModal() {
    document.getElementById('createStudyModal').style.display = 'none';
}

// STEP 7: Submit Study to Backend API
async function submitStudy(event) {
    event.preventDefault();
    
    // Get form values
    const studyName = document.getElementById('studyName').value;
    const studyDescription = document.getElementById('studyDescription').value;
    const studyDuration = parseInt(document.getElementById('studyDuration').value);
    
    // Create study payload
    const studyData = {
        name: studyName,
        description: studyDescription,
        duration_days: studyDuration,
        status: 'draft',
        forms: []  // Empty forms array for now
    };
    
    console.log('📤 Creating study:', studyData);
    
    try {
        // Call backend API to create study
        const response = await fetch(`${API_URL}/studies`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studyData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create study');
        }
        
        const createdStudy = await response.json();
        console.log('✅ Study created successfully:', createdStudy);
        
        // Show success message
        showAlert(`Study "${studyName}" created successfully!`, 'success');
        
        // Close the modal
        closeStudyModal();
        
        // Reload the studies list (Step 8 - Display Studies)
        await loadMyStudies();
        
    } catch (error) {
        console.error('❌ Error creating study:', error);
        showAlert(`Error: ${error.message}`, 'error');
    }
}

function enrollInStudy() {
    window.location.href = 'enroll.html';
}

function viewStudy(studyId) {
    console.log('👀 View study:', studyId);
    showAlert(`Viewing study ${studyId} - Full viewer coming soon!`, 'info');
    // TODO: Show study details modal or navigate to study page
}

function viewStudyData(studyId) {
    console.log('📊 View study data:', studyId);
    showAlert(`Viewing data for study ${studyId} - Data viewer coming soon!`, 'info');
    // TODO: Navigate to data viewer page
}

function editStudy(studyId) {
    console.log('✏️ Edit study:', studyId);
    showAlert(`Editing study ${studyId} - Editor coming soon!`, 'info');
    // TODO: Navigate to study editor
}

function generateAccessCode(studyId) {
    console.log('🔑 Generate access code for study:', studyId);
    showAlert(`Generating access code for study ${studyId} - Coming soon!`, 'info');
    // TODO: Show access code generation modal
}

function completeForms(studyId) {
    console.log('📝 Complete forms for study:', studyId);
    showAlert(`Opening forms for study ${studyId} - Coming soon!`, 'info');
    // TODO: Navigate to form completion page
}

function viewMyProgress(studyId) {
    console.log('📈 View my progress in study:', studyId);
    showAlert(`Viewing progress for study ${studyId} - Coming soon!`, 'info');
    // TODO: Show progress view
}

// ==================== UTILITY FUNCTIONS ====================

function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.appendChild(alert);
    alert.style.display = 'block';
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.style.display = 'none';
        alert.remove();
    }, 5000);
}

function logout() {
    console.log('👋 Logging out...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    window.location.href = 'login.html';
}

// ==================== ERROR HANDLING ====================
window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Unhandled promise rejection:', event.reason);
    showAlert('An unexpected error occurred. Please try again.', 'error');
});