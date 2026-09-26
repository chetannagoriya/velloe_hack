# Workflow Session Fix - Force New Session

## Issue
Jab user "Complete Analysis" button click karta tha, toh:
1. Purane completed session ko resume karne ki koshish hoti thi
2. GAD-7 ke badle PHQ-9 ya koi aur step show hota tha
3. User ko lagta tha ki test already completed hai

## Root Cause
Session resume functionality purane completed sessions ko bhi resume karne ki koshish kar rahi thi, even though `can_resume_workflow()` function complete sessions ko reject karta hai. Lekin agar session complete nahi tha aur user ne beech mein chhod diya tha, toh wo wahi se resume ho jata tha.

## Solution Applied

### 1. Added Force New Parameter
`/complete-analysis/start` route mein `?new=true` parameter support add kiya:
- Jab `new=true` ho, toh purana session clear kar ke naya session start kare
- Default behavior: Resume incomplete sessions (good for user experience)
- Explicit new: Always start fresh (good for "Complete Analysis" button)

### 2. Updated All "Start" Buttons
Sabhi buttons ko `?new=true` parameter ke saath update kiya:
- Home page: "Complete Analysis" button
- Dashboard: "New Analysis" button
- Dashboard empty state: "Start Complete Analysis" button

## Technical Changes

### app.py
```python
@app.route("/complete-analysis/start")
def start_complete_analysis():
    # Check if user wants to force a new session
    force_new = request.args.get('new', 'false').lower() == 'true'
    
    if existing_session_id and not force_new:
        # Try to resume
        if can_resume_workflow(existing_data):
            return redirect(resume_url)
    elif force_new and existing_session_id:
        # Force new session, clear old one
        session.pop('workflow_session_id', None)
    
    # Create new session...
```

### templates/index.html
```html
<!-- Before -->
<a href="{{ url_for('start_complete_analysis') }}">

<!-- After -->
<a href="{{ url_for('start_complete_analysis') }}?new=true">
```

### templates/dashboard.html
```html
<!-- Before -->
<a href="/complete-analysis/start">

<!-- After -->
<a href="/complete-analysis/start?new=true">
```

### static/js/main.js
```javascript
// Before
<a href="/complete-analysis/start">

// After
<a href="/complete-analysis/start?new=true">
```

## Behavior Now

### Scenario 1: Fresh Start (No Previous Session)
- User clicks "Complete Analysis"
- New session created
- Redirects to GAD-7 (Step 1)
- ✅ Works correctly

### Scenario 2: Incomplete Session Exists
- User clicks "Complete Analysis" with `?new=true`
- Old session cleared
- New session created
- Redirects to GAD-7 (Step 1)
- ✅ Always starts fresh

### Scenario 3: Direct URL Access (No Parameter)
- User goes to `/complete-analysis/start` directly
- If incomplete session exists, resumes from last step
- If no session or expired, creates new
- ✅ Resume functionality preserved

### Scenario 4: Completed Session Exists
- User clicks "Complete Analysis" with `?new=true`
- Old completed session cleared
- New session created
- Redirects to GAD-7 (Step 1)
- ✅ Can start new assessment

## Benefits

✅ **Always Fresh Start**: "Complete Analysis" button always starts from beginning
✅ **Resume Preserved**: Direct URL access still allows resume
✅ **User Control**: Explicit parameter gives control
✅ **No Confusion**: Users won't see "already completed" state
✅ **Multiple Assessments**: Users can do multiple assessments easily

## Testing

### Test Case 1: First Time User
1. Click "Complete Analysis"
2. **Expected**: Starts at GAD-7
3. **Result**: ✅ Pass

### Test Case 2: Incomplete Session
1. Start assessment, complete GAD-7
2. Close browser
3. Come back, click "Complete Analysis"
4. **Expected**: Starts fresh at GAD-7 (not PHQ-9)
5. **Result**: ✅ Pass

### Test Case 3: Completed Session
1. Complete full assessment
2. Click "Complete Analysis" again
3. **Expected**: Starts fresh at GAD-7
4. **Result**: ✅ Pass

### Test Case 4: Resume Functionality
1. Start assessment, complete GAD-7
2. Close browser
3. Go directly to `/complete-analysis/start` (no parameter)
4. **Expected**: Resumes at PHQ-9
5. **Result**: ✅ Pass

## Status
✅ **FIXED** - Complete Analysis button now always starts fresh workflow
