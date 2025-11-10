// ==================== DEMO DATA ====================
const demoScenarios = {
    pain: {
        title: "💊 Health Tracking Study",
        subtitle: "Simple daily data collection for symptom monitoring",
        description: "A straightforward 14-day study tracking daily symptoms, medication adherence, and sleep quality. Perfect for researchers new to digital data collection.",
        details: {
            duration: "14 days",
            participants: "Single participant or small group",
            complexity: "Beginner-friendly",
            schedule: "Daily collection at consistent time"
        },
        forms: [
            {
                name: "Daily Symptom Diary",
                frequency: "Once per day",
                fields: ["Pain level (0-10 scale)", "Location of symptoms", "Duration", "Medication taken", "Side effects"]
            },
            {
                name: "Sleep Quality Log",
                frequency: "Once per day (morning)",
                fields: ["Hours slept", "Sleep quality (1-5)", "Woke up during night", "Feeling upon waking"]
            },
            {
                name: "Medication Adherence",
                frequency: "As needed",
                fields: ["Medication name", "Dosage", "Time taken", "Missed dose (Y/N)"]
            }
        ],
        scheduling: {
            algorithm: "Simple daily schedule",
            lcm_cycle: "1 day",
            total_collections: "14 collections over 14 days",
            burden: "Low - 5 minutes per day"
        },
        outcomes: [
            "Track symptom patterns over time",
            "Monitor medication effectiveness",
            "Identify sleep quality correlations",
            "Generate compliance reports"
        ],
        calendar: generateSimpleCalendar(14) // 14 days, all same
    },
    
    depression: {
        title: "🧠 Psychology Research Study",
        subtitle: "Multi-frequency longitudinal study with validated instruments",
        description: "An 84-day (12-week) research study combining daily mood tracking with weekly standardized questionnaires and biweekly assessments. Demonstrates the power of LCM scheduling.",
        details: {
            duration: "84 days (12 weeks)",
            participants: "Medium to large cohort",
            complexity: "Intermediate",
            schedule: "LCM-optimized (Daily, Weekly, Biweekly)"
        },
        forms: [
            {
                name: "Daily Mood Tracker",
                frequency: "Once per day (evening)",
                fields: ["Overall mood (1-10)", "Energy level", "Anxiety level", "Significant events", "Sleep last night"]
            },
            {
                name: "Weekly PHQ-9",
                frequency: "Every 7 days",
                fields: ["9 depression screening questions", "Functional impairment", "Self-harm ideation"]
            },
            {
                name: "Biweekly Wellbeing Assessment",
                frequency: "Every 14 days",
                fields: ["Life satisfaction", "Social connections", "Work/study productivity", "Physical health", "Goal progress"]
            }
        ],
        scheduling: {
            algorithm: "LCM Scheduling",
            lcm_cycle: "14 days (LCM of 1, 7, 14)",
            total_collections: "84 daily + 12 weekly + 6 biweekly = 102 total",
            burden: "Medium - 10 minutes daily, 15 minutes weekly, 20 minutes biweekly"
        },
        outcomes: [
            "Identify mood patterns and triggers",
            "Track depression symptom changes",
            "Correlate daily mood with weekly assessments",
            "Generate research-quality longitudinal data",
            "Export data for statistical analysis"
        ],
        calendar: generateLCMCalendar(28) // Show 28 days (2 cycles)
    },
    
    diabetes: {
        title: "📈 Longitudinal Research Study",
        subtitle: "Complex multi-phase study with event-driven data collection",
        description: "A sophisticated research study spanning multiple phases from baseline through follow-up, with both scheduled and event-triggered data collection. Showcases advanced features like phase management and automatic progression.",
        details: {
            duration: "Variable (typically 6-12 months)",
            participants: "Structured cohort with enrollment windows",
            complexity: "Advanced",
            schedule: "Multi-phase with LCM + event-triggered"
        },
        phases: [
            {
                name: "Screening Phase",
                duration: "7 days",
                purpose: "Participant eligibility and baseline assessment",
                forms: ["Eligibility Checklist", "Informed Consent", "Demographics", "Medical History"]
            },
            {
                name: "Baseline Phase",
                duration: "14 days",
                purpose: "Establish baseline measurements",
                forms: ["Baseline Assessment", "Daily Health Log", "Initial Lab Results"]
            },
            {
                name: "Intervention Phase",
                duration: "84 days (12 weeks)",
                purpose: "Active study period with intervention",
                forms: ["Daily Compliance Log", "Weekly Assessment", "Biweekly Progress Check", "Adverse Event Report (as needed)"]
            },
            {
                name: "Follow-up Phase",
                duration: "28 days",
                purpose: "Monitor post-intervention outcomes",
                forms: ["Weekly Follow-up", "Final Assessment", "Exit Survey"]
            }
        ],
        forms: [
            {
                name: "Daily Compliance Log",
                frequency: "Once per day",
                fields: ["Intervention adherence (Y/N)", "Time spent", "Barriers encountered", "Notes"]
            },
            {
                name: "Weekly Progress Assessment",
                frequency: "Every 7 days",
                fields: ["Primary outcome measures", "Secondary outcomes", "Quality of life", "Side effects"]
            },
            {
                name: "Biweekly Check-in",
                frequency: "Every 14 days",
                fields: ["Overall progress", "Goal achievement", "Concerns", "Next steps"]
            },
            {
                name: "Adverse Event Report",
                frequency: "Event-triggered (as needed)",
                fields: ["Event description", "Severity", "Relationship to study", "Action taken", "Resolution"]
            },
            {
                name: "Phase Completion Survey",
                frequency: "End of each phase",
                fields: ["Phase experience", "Challenges faced", "Satisfaction", "Readiness for next phase"]
            }
        ],
        scheduling: {
            algorithm: "Advanced LCM + Event-driven + Phase-based",
            lcm_cycle: "14 days per intervention phase (LCM of 1, 7, 14)",
            total_collections: "Variable based on phase and events",
            burden: "High initially, medium during intervention - 15-30 minutes per day during active phase"
        },
        features: [
            "✅ Automatic phase progression based on completion criteria",
            "✅ Event-triggered forms (adverse events, milestones)",
            "✅ Conditional logic and skip patterns",
            "✅ Real-time compliance monitoring",
            "✅ Multi-role access (researchers, coordinators, participants)",
            "✅ Automated reminders and notifications",
            "✅ Phase-specific data isolation",
            "✅ Comprehensive audit trail"
        ],
        outcomes: [
            "Complete longitudinal dataset across study phases",
            "Capture both scheduled and spontaneous events",
            "Track participant journey through phases",
            "Generate compliance and retention metrics",
            "Export phase-specific or complete study data",
            "Produce regulatory-ready documentation"
        ],
        calendar: generateComplexCalendar(28) // 28 days with phases
    }
};

// ==================== CALENDAR GENERATORS ====================

function generateSimpleCalendar(days) {
    const calendar = [];
    for (let i = 1; i <= days; i++) {
        calendar.push({
            day: i,
            type: 'a',
            label: 'All Forms',
            description: 'Daily symptom diary, sleep log, medication tracking'
        });
    }
    return calendar;
}

function generateLCMCalendar(days) {
    const calendar = [];
    for (let i = 1; i <= days; i++) {
        let type, label, description;
        
        if (i === 1 || i === 15) {
            // Days where all three frequencies align (1, 7, 14)
            type = 'abc';
            label = 'ABC';
            description = 'Daily mood + Weekly PHQ-9 + Biweekly wellbeing';
        } else if (i % 7 === 1) {
            // Weekly days (also have daily)
            type = 'ab';
            label = 'AB';
            description = 'Daily mood + Weekly PHQ-9';
        } else {
            // Just daily
            type = 'a';
            label = 'A';
            description = 'Daily mood tracker only';
        }
        
        calendar.push({ day: i, type, label, description });
    }
    return calendar;
}

function generateComplexCalendar(days) {
    const calendar = [];
    for (let i = 1; i <= days; i++) {
        let type, label, description;
        
        if (i === 1) {
            type = 'baseline';
            label = 'Baseline';
            description = 'Baseline assessment + Daily log';
        } else if (i === 28) {
            type = 'eot';
            label = 'Phase End';
            description = 'Phase completion survey + All forms';
        } else if (i === 15) {
            type = 'abc';
            label = 'ABC';
            description = 'Daily + Weekly + Biweekly assessments';
        } else if (i % 7 === 1) {
            type = 'ab';
            label = 'AB';
            description = 'Daily + Weekly assessments';
        } else {
            type = 'a';
            label = 'A';
            description = 'Daily compliance log';
        }
        
        calendar.push({ day: i, type, label, description });
    }
    return calendar;
}

// ==================== MODAL FUNCTIONS ====================
function openDemo(demoKey) {
    const demo = demoScenarios[demoKey];
    if (!demo) return;
    
    const modal = document.getElementById('demoModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    // Set title
    modalTitle.textContent = demo.title;
    
    // Build modal content
    let content = `
        <div style="margin-bottom: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 0.5rem;">${demo.subtitle}</h3>
            <p style="color: #666; line-height: 1.6;">${demo.description}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: #333;">📋 Study Details</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div><strong>Duration:</strong> ${demo.details.duration}</div>
                <div><strong>Participants:</strong> ${demo.details.participants}</div>
                <div><strong>Complexity:</strong> ${demo.details.complexity}</div>
                <div><strong>Schedule:</strong> ${demo.details.schedule}</div>
            </div>
        </div>
    `;
    
    // Add calendar visualization
    content += `
        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: #333;">📅 Schedule Calendar</h4>
            <div style="background: #fff; padding: 1.5rem; border-radius: 10px; border: 2px solid #e5e7eb;">
                <div class="calendar-grid">
    `;
    
    demo.calendar.forEach((day) => {
        content += `
            <div class="day-cell" title="${day.description}">
                <div class="day-number">Day ${day.day}</div>
                <span class="day-type day-type-${day.type}">${day.label}</span>
            </div>
        `;
    });
    
    content += `
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                    <strong>Legend:</strong><br>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem; margin-top: 0.5rem;">
                        ${getLegendForDemo(demoKey)}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add phases if present (for complex studies)
    if (demo.phases) {
        content += `
            <div style="margin-bottom: 2rem;">
                <h4 style="margin-bottom: 1rem; color: #333;">📊 Study Phases</h4>
        `;
        demo.phases.forEach((phase, index) => {
            content += `
                <div style="background: #fff; border-left: 4px solid #667eea; padding: 1rem; margin-bottom: 1rem; border-radius: 5px;">
                    <h5 style="color: #667eea; margin-bottom: 0.5rem;">${index + 1}. ${phase.name}</h5>
                    <p style="color: #666; margin-bottom: 0.5rem;"><strong>Duration:</strong> ${phase.duration}</p>
                    <p style="color: #666; margin-bottom: 0.5rem;"><strong>Purpose:</strong> ${phase.purpose}</p>
                    <p style="color: #666;"><strong>Forms:</strong> ${phase.forms.join(', ')}</p>
                </div>
            `;
        });
        content += `</div>`;
    }
    
    // Add forms
    content += `
        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: #333;">📝 Data Collection Forms</h4>
    `;
    demo.forms.forEach((form, index) => {
        content += `
            <div style="background: #fff; border: 1px solid #e5e7eb; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                <h5 style="color: #333; margin-bottom: 0.5rem;">${index + 1}. ${form.name}</h5>
                <p style="color: #667eea; font-weight: 600; margin-bottom: 0.5rem;">${form.frequency}</p>
                <ul style="margin-left: 1.5rem; color: #666;">
                    ${form.fields.map(field => `<li>${field}</li>`).join('')}
                </ul>
            </div>
        `;
    });
    content += `</div>`;
    
    // Add scheduling info
    content += `
        <div style="background: #e0e7ff; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: #333;">⚙️ Scheduling Strategy</h4>
            <p style="margin-bottom: 0.5rem;"><strong>Algorithm:</strong> ${demo.scheduling.algorithm}</p>
            <p style="margin-bottom: 0.5rem;"><strong>LCM Cycle:</strong> ${demo.scheduling.lcm_cycle}</p>
            <p style="margin-bottom: 0.5rem;"><strong>Total Collections:</strong> ${demo.scheduling.total_collections}</p>
            <p><strong>Participant Burden:</strong> ${demo.scheduling.burden}</p>
        </div>
    `;
    
    // Add features if present
    if (demo.features) {
        content += `
            <div style="margin-bottom: 2rem;">
                <h4 style="margin-bottom: 1rem; color: #333;">✨ Advanced Features</h4>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                    ${demo.features.map(feature => `<p style="margin-bottom: 0.5rem;">${feature}</p>`).join('')}
                </div>
            </div>
        `;
    }
    
    // Add outcomes
    content += `
        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: #333;">🎯 Expected Outcomes</h4>
            <ul style="margin-left: 1.5rem; color: #666;">
                ${demo.outcomes.map(outcome => `<li style="margin-bottom: 0.5rem;">${outcome}</li>`).join('')}
            </ul>
        </div>
    `;
    
    // Add CTA
    content += `
        <div style="text-align: center; padding: 2rem 0;">
            <a href="register.html" style="background: #667eea; color: white; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
                Create Your Own Study Like This →
            </a>
        </div>
    `;
    
    modalBody.innerHTML = content;
    modal.classList.add('active');
}

function getLegendForDemo(demoKey) {
    const legends = {
        pain: `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-a" style="display: inline-block;">A</span>
                <span style="font-size: 0.85rem;">All Forms Daily</span>
            </div>
        `,
        depression: `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-abc" style="display: inline-block;">ABC</span>
                <span style="font-size: 0.85rem;">All 3 forms</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-ab" style="display: inline-block;">AB</span>
                <span style="font-size: 0.85rem;">Daily + Weekly</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-a" style="display: inline-block;">A</span>
                <span style="font-size: 0.85rem;">Daily only</span>
            </div>
        `,
        diabetes: `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-baseline" style="display: inline-block;">Baseline</span>
                <span style="font-size: 0.85rem;">Phase start</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-abc" style="display: inline-block;">ABC</span>
                <span style="font-size: 0.85rem;">All forms</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-ab" style="display: inline-block;">AB</span>
                <span style="font-size: 0.85rem;">Daily + Weekly</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-a" style="display: inline-block;">A</span>
                <span style="font-size: 0.85rem;">Daily only</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="day-type day-type-eot" style="display: inline-block;">Phase End</span>
                <span style="font-size: 0.85rem;">Completion</span>
            </div>
        `
    };
    
    return legends[demoKey] || '';
}

function closeDemo() {
    const modal = document.getElementById('demoModal');
    modal.classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('demoModal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeDemo();
        }
    });
});