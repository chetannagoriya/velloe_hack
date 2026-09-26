# Complete Analysis Workflow - Test Guide

## Overview
This guide helps you manually test the Complete Analysis Workflow end-to-end.

## Prerequisites
- Flask app running on http://127.0.0.1:5000
- Ollama running (for chatbot integration)

## Test Steps

### 1. Start Workflow
1. Open browser: http://127.0.0.1:5000
2. Click "Complete Analysis" button (purple gradient button)
3. **Expected**: Redirects to GAD-7 assessment page
4. **Verify**: Progress indicator shows "Step 1 of 5" (20%)

### 2. GAD-7 Assessment
1. Answer all 7 questions (select any values 0-3)
2. Click "Submit" button
3. **Expected**: Redirects to PHQ-9 assessment page
4. **Verify**: Progress indicator shows "Step 2 of 5" (40%)

### 3. PHQ-9 Assessment
1. Answer all 9 questions (select any values 0-3)
2. Click "Submit" button
3. **Expected**: Redirects to Emotion Detection page
4. **Verify**: Progress indicator shows "Step 3 of 5" (60%)

### 4. Emotion Detection
1. Click "Start Camera" button
2. Allow camera access when prompted
3. Wait for face detection (should show emotion and confidence)
4. Click "Continue" button
   - **OR** Click "Skip" if camera not available
5. **Expected**: Redirects to Lifestyle Questionnaire
6. **Verify**: Progress indicator shows "Step 4 of 5" (80%)

### 5. Lifestyle Questionnaire
1. Fill in all 8 text fields with any responses:
   - Hobbies kya hai?
   - Recently kya aur kesa kha rahe ho?
   - Daily life kesi hai?
   - Sleeping time kitna follow kar rahe ho?
   - Meditation kar rahe ho ya nahi?
   - Exercise kar rahe ho?
   - Kya karke good feel karte ho?
   - Konsi cheezein happy feel karwati hain?
2. Click "Submit Responses" button
3. **Expected**: Redirects to Analysis Report page
4. **Verify**: Progress indicator shows "Step 5 of 5" (100%)

### 6. Analysis Report
1. **Verify** report displays:
   - GAD-7 score and severity (color-coded badge)
   - PHQ-9 score and severity (color-coded badge)
   - Emotion detection result (or "Skipped" if skipped)
   - All 8 lifestyle questionnaire responses
2. Click "Concern with Jaya" button
3. **Expected**: Opens chatbot with pre-loaded assessment context
4. **Verify**: Chatbot page opens

### 7. Chatbot Integration
1. In chatbot, type a message like "How can you help me?"
2. **Expected**: Jaya responds with personalized support based on assessment data
3. **Verify**: Response references your assessment scores/severity

## Success Criteria
✅ All 5 workflow steps complete without errors
✅ Progress indicator updates correctly at each step
✅ All assessment data is saved and displayed in report
✅ Chatbot receives and uses assessment context
✅ Session data persists in `data/sessions/` directory

## Troubleshooting

### Workflow stops after GAD-7/PHQ-9
- Check browser console for JavaScript errors
- Verify Flask app is running without errors
- Check Flask logs for backend errors

### Camera access fails
- Click "Skip" button to continue workflow
- Verify browser has camera permissions
- Check if camera is being used by another app

### Chatbot doesn't respond
- Verify Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Pull model if needed: `ollama pull llama3.2:3b`

### Session data not found
- Check `data/sessions/` directory exists
- Verify file permissions allow read/write
- Check Flask session is configured correctly

## Files to Check
- `app.py` - All workflow routes
- `workflow_orchestrator.py` - Workflow state management
- `data_store.py` - Session data persistence
- `templates/gad7.html` - GAD-7 with workflow mode
- `templates/phq9.html` - PHQ-9 with workflow mode
- `templates/emotion.html` - Emotion detection with workflow mode
- `templates/workflow_lifestyle.html` - Lifestyle questionnaire
- `templates/workflow_report.html` - Analysis report
- `templates/components/workflow_progress.html` - Progress indicator

## Data Privacy
- Session files use UUID only (no PII in filename)
- `data/sessions/` is in `.gitignore`
- All processing happens server-side (secure)
