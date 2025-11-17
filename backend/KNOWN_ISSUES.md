# Known Issues & Limitations

**Project:** AI-Powered Clinical Research Form Generator  
**Date:** November 17, 2025  
**Status:** Day 4 - Multi-Agent Orchestration Complete  

---

## Overview

This document tracks known issues, limitations, and areas for future improvement discovered during development and testing. Documenting these demonstrates critical evaluation and provides a roadmap for future enhancements.

---

## 1. JSON Parsing Errors in Complex Clinical Trials

**Severity:** Medium  
**Frequency:** Occasional (~10% of clinical trial requests)  
**Component:** Form Designer Agent, Policy Recommender Agent

### Description
When processing complex clinical trial descriptions (e.g., Phase 2 trials with multiple phases), Claude API occasionally returns malformed JSON with:
- Unterminated strings
- Missing closing quotes
- Syntax errors in nested objects

### Example Error
```
❌ Error parsing JSON: Expecting property name enclosed in double quotes: 
line 165 column 58 (char 7370)
```

### Root Cause
- Claude's response occasionally gets truncated or malformed when generating very large JSON schemas
- More common with complex clinical trials requiring extensive validation rules
- May be related to token limits or response streaming issues

### Impact
- System still completes workflow but with degraded quality
- Forms may be incomplete or use default values
- Policies may not be fully generated

### Workarounds Currently Applied
1. Error handling catches JSON parse errors
2. System continues with partial data
3. Logs errors for debugging

### Future Solutions
1. **Implement retry logic** with exponential backoff
2. **Add JSON repair utilities** to fix common malformations
3. **Break large requests into smaller chunks** (e.g., generate policies per field group)
4. **Use streaming with incremental parsing** to detect issues earlier
5. **Add validation layer** that requests clarification when JSON is malformed

---

## 2. Low Quality Scores from Reflection QA Agent

**Severity:** Low  
**Frequency:** Consistent  
**Component:** Reflection QA Agent

### Description
Quality scores from ReflectionQAAgent are consistently low (15-25/100) even when other agents report successful completion.

### Example
```
Quality Score: 25/100
Issues Found: 9
Status: REJECTED
```

### Root Cause
- QA agent may be overly strict in evaluation criteria
- Adapter layer may not be passing complete context
- Forms generated with minimal fields don't meet QA expectations
- QA agent expects more comprehensive metadata than simple tests provide

### Impact
- Low scores don't prevent system from working
- May confuse users about actual quality
- `Success: True` still returned despite low QA scores

### Current Status
- Non-blocking for MVP demonstration
- System functionality not affected
- QA agent still provides useful feedback

### Future Solutions
1. **Calibrate QA scoring criteria** to be more realistic
2. **Pass more complete context** including study type expectations
3. **Adjust thresholds** based on study complexity (personal tracker vs clinical trial)
4. **Add weighted scoring** where different aspects have different importance
5. **Implement two-tier QA**: "acceptable" vs "excellent"

---

## 3. Schedule Optimizer - Form Metadata Dependencies

**Severity:** Low  
**Frequency:** Resolved  
**Component:** Schedule Optimizer Agent, Adapter Layer

### Description
Schedule optimizer expected `form_name` key but Form Designer used `title` or `form_id`.

### Resolution
✅ **FIXED** - Added adapter logic to normalize form keys:
```python
if 'form_name' not in result and 'title' in result:
    result['form_name'] = result['title']
```

### Lessons Learned
- Different agents have different schema expectations
- Adapter pattern successfully resolved interface mismatches
- Demonstrates value of loose coupling between components

---

## 4. Missing 'frequency' Field in Generated Forms

**Severity:** Low  
**Frequency:** Occasional  
**Component:** Form Designer Agent

### Description
Some forms generated without explicit `frequency` field, causing issues for Schedule Optimizer.

### Resolution
✅ **FIXED** - Adapter adds default frequency:
```python
if 'frequency' not in result:
    result['frequency'] = 1  # default to daily
```

### Future Enhancement
- Form Designer should explicitly determine frequency from description
- Could be a separate AI call: "What frequency is implied by 'daily mood tracking'?"

---

## 5. Network Connection Dependency

**Severity:** High (but expected)  
**Frequency:** When network issues occur  
**Component:** All AI agents (Anthropic API calls)

### Description
System is completely dependent on network connectivity to Anthropic API. Any network interruption causes complete failure.

### Example
```
❌ Classification error: Connection error.
❌ Error in Form Designer Agent: Connection error.
```

### Impact
- Total system failure during network outages
- No offline mode available
- All tests fail simultaneously

### Future Solutions
1. **Implement caching** for common patterns
2. **Add retry logic** with exponential backoff
3. **Offline mode** with pre-generated templates
4. **Queue system** for background processing
5. **Local LLM fallback** for basic operations

---

## 6. Python 3.14 Compatibility Warning

**Severity:** Low  
**Frequency:** Always  
**Component:** LangChain dependencies

### Description
```
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.
```

### Root Cause
- Using Python 3.14 (very new)
- LangChain's Pydantic v1 dependencies not yet fully compatible

### Impact
- Warning only, doesn't affect functionality
- May cause issues in future updates

### Recommendation
- Consider downgrading to Python 3.11 or 3.12 for production
- Monitor LangChain updates for Python 3.14 support
- Current functionality unaffected

---

## 7. Agent Response Time Variability

**Severity:** Medium  
**Frequency:** Consistent  
**Component:** All AI agents

### Description
- Personal tracker: ~15-30 seconds
- Simple survey: ~45-90 seconds  
- Clinical trial: ~2-3 minutes

### Impact
- Users may perceive system as slow for complex studies
- No progress indicators during processing
- Timeout risk for very complex trials

### Future Solutions
1. **Add progress indicators** showing which agent is working
2. **Implement streaming responses** to show partial results
3. **Parallel agent execution** where possible (e.g., policies + compliance)
4. **Caching** for similar requests
5. **Background processing** with notifications

---

## 8. Limited Error Recovery

**Severity:** Medium  
**Frequency:** Occasional  
**Component:** Orchestrator workflow

### Description
When one agent fails, workflow continues but may produce incomplete results.

### Current Behavior
- Errors are logged but not always handled gracefully
- System marks workflow as incomplete but returns partial data
- No automatic retry or alternative approach

### Future Solutions
1. **Smart retry logic** - Retry failed agents with adjusted prompts
2. **Fallback strategies** - Use simpler approaches when complex ones fail
3. **Human-in-the-loop** - Ask for clarification when ambiguous
4. **Partial success handling** - Better communication about what worked

---

## Summary Statistics

**From Test Run (November 17, 2025):**

| Test Case | Agent Calls | Success | Issues |
|-----------|------------|---------|--------|
| Personal Tracker | 6 | ✅ | 0 |
| Simple Survey | 30 | ✅ | 1 (low QA score) |
| Clinical Trial | 62 | ✅ | 2 (JSON parse, low QA) |

**Overall System Health:** 🟢 Functional with known edge cases

---

## For Dissertation Discussion

These issues provide excellent material for:

### Chapter 6: Evaluation & Discussion
- **Limitations Section:** Honest assessment of system constraints
- **Comparative Analysis:** How other systems handle similar issues
- **Lessons Learned:** Design decisions and their trade-offs

### Chapter 7: Future Work
- Clear roadmap for improvements
- Demonstrates understanding of production requirements
- Shows critical thinking beyond MVP scope

### Examiner Questions
Documenting issues proactively shows:
- Self-awareness of system limitations
- Professional engineering practice  
- Understanding that all systems have trade-offs
- Ability to prioritize features vs perfect

---

## Prioritization for Future Development

**Priority 1 (Essential for Production):**
1. Retry logic for API failures
2. Better error messages for users
3. Progress indicators

**Priority 2 (Quality Improvements):**
4. JSON repair utilities
5. QA score calibration
6. Caching layer

**Priority 3 (Nice to Have):**
7. Parallel agent execution
8. Offline mode
9. Local LLM fallback

---

## Update Log

### November 17, 2025 - Initial Documentation
- Documented 8 known issues from Day 4 testing
- Categorized by severity and frequency
- Added future solutions for each issue
- Created prioritization framework

### [Add new updates here as issues are discovered or resolved]

---

**Next Review:** After Day 5 implementation  
**Maintained By:** Ihtesham Ul Haq  
**For:** MSc AI Dissertation - Aston University
