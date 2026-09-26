/**
 * CalmNest Screen Time Tracker
 * Tracks user's time spent on the website
 */

class ScreenTimeTracker {
    constructor() {
        this.sessionStart = Date.now();
        this.lastActivity = Date.now();
        this.totalActiveTime = 0;
        this.isActive = true;
        this.inactivityTimeout = 60000; // 1 minute
        this.syncInterval = 30000; // Sync every 30 seconds
        this.currentPage = window.location.pathname;
        this.pageStartTime = Date.now();
        
        this.init();
    }
    
    init() {
        // Load existing session data
        this.loadSessionData();
        
        // Track user activity
        this.setupActivityListeners();
        
        // Track page visibility
        this.setupVisibilityListener();
        
        // Periodic sync
        this.startPeriodicSync();
        
        // Track page changes
        this.setupPageTracking();
        
        // Save on page unload
        window.addEventListener('beforeunload', () => this.saveSession());
    }
    
    setupActivityListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
                if (!this.isActive) {
                    this.isActive = true;
                    this.sessionStart = Date.now();
                }
            }, { passive: true });
        });
        
        // Check for inactivity
        setInterval(() => {
            if (Date.now() - this.lastActivity > this.inactivityTimeout) {
                if (this.isActive) {
                    this.isActive = false;
                    this.saveSession();
                }
            }
        }, 5000);
    }
    
    setupVisibilityListener() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.isActive = false;
                this.saveSession();
            } else {
                this.isActive = true;
                this.sessionStart = Date.now();
                this.lastActivity = Date.now();
            }
        });
    }
    
    setupPageTracking() {
        // Track page changes (for SPAs)
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                this.savePageTime();
                this.currentPage = window.location.pathname;
                this.pageStartTime = Date.now();
                lastUrl = url;
            }
        }).observe(document, { subtree: true, childList: true });
    }
    
    startPeriodicSync() {
        setInterval(() => {
            if (this.isActive) {
                this.saveSession();
            }
        }, this.syncInterval);
    }
    
    loadSessionData() {
        try {
            const today = this.getTodayKey();
            const data = localStorage.getItem(`screenTime_${today}`);
            
            if (data) {
                const parsed = JSON.parse(data);
                this.totalActiveTime = parsed.totalTime || 0;
                console.log('📂 Loaded session data:', this.formatTime(this.totalActiveTime));
            }
        } catch (error) {
            console.warn('⚠️ LocalStorage blocked or unavailable:', error.message);
            console.log('📝 Tracking will continue in memory only (data won\'t persist)');
            // Continue without localStorage - track in memory only
        }
    }
    
    saveSession() {
        if (!this.isActive) return;
        
        const sessionDuration = Date.now() - this.sessionStart;
        this.totalActiveTime += sessionDuration;
        this.sessionStart = Date.now();
        
        try {
            const today = this.getTodayKey();
            const data = {
                date: today,
                totalTime: this.totalActiveTime,
                lastUpdate: Date.now(),
                sessions: this.getSessions()
            };
            
            localStorage.setItem(`screenTime_${today}`, JSON.stringify(data));
            
            // Save page time
            this.savePageTime();
            
            // Sync to server
            this.syncToServer(data);
        } catch (error) {
            console.warn('⚠️ Could not save to LocalStorage:', error.message);
            // Still sync to server even if localStorage fails
            this.syncToServer({
                date: this.getTodayKey(),
                totalTime: this.totalActiveTime,
                lastUpdate: Date.now()
            });
        }
    }
    
    savePageTime() {
        const pageDuration = Date.now() - this.pageStartTime;
        const pageKey = `pageTime_${this.getTodayKey()}_${this.currentPage}`;
        
        let pageData = localStorage.getItem(pageKey);
        pageData = pageData ? JSON.parse(pageData) : { page: this.currentPage, time: 0 };
        pageData.time += pageDuration;
        
        localStorage.setItem(pageKey, JSON.stringify(pageData));
        this.pageStartTime = Date.now();
    }
    
    getSessions() {
        const sessions = [];
        const keys = Object.keys(localStorage);
        
        keys.forEach(key => {
            if (key.startsWith('screenTime_')) {
                const data = JSON.parse(localStorage.getItem(key));
                sessions.push({
                    date: data.date,
                    time: data.totalTime
                });
            }
        });
        
        return sessions;
    }
    
    async syncToServer(data) {
        try {
            await fetch('/api/screen-time/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error('Failed to sync screen time:', error);
        }
    }
    
    getTodayKey() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    }
    
    getTodayTime() {
        try {
            const today = this.getTodayKey();
            const data = localStorage.getItem(`screenTime_${today}`);
            if (data) {
                const parsed = JSON.parse(data);
                return parsed.totalTime || 0;
            }
        } catch (error) {
            // LocalStorage blocked, use in-memory value
            console.warn('⚠️ Using in-memory time (LocalStorage blocked)');
        }
        
        // Fallback: return current session time
        if (this.isActive) {
            return this.totalActiveTime + (Date.now() - this.sessionStart);
        }
        return this.totalActiveTime;
    }
    
    getWeeklyTime() {
        let total = 0;
        const now = new Date();
        
        for (let i = 0; i < 7; i++) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
            const data = localStorage.getItem(`screenTime_${key}`);
            if (data) {
                total += JSON.parse(data).totalTime;
            }
        }
        
        return total;
    }
    
    getPageTimes() {
        const today = this.getTodayKey();
        const pageTimes = {};
        const keys = Object.keys(localStorage);
        
        keys.forEach(key => {
            if (key.startsWith(`pageTime_${today}_`)) {
                const data = JSON.parse(localStorage.getItem(key));
                pageTimes[data.page] = data.time;
            }
        });
        
        return pageTimes;
    }
    
    formatTime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }
    
    // Debug helper
    getDebugInfo() {
        return {
            isActive: this.isActive,
            sessionStart: new Date(this.sessionStart).toLocaleTimeString(),
            lastActivity: new Date(this.lastActivity).toLocaleTimeString(),
            totalActiveTime: this.formatTime(this.totalActiveTime),
            currentSessionTime: this.formatTime(Date.now() - this.sessionStart),
            todayTotal: this.formatTime(this.getTodayTime()),
            currentPage: this.currentPage
        };
    }
}

// Initialize tracker
let screenTimeTracker;

function initializeScreenTimeTracker() {
    try {
        screenTimeTracker = new ScreenTimeTracker();
        console.log('✅ Screen Time Tracker initialized successfully');
        console.log('Current session start:', new Date(screenTimeTracker.sessionStart));
        
        // Update display immediately
        setTimeout(() => {
            if (window.updateScreenTimeDisplay) {
                window.updateScreenTimeDisplay();
            }
        }, 1000);
    } catch (error) {
        console.error('❌ Failed to initialize Screen Time Tracker:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeScreenTimeTracker);
} else {
    initializeScreenTimeTracker();
}

// Export for use in other scripts
window.ScreenTimeTracker = ScreenTimeTracker;
window.getScreenTimeTracker = () => screenTimeTracker;
