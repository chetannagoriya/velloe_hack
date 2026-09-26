# 🔧 Screen Time Tracking - Debug Guide

## Problem: Time Not Tracking (Showing 0m)

### Quick Fix Steps:

## 1️⃣ Test Page (Easiest Way)

Visit: `http://localhost:5000/screen-time-test`

This page shows:
- ✅ Real-time session time
- ✅ Today's total time
- ✅ Debug information
- ✅ LocalStorage data
- ✅ Tracker status

**What to check:**
- Status should show "✅ Active"
- Session time should increase every second
- LocalStorage should have data

---

## 2️⃣ Browser Console Check

1. Open website
2. Press `F12` (Developer Tools)
3. Go to "Console" tab
4. Look for:
   ```
   ✅ Screen Time Tracker initialized successfully
   Current session start: [time]
   ```

**If you see errors:**
- Check if `screen_time_tracker.js` loaded
- Check Network tab for 404 errors

---

## 3️⃣ Manual Test in Console

Open Console (F12) and run:

```javascript
// Check if tracker exists
window.getScreenTimeTracker()

// Get debug info
window.getScreenTimeTracker().getDebugInfo()

// Get today's time
window.getScreenTimeTracker().getTodayTime()

// Format time
window.getScreenTimeTracker().formatTime(123456)
```

**Expected output:**
```javascript
{
  isActive: true,
  sessionStart: "10:30:45 AM",
  lastActivity: "10:30:50 AM",
  totalActiveTime: "2m 15s",
  currentSessionTime: "5s",
  todayTotal: "2m 20s",
  currentPage: "/dashboard"
}
```

---

## 4️⃣ Check LocalStorage

1. Open DevTools (F12)
2. Go to "Application" tab
3. Click "Local Storage" → your domain
4. Look for keys starting with:
   - `screenTime_2026-03-05`
   - `pageTime_2026-03-05_/dashboard`

**Should see:**
```json
{
  "date": "2026-03-05",
  "totalTime": 135000,
  "lastUpdate": 1709654321000,
  "sessions": [...]
}
```

---

## 5️⃣ Force Refresh

Sometimes browser cache causes issues:

1. **Hard Refresh:**
   - Windows: `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. **Clear Cache:**
   - DevTools → Network tab
   - Check "Disable cache"
   - Refresh page

---

## 6️⃣ Check Server API

Test if backend is working:

```bash
# In browser console or new tab:
fetch('/api/screen-time/stats?days=7')
  .then(r => r.json())
  .then(d => console.log(d))
```

**Expected response:**
```json
{
  "stats": [...],
  "totalTime": 0,
  "averageTime": 0,
  "totalFormatted": "0m",
  "averageFormatted": "0m"
}
```

---

## 7️⃣ Common Issues & Fixes

### Issue: "Tracker not initialized"
**Fix:**
- Check if `screen_time_tracker.js` is loaded
- Look for JavaScript errors in console
- Try hard refresh (Ctrl+F5)

### Issue: Time shows 0m but I've been using
**Fix:**
- Check if you're moving mouse/keyboard (activity detection)
- Check if tab is visible (hidden tabs don't count)
- Check LocalStorage for data
- Try test page: `/screen-time-test`

### Issue: Time resets to 0
**Fix:**
- Check if LocalStorage is being cleared
- Check browser privacy settings
- Verify data is syncing to server

### Issue: Different time on different pages
**Fix:**
- This is normal - each page loads fresh
- Data syncs from LocalStorage
- Wait 1-2 seconds for data to load

---

## 8️⃣ Manual Data Entry (Testing)

If you want to test with fake data:

```javascript
// Add 15 minutes to today
const today = new Date().toISOString().split('T')[0];
const data = {
  date: today,
  totalTime: 15 * 60 * 1000, // 15 minutes in ms
  lastUpdate: Date.now(),
  sessions: []
};
localStorage.setItem(`screenTime_${today}`, JSON.stringify(data));

// Refresh dashboard
location.reload();
```

---

## 9️⃣ Reset Everything

If nothing works, reset:

```javascript
// Clear all screen time data
Object.keys(localStorage)
  .filter(k => k.startsWith('screenTime_') || k.startsWith('pageTime_'))
  .forEach(k => localStorage.removeItem(k));

// Hard refresh
location.reload();
```

---

## 🔟 Verify It's Working

After fixes, verify:

1. ✅ Visit `/screen-time-test`
2. ✅ Session time increases every second
3. ✅ Console shows no errors
4. ✅ LocalStorage has data
5. ✅ Dashboard shows time after 30 seconds
6. ✅ Time persists after page refresh

---

## 📞 Still Not Working?

### Check These:

1. **Browser Compatibility:**
   - Use Chrome, Firefox, or Edge
   - Update to latest version
   - Disable ad blockers

2. **Server Running:**
   - Flask app is running
   - No errors in terminal
   - Port 5000 accessible

3. **File Permissions:**
   - `data/screen_time/` folder exists
   - Write permissions enabled

4. **JavaScript Enabled:**
   - Check browser settings
   - No script blockers active

---

## 🎯 Expected Behavior

**After 1 minute of use:**
- Session time: ~1m
- Today total: ~1m
- Status: Active
- LocalStorage: Has data

**After 15 minutes of use:**
- Session time: ~15m
- Today total: ~15m
- Dashboard: Shows 15m
- Chart: Shows data point

**After closing and reopening:**
- Previous time persists
- New session starts
- Total accumulates

---

## 🐛 Debug Checklist

- [ ] Test page shows "Active" status
- [ ] Session time increases
- [ ] Console has no errors
- [ ] LocalStorage has data
- [ ] API endpoint responds
- [ ] Dashboard updates
- [ ] Time persists after refresh
- [ ] Chart shows data

---

**If all checks pass but still showing 0m:**
1. Wait 30 seconds (sync interval)
2. Refresh dashboard
3. Check test page
4. Clear cache and retry

---

**Last Updated:** March 5, 2026
**Status:** Debugging Guide
