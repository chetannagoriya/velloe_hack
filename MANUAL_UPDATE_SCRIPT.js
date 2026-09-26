// 🚀 MANUAL SCREEN TIME UPDATE SCRIPT
// Copy-paste this in browser console (F12) if time not showing

console.log('🔧 Starting manual screen time update...');

// Function to update display
function updateScreenTimeDisplay() {
    const tracker = window.getScreenTimeTracker ? window.getScreenTimeTracker() : null;
    
    if (!tracker) {
        console.error('❌ Tracker not found!');
        return false;
    }
    
    const time = tracker.getTodayTime();
    const formatted = tracker.formatTime(time);
    
    console.log('📊 Current time:', formatted);
    console.log('📊 Raw milliseconds:', time);
    
    // Update all possible elements
    const elements = [
        'today-screen-time',
        'session-time',
        'test-today-time',
        'current-session-time'
    ];
    
    let updated = 0;
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = formatted;
            el.style.color = '#14b8a6'; // Teal color
            el.style.fontWeight = 'bold';
            console.log('✅ Updated', id);
            updated++;
        }
    });
    
    if (updated === 0) {
        console.warn('⚠️ No elements found to update');
        console.log('Available elements:', document.querySelectorAll('[id*="time"]'));
    } else {
        console.log(`✅ Updated ${updated} element(s)`);
    }
    
    return true;
}

// Run once immediately
updateScreenTimeDisplay();

// Then update every second
const updateInterval = setInterval(() => {
    updateScreenTimeDisplay();
}, 1000);

console.log('✅ Auto-update started (every 1 second)');
console.log('To stop: clearInterval(' + updateInterval + ')');

// Return interval ID so user can stop it
updateInterval;
