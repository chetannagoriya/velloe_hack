# ⏱️ Screen Time Tracking System - Complete Guide

## Overview
Automatic screen time tracking system for CalmNest that monitors user's time spent on the website.

---

## ✅ What It Tracks

### 📊 Metrics Tracked:
1. **Total Daily Time** - How long user spent on CalmNest today
2. **Weekly Time** - Last 7 days total usage
3. **Daily Average** - Average time per day
4. **Page-wise Breakdown** - Time spent on each page
5. **Active vs Inactive** - Only counts active usage
6. **Session History** - All past sessions

### 🎯 What It DOES Track:
- ✅ Time spent on CalmNest website
- ✅ Active browsing time (mouse/keyboard activity)
- ✅ Time on each page (Home, Dashboard, PHQ-9, etc.)
- ✅ Daily, weekly, monthly patterns
- ✅ Session start/end times

### ❌ What It DOES NOT Track:
- ❌ Total device screen time (laptop/phone)
- ❌ Other websites or apps
- ❌ Screen-on time when inactive
- ❌ Background tabs
- ❌ System-level activity

---

## 🏗️ Architecture

### Frontend (JavaScript)
**File:** `static/js/screen_time_tracker.js`

**Features:**
- Automatic initialization on page load
- Activity detection (mouse, keyboard, scroll)
- Inactivity timeout (1 minute)
- Page visibility tracking
- Periodic sync to server (30 seconds)
- LocalStorage backup
- Page-wise time tracking

### Backend (Python/Flask)
**File:** `app.py`

**Endpoints:**
1. `/api/screen-time/sync` - Sync data from client
2. `/api/screen-time/stats` - Get statistics
3. `/api/screen-time/update` - Update session data

**Storage:**
- Location: `data/screen_time/`
- Format: JSON files per day
- Filename: `YYYY-MM-DD.json`

---

## 📱 User Interface

### Dashboard Widget
**Location:** `templates/dashboard.html`

**Displays:**
- Today's total time (large display)
- 7-day chart (bar graph)
- Weekly total
- Daily average
- Usage status (healthy/moderate/high)

**Features:**
- Real-time updates (every 30 seconds)
- Color-coded status indicators
- Interactive chart
- Refresh button

---

## 🔧 How It Works

### 1. Initialization
```javascript
// Automatically starts when page loads
screenTimeTracker = new ScreenTimeTracker();
```

### 2. Activity Detection
- Monitors: mouse, keyboard, scroll, touch events
- Updates `lastActivity` timestamp
- Marks user as active

### 3. Inactivity Detection
- Checks every 5 seconds
- If no activity for 1 minute → marks inactive
- Stops counting time

### 4. Page Visibility
- Detects when tab is hidden/visible
- Pauses tracking when tab hidden
- Resumes when tab visible

### 5. Data Sync
- Syncs to server every 30 seconds
- Saves to localStorage as backup
- Sends to `/api/screen-time/sync`

### 6. Page Tracking
- Tracks time on each page separately
- Detects page changes (URL changes)
- Saves page time before switching

---

## 📊 Data Structure

### LocalStorage Format
```javascript
{
  "date": "2026-03-05",
  "totalTime": 1234567,  // milliseconds
  "lastUpdate": 1709654321000,
  "sessions": [
    {
      "sessionId": "user_abc123",
      "totalTime": 1234567,
      "lastUpdated": 1709654321000
    }
  ]
}
```

### Server Storage Format
```json
{
  "date": "2026-03-05",
  "totalTime": 1234567,
  "sessions": [
    {
      "sessionId": "user_abc123",
      "totalTime": 1234567,
      "lastUpdated": 1709654321000
    }
  ]
}
```

### Page Time Format
```javascript
{
  "page": "/dashboard",
  "time": 123456  // milliseconds
}
```

---

## 🎨 UI Components

### Today's Time Display
```
┌─────────────────────┐
│   Today             │
│   2h 34m            │ ← Large, prominent
│   ⚠️ Consider break │ ← Status indicator
└─────────────────────┘
```

### Weekly Chart
```
Bar chart showing last 7 days
Mon Tue Wed Thu Fri Sat Sun
 █   ██  ███  █   ██  █   ██
```

### Status Indicators
- ✨ Just getting started (< 30 min)
- 👍 Moderate usage (30 min - 1 hour)
- ⚠️ Consider taking a break (1-2 hours)
- 🚨 High usage - take a break! (> 2 hours)

---

## 🧪 Testing

### Manual Test:
1. Open CalmNest website
2. Browse for 2-3 minutes
3. Go to Dashboard
4. Check "Screen Time Tracker" section
5. Should show ~2-3 minutes

### Test Inactivity:
1. Open website
2. Don't touch mouse/keyboard for 1 minute
3. Time should stop counting
4. Move mouse
5. Time should resume

### Test Page Tracking:
1. Visit Home page (30 seconds)
2. Visit Dashboard (1 minute)
3. Visit PHQ-9 (30 seconds)
4. Check Dashboard widget
5. Should show breakdown by page

---

## 📈 Analytics

### Available Metrics:
- Daily usage trend
- Peak usage times
- Most visited pages
- Average session duration
- Total users (if multi-user)

### Health Insights:
- Excessive usage alerts
- Break reminders
- Healthy usage patterns
- Comparison with averages

---

## 🔒 Privacy & Security

### Data Privacy:
- ✅ Data stored locally first (LocalStorage)
- ✅ Only syncs to your own server
- ✅ No third-party tracking
- ✅ No personal data collected
- ✅ Can be cleared anytime

### User Control:
- Clear data: `localStorage.clear()`
- Disable tracking: Remove script
- View data: Browser DevTools → Application → LocalStorage

---

## 🚀 Deployment

### Production Checklist:
- [x] Frontend tracker implemented
- [x] Backend API endpoints
- [x] Dashboard widget
- [x] Data storage setup
- [x] Error handling
- [x] Privacy compliance

### Server Requirements:
- Disk space for JSON files (~1KB per day per user)
- Write permissions to `data/screen_time/`
- No special dependencies

---

## 🔮 Future Enhancements

### Potential Features:
1. **Break Reminders**
   - Popup after 1 hour
   - Suggest breathing exercises
   - 20-20-20 rule reminder

2. **Usage Goals**
   - Set daily time limits
   - Track progress
   - Achievements/badges

3. **Detailed Analytics**
   - Hourly breakdown
   - Day of week patterns
   - Month-over-month trends

4. **Export Data**
   - Download as CSV
   - Generate reports
   - Share with therapist

5. **Multi-Device Sync**
   - Track across devices
   - Unified dashboard
   - Cloud backup

6. **Wellness Insights**
   - Correlate with mood
   - Usage vs mental health
   - Personalized recommendations

---

## 🛠️ Troubleshooting

### Time Not Updating:
1. Check browser console for errors
2. Verify `screen_time_tracker.js` loaded
3. Check LocalStorage: DevTools → Application
4. Verify API endpoint working: `/api/screen-time/stats`

### Inaccurate Time:
1. Check if tab was hidden (doesn't count)
2. Verify activity detection working
3. Check inactivity timeout (1 minute)
4. Clear LocalStorage and restart

### Data Not Syncing:
1. Check network tab for API calls
2. Verify server endpoint responding
3. Check `data/screen_time/` folder exists
4. Check file permissions

---

## 📞 API Reference

### POST /api/screen-time/sync
Sync screen time data from client.

**Request:**
```json
{
  "date": "2026-03-05",
  "totalTime": 1234567,
  "lastUpdate": 1709654321000
}
```

**Response:**
```json
{
  "success": true,
  "totalTime": 1234567
}
```

### GET /api/screen-time/stats?days=7
Get statistics for last N days.

**Response:**
```json
{
  "stats": [
    {
      "date": "2026-03-05",
      "time": 1234567,
      "formatted": "20m 34s"
    }
  ],
  "totalTime": 8641000,
  "averageTime": 1234428,
  "totalFormatted": "2h 24m",
  "averageFormatted": "20m 34s"
}
```

---

## 💡 Usage Tips

### For Users:
- Check dashboard daily to monitor usage
- Take breaks when status shows ⚠️ or 🚨
- Use breathing exercises during breaks
- Set personal time goals

### For Developers:
- Customize inactivity timeout in `screen_time_tracker.js`
- Adjust sync interval for performance
- Add custom analytics as needed
- Integrate with other health metrics

---

## ✅ Summary

**Status:** ✅ Fully Implemented

**Components:**
- ✅ Frontend tracker (JavaScript)
- ✅ Backend API (Flask)
- ✅ Dashboard widget (HTML/JS)
- ✅ Data storage (JSON files)
- ✅ Real-time updates
- ✅ Privacy-focused

**Tracks:**
- ✅ CalmNest website usage only
- ✅ Active time (not idle)
- ✅ Page-wise breakdown
- ✅ Daily/weekly patterns

**Does NOT Track:**
- ❌ Total device screen time
- ❌ Other apps/websites
- ❌ Background activity

---

**Last Updated:** March 5, 2026
**Version:** 1.0
**Status:** Production Ready
