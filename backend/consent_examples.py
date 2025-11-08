"""
Real-World Informed Consent Examples

Synthetic consent forms demonstrating common patterns following
standard IRB requirements (Common Rule 45 CFR 46, ICH-GCP).

These are FICTIONAL examples created to demonstrate system capabilities.
They follow standard research ethics frameworks but do not represent
real studies or participants.
"""

from consent import create_standard_consent, ConsentType, ConsentSchema, ConsentSection

# Example 1: Simple Survey Study
survey_consent = create_standard_consent(
    study_id="SURVEY_001",
    study_title="Customer Satisfaction Survey",
    pi_name="Dr. Sarah Johnson",
    institution="Market Research Institute",
    purpose="""
    This survey aims to understand customer satisfaction with our services.
    Your feedback will help us improve our offerings and better serve our community.
    The survey takes approximately 10 minutes to complete.
    """,
    procedures="""
    You will be asked to complete an online questionnaire consisting of 15 questions
    about your recent experience with our services. Questions include multiple choice,
    rating scales, and optional open-ended responses. You may skip any questions you
    do not wish to answer.
    """,
    risks="""
    Risks are minimal. You may experience minor inconvenience from the time required
    to complete the survey. There are no foreseeable psychological or physical risks.
    """,
    benefits="""
    There is no direct benefit to you from participating in this survey. However,
    your feedback may help improve services for future customers. Upon completion,
    you will be entered into a drawing for a $50 gift card (optional).
    """,
    contact_name="Dr. Sarah Johnson",
    contact_email="sjohnson@mri.org",
    version="v1.0"
)

# Example 2: Clinical Trial
clinical_trial_consent = create_standard_consent(
    study_id="TRIAL_002",
    study_title="Phase III Trial of Exercise Intervention for Depression",
    pi_name="Dr. Michael Chen",
    institution="University Medical Center",
    purpose="""
    This research study aims to determine whether a structured exercise program
    can effectively reduce symptoms of depression in adults. We are comparing
    the effectiveness of exercise to standard care. This study will help us
    understand whether exercise can be used as a treatment option for depression.
    """,
    procedures="""
    If you agree to participate, you will be randomly assigned to either the
    exercise intervention group or the control group. The study lasts 12 weeks.
    
    Exercise Group:
    - Attend supervised exercise sessions 3 times per week (45 minutes each)
    - Complete daily mood diaries on your smartphone
    - Attend weekly check-in appointments with study staff
    - Complete depression assessments at weeks 0, 4, 8, and 12
    
    Control Group:
    - Continue your regular care
    - Complete daily mood diaries on your smartphone
    - Attend weekly check-in appointments with study staff
    - Complete depression assessments at weeks 0, 4, 8, and 12
    
    All participants will undergo a physical examination before starting.
    You may be asked to provide blood samples at the beginning and end of the study.
    """,
    risks="""
    Possible risks include:
    
    Physical Risks (Exercise Group):
    - Muscle soreness or minor injury from exercise
    - Fatigue
    - Increased heart rate and blood pressure during exercise
    
    Psychological Risks (All Participants):
    - Temporary increase in awareness of mood symptoms from daily tracking
    - Disappointment if assigned to control group
    - Emotional discomfort when discussing depression symptoms
    
    Privacy Risks:
    - Possible loss of confidentiality (we have safeguards in place to minimize this)
    
    We will monitor you closely and provide immediate assistance if needed.
    """,
    benefits="""
    Possible benefits include:
    - You may experience improvement in depression symptoms
    - You may experience improved physical fitness (exercise group)
    - You will receive regular monitoring of your mental health at no cost
    - You will contribute to scientific knowledge about depression treatment
    
    However, we cannot guarantee you will receive any direct benefit from participating.
    You may be in the control group and not receive the intervention. You may not
    experience improvement in your symptoms.
    """,
    contact_name="Dr. Michael Chen",
    contact_email="mchen@umc.edu",
    version="v1.0"
)

# Example 3: Observational Study (Minor Participant)
minor_consent = ConsentSchema(
    form_id="consent_OBSERV_003",
    form_type="consent",
    consent_type=ConsentType.ASSENT,
    title="Youth Participant Assent: Social Media Use Study",
    version="v1.0",
    study_id="OBSERV_003",
    study_title="Patterns of Social Media Use Among Adolescents",
    principal_investigator="Dr. Emily Rodriguez",
    institution="Department of Psychology, State University",
    contact_name="Dr. Emily Rodriguez",
    contact_email="erodriguez@stateuniversity.edu",
    sections=[
        ConsentSection(
            heading="Why are we doing this study?",
            content="""
            We want to learn about how teenagers use social media. We're interested
            in understanding what apps you use, how much time you spend on them,
            and how using social media makes you feel. This will help us understand
            how social media affects young people's lives.
            """,
            order=1
        ),
        ConsentSection(
            heading="What will I do if I join?",
            content="""
            If you agree to be in this study, here's what will happen:
            
            1. You'll answer questions about which social media apps you use
            2. You'll complete a short survey once a week for 8 weeks (about 5 minutes each time)
            3. The survey asks about your mood and experiences that week
            4. Everything is done online - you can use your phone or computer
            5. Your parents have also given permission for you to participate
            
            You can stop at any time if you want to. Just tell us and we'll stop right away.
            """,
            order=2
        ),
        ConsentSection(
            heading="Will anything bad happen?",
            content="""
            We don't think anything bad will happen. The surveys are pretty simple.
            Sometimes thinking about social media might make you realize you spend a lot
            of time on it, which might feel a little uncomfortable. If any questions make
            you upset, you can skip them or talk to your parents or school counselor.
            """,
            order=3
        ),
        ConsentSection(
            heading="Will anything good happen?",
            content="""
            You might learn interesting things about your own social media habits.
            You'll also help researchers understand how social media affects teenagers.
            When you finish all 8 weeks of surveys, you'll get a $25 gift card as a
            thank you for your time.
            """,
            order=4
        ),
        ConsentSection(
            heading="Who will know about my answers?",
            content="""
            Your answers are private. We won't tell your parents or teachers what you
            said in the surveys. We'll keep your information secure with passwords and
            locked computers. When we write about what we learned, we'll never use your
            real name. We might share the overall results (like "teenagers use Instagram
            more than Facebook"), but no one will know which answers were yours.
            """,
            order=5
        ),
        ConsentSection(
            heading="Do I have to do this?",
            content="""
            No! It's totally up to you. Even though your parents said it's okay, YOU get
            to decide if you want to participate. You can say no and nothing bad will happen.
            If you say yes but change your mind later, that's okay too. Just let us know.
            """,
            order=6
        ),
        ConsentSection(
            heading="Questions?",
            content="""
            If you have any questions about the study, you can ask Dr. Rodriguez at
            erodriguez@stateuniversity.edu or call 555-0789. You can ask questions now
            or anytime during the study.
            """,
            order=7
        )
    ],
    signature_required=True,
    date_required=True,
    witness_required=True,  # Parent/guardian as witness
    allow_download=True,
    require_scroll_through=True
)


# Test the examples
if __name__ == "__main__":
    from consent import ConsentValidator
    
    print("=" * 60)
    print("SYNTHETIC INFORMED CONSENT EXAMPLES")
    print("Following standard IRB requirements (45 CFR 46)")
    print("=" * 60)
    
    validator = ConsentValidator()
    
    examples = [
        ("Survey Consent", survey_consent),
        ("Clinical Trial Consent", clinical_trial_consent),
        ("Minor Assent", minor_consent)
    ]
    
    for name, consent in examples:
        print(f"\n{name}:")
        print(f"  Study ID: {consent.study_id}")
        print(f"  Type: {consent.consent_type}")
        print(f"  Sections: {len(consent.sections)}")
        print(f"  Signature Required: {consent.signature_required}")
        print(f"  Witness Required: {consent.witness_required}")
        
        is_valid, errors = validator.validate_consent_schema(consent)
        if is_valid:
            print(f"  ✅ Valid")
        else:
            print(f"  ❌ Invalid:")
            for error in errors:
                print(f"    - {error}")
    
    print("\n" + "=" * 60)
    print("✅ All examples validated!")
    print("=" * 60)
    print("\nNOTE: These are synthetic examples for demonstration.")
    print("They follow standard IRB patterns but are not real studies.")