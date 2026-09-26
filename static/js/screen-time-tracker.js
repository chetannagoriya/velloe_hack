/**
 * Screen Time Tracker for CalmNest
 * Tracks user's active time on the website
 */

class ScreenTimeTracker {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.startTime = Date.now();
        this.lastActivityTime = Date.now();
        this.totalActiveTime = 0;
        this.isActive = true;
        this.inactivityThreshold = 30000; // 30 seconds
        this.saveInterval = 10000; // Save every 10 seconds
        
        this.init();
    }
    
    init() {
        // Load existing session time
        this.loadSessionTime();
        
        // Track user activity
        this.setupActivityListeners();
        
        // Start tracking loop
        this.startTracking();
        
        // Save on page unload
        window.addEventListener('beforeunload', () => this.saveSessionTime());
        
        // Handle visibility change (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleInactive();
            } else {
                this.handleActive();
            }
        });
    }
    
    getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('calmnest_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('calmnest_session_id', sessionId);
        }
        return sessionId;
    }
    
    setupActivityListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivityTime = Date.now();
                if (!this.isActive) {
                    this.handleActive();
                }
            }, { passive: true });
        });
    }
    
    startTracking() {
        setInterval(() => {
            const now = Date.now();
            const timeSinceActivity = now - this.lastActivityTime;
            
            // Check if user is inactive
            if (timeSinceActivity > this.inactivityThreshold && this.isActive) {
                this.handleInactive();
            }
            
            // If active, add time
            if (this.isActive && !document.hidden) {
                this.totalActiveTime += 1000; // Add 1 second
            }
        }, 1000);
        
        // Save periodically
        setInterval(() => {
            this.saveSessionTime();
        }, this.saveInterval);
    }
    
    handleActive() {
        this.isActive = true;
        this.lastActivityTime = Date.now();
    }
    
    handleInactive() {
        this.isActive = false;
    }
    
    loadSessionTime() {
        const today = this.getTodayKey();
        const savedData = localStorage.getItem(`screen_time_${today}`);
        
        if (savedData) {
            const data = JSON.parse(savedData);
            this.totalActiveTime = data.totalTime || 0;
        }
    }
    
    saveSessionTime() {
        const today = this.getTodayKey();
        const data = {
            date: today,
            totalTime: this.totalActiveTime,
            lastUpdated: Date.now(),
            sessionId: this.sessionId
        };
        
        localStorage.setItem(`screen_time_${today}`, JSON.stringify(data));
        
        // Also send to server
        this.sendToServer(data);
    }
    
    async sendToServer(data) {
        try {
            await fetch('/api/screen-time/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error('Failed to save screen time:', error);
        }
    }
    
    getTodayKey() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    }
    
    getFormattedTime() {
        const seconds = Math.floor(this.totalActiveTime / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
    
    getTotalTime() {
        return this.totalActiveTime;
    }
}

// Initialize tracker when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.screenTimeTracker = new ScreenTimeTracker();
    });
} else {
    window.screenTimeTracker = new ScreenTimeTracker();
}

// Utility functions for getting screen time data
window.getScreenTimeData = function(days = 7) {
    const data = [];
    const now = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        
        const savedData = localStorage.getItem(`screen_time_${key}`);
        if (savedData) {
            const parsed = JSON.parse(savedData);
            data.push({
                date: key,
                time: parsed.totalTime || 0
            });
        } else {
            data.push({
                date: key,
                time: 0
            });
        }
    }
    
    return data;
};

window.getTodayScreenTime = function() {
    if (window.screenTimeTracker) {
        return window.screenTimeTracker.getTotalTime();
    }
    return 0;
};

window.getFormattedScreenTime = function() {
    if (window.screenTimeTracker) {
        return window.screenTimeTracker.getFormattedTime();
    }
    return '0s';
};
