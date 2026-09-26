// CalmNest – Frontend JavaScript (streamlined)
//
// Core features:
// - Live camera-based emotion detection (face-api.js)
// - Real-time Chart.js emotion graph
// - PHQ-9 and GAD-7 self-assessments
// - Dashboard with localStorage persistence
// - Breathing exercise and supportive chatbot
//
// Notes:
// - All user data is stored in localStorage only (no backend database).
// - Emotion detection now uses face-api.js in the browser.

// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // setupBreathingText is deprecated in favour of setupBreathingExercise
    setupEmotionPage();
    setupPhq9();
    setupGad7();
    setupDashboard();
    setupBreathingExercise();
    setupChatbotWidget();
});

// ==============================
// AI Emotion Detection (face-api.js browser-based)
// ==============================

function setupEmotionPage() {
    const video = document.getElementById("emotion-video");
    const canvas = document.getElementById("emotion-canvas");
    const startBtn = document.getElementById("start-emotion-btn");
    const captureBtn = document.getElementById("capture-emotion-btn");
    const emojiEl = document.getElementById("emotion-emoji");
    const labelEl = document.getElementById("emotion-label");
    const confEl = document.getElementById("emotion-confidence");
    const msgEl = document.getElementById("emotion-message");
    const chartCanvas = document.getElementById("emotion-realtime-chart");

    if (!video || !canvas || !startBtn || !captureBtn || !emojiEl || !labelEl || !confEl || !msgEl || !chartCanvas) {
        return;
    }

    const ctx = canvas.getContext("2d");
    let mediaStream = null;
    let detectInterval = null; // for live detection loop
    let isPredicting = false; // Prevent overlapping requests

    // Emotion history for the live chart (in-memory, last ~60 points)
    const emotionHistory = [];
    const emotionOrder = ["Angry", "Fear", "Happy", "Neutral", "Sad", "Surprise"]; // same as backend

    const chart = new Chart(chartCanvas, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Emotion (index)",
                    data: [],
                    borderColor: "#4f8ae9",
                    backgroundColor: "rgba(79,138,233,0.15)",
                    tension: 0.3,
                    pointRadius: 2,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: (value) => emotionOrder[value] || "",
                        stepSize: 1,
                    },
                    min: 0,
                    max: emotionOrder.length - 1,
                },
            },
            animation: false,
        },
    });

    function updateChart(label, emotionLabel) {
        const idx = emotionOrder.indexOf(emotionLabel);
        if (idx === -1) return;

        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(idx);

        // Keep only last 60 points
        if (chart.data.labels.length > 60) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }

    function saveEmotionToLocalHistory(emotionLabel, confidence) {
        const now = Date.now();
        const entry = { time: now, emotion: emotionLabel, confidence: confidence, score: getEmotionScore(emotionLabel) };
        try {
            const raw = localStorage.getItem("emotionData") || "[]";
            const arr = JSON.parse(raw);
            arr.push(entry);
            // Keep last 200 entries to avoid unbounded growth
            while (arr.length > 200) arr.shift();
            localStorage.setItem("emotionData", JSON.stringify(arr));
        } catch (e) {
            console.warn("Could not save emotion history:", e);
        }
    }

    function getEmotionScore(emotion) {
        const scores = {
            "Happy": 8,
            "Surprise": 6,
            "Neutral": 5,
            "Fear": 3,
            "Sad": 2,
            "Angry": 1
        };
        return scores[emotion] || 5;
    }

    async function startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            labelEl.textContent = "Camera is not supported in this browser.";
            return;
        }

        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = mediaStream;
            video.play().catch(e => console.error("Video play failed:", e));
            // Start live detection loop if not already running
            if (!detectInterval) {
                detectInterval = setInterval(() => {
                    captureAndPredict(false);
                }, 1500); // every 1.5 seconds
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            labelEl.textContent = "Camera access was denied or not available.";
        }
    }

    async function captureAndPredict(fromButton = true) {
        if (!mediaStream) {
            if (fromButton) {
                labelEl.textContent = "Please start the camera first.";
            }
            return;
        }

        // Prevent overlap if called automatically and a request is already pending
        if (!fromButton && isPredicting) return;

        const width = canvas.width;
        const height = canvas.height;
        ctx.drawImage(video, 0, 0, width, height);

        const dataUrl = canvas.toDataURL("image/png");

        if (fromButton) {
            labelEl.textContent = "Detecting emotion...";
            confEl.textContent = "";
            msgEl.textContent = "";
        }

        isPredicting = true;
        try {
            const response = await fetch("/predict_emotion", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: dataUrl }),
            });

            const data = await response.json();
            if (!data.success) {
                if (fromButton) {
                    labelEl.textContent = data.error || "Could not detect emotion.";
                }
                return;
            }

            const emotion = data.emotion;
            const confidence = data.confidence;
            emojiEl.textContent = data.emoji || "🙂";
            labelEl.textContent = `Detected: ${emotion}`;
            confEl.textContent = `Confidence: ${confidence}%`;
            msgEl.textContent = data.message || "";

            const timeLabel = new Date().toLocaleTimeString();
            updateChart(timeLabel, emotion);
            saveEmotionToLocalHistory(emotion, confidence);
            saveCurrentMood(emotion);
        } catch (err) {
            console.error("Error calling /predict_emotion:", err);
            if (fromButton) {
                labelEl.textContent = "Error while talking to the server.";
            }
        } finally {
            isPredicting = false;
        }
    }

    startBtn.addEventListener("click", startCamera);
    captureBtn.addEventListener("click", () => captureAndPredict(true));

    // Clean up camera and interval if the user leaves the page
    window.addEventListener("beforeunload", () => {
        if (detectInterval) {
            clearInterval(detectInterval);
            detectInterval = null;
        }
        if (mediaStream) {
            mediaStream.getTracks().forEach((t) => t.stop());
        }
    });
}

// Helper to store the most recent mood label in localStorage
function saveCurrentMood(emotionLabel) {
    try {
        localStorage.setItem(
            "current_mood",
            JSON.stringify({ emotion: emotionLabel, time: Date.now() })
        );
    } catch (e) {
        console.warn("Could not save current mood:", e);
    }
}

// ==============================
// PHQ-9 scoring (frontend only)
// ==============================

function setupPhq9() {
    const form = document.getElementById("phq9-form");
    const resultDiv = document.getElementById("phq9-result");

    if (!form || !resultDiv) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        let total = 0;
        let allAnswered = true;

        for (let i = 1; i <= 9; i++) {
            const name = `q${i}`;
            const selected = form.querySelector(`input[name="${name}"]:checked`);
            if (!selected) {
                allAnswered = false;
                continue;
            }
            total += parseInt(selected.value, 10);
        }

        if (!allAnswered) {
            alert('Please answer all questions to get your score.');
            return;
        }

        // Save to localStorage
        const phq9Data = JSON.parse(localStorage.getItem('phq9Data') || '[]');
        phq9Data.push({
            score: total,
            timestamp: new Date().toISOString(),
            level: getDepressionLevel(total)
        });
        localStorage.setItem('phq9Data', JSON.stringify(phq9Data));

        // Show results
        const scoreDisplay = document.getElementById('score-display');
        const interpretationText = document.getElementById('interpretation-text');
        const recommendationText = document.getElementById('recommendation-text');
        
        if (scoreDisplay) scoreDisplay.textContent = total;
        
        let interpretation, recommendation;
        if (total <= 4) {
            interpretation = "Minimal depression";
            recommendation = "Your symptoms suggest minimal depression. Continue to monitor your mental health and practice self-care strategies like regular exercise, good sleep, and social connections.";
        } else if (total <= 9) {
            interpretation = "Mild depression";
            recommendation = "Your symptoms suggest mild depression. Consider talking to a friend or family member, practicing stress management techniques, and monitoring your symptoms. If symptoms persist, consider professional help.";
        } else if (total <= 14) {
            interpretation = "Moderate depression";
            recommendation = "Your symptoms suggest moderate depression. It's recommended to speak with a healthcare professional about your symptoms. They can help determine the best treatment approach for you.";
        } else {
            interpretation = "Moderately severe to severe depression";
            recommendation = "Your symptoms suggest significant depression. It's important to seek professional help from a healthcare provider. They can provide appropriate treatment and support.";
        }
        
        if (interpretationText) interpretationText.textContent = interpretation;
        if (recommendationText) recommendationText.textContent = recommendation;
        
        resultDiv.classList.remove('hidden');
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    });
}

function getDepressionLevel(score) {
    if (score <= 4) return 'Minimal';
    if (score <= 9) return 'Mild';
    if (score <= 14) return 'Moderate';
    return 'Severe';
}

// ==============================
// GAD-7 scoring (frontend only)
// ==============================

function setupGad7() {
    const form = document.getElementById("gad7-form");
    const resultDiv = document.getElementById("gad7-result");

    if (!form || !resultDiv) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        let total = 0;
        let allAnswered = true;

        for (let i = 1; i <= 7; i++) {
            const name = `g${i}`;
            const selected = form.querySelector(`input[name="${name}"]:checked`);
            if (!selected) {
                allAnswered = false;
                continue;
            }
            total += parseInt(selected.value, 10);
        }

        if (!allAnswered) {
            alert('Please answer all questions to get your score.');
            return;
        }

        // Save to localStorage
        const gad7Data = JSON.parse(localStorage.getItem('gad7Data') || '[]');
        gad7Data.push({
            score: total,
            timestamp: new Date().toISOString(),
            level: getAnxietyLevel(total)
        });
        localStorage.setItem('gad7Data', JSON.stringify(gad7Data));

        // Show results
        const scoreDisplay = document.getElementById('score-display');
        const interpretationText = document.getElementById('interpretation-text');
        const recommendationText = document.getElementById('recommendation-text');
        
        if (scoreDisplay) scoreDisplay.textContent = total;
        
        let interpretation, recommendation;
        if (total <= 4) {
            interpretation = "Minimal anxiety";
            recommendation = "Your symptoms suggest minimal anxiety. Continue to monitor your mental health and practice stress management techniques like regular exercise, mindfulness, and adequate sleep.";
        } else if (total <= 9) {
            interpretation = "Mild anxiety";
            recommendation = "Your symptoms suggest mild anxiety. Consider practicing relaxation techniques, regular physical activity, and talking to someone you trust. If symptoms persist, consider professional help.";
        } else if (total <= 14) {
            interpretation = "Moderate anxiety";
            recommendation = "Your symptoms suggest moderate anxiety. It's recommended to speak with a healthcare professional about your symptoms. They can help develop coping strategies and determine if treatment is needed.";
        } else {
            interpretation = "Severe anxiety";
            recommendation = "Your symptoms suggest significant anxiety. It's important to seek professional help from a healthcare provider. They can provide appropriate treatment and support to help manage your anxiety.";
        }
        
        if (interpretationText) interpretationText.textContent = interpretation;
        if (recommendationText) recommendationText.textContent = recommendation;
        
        resultDiv.classList.remove('hidden');
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    });
}

function getAnxietyLevel(score) {
    if (score <= 4) return 'Minimal';
    if (score <= 9) return 'Mild';
    if (score <= 14) return 'Moderate';
    return 'Severe';
}

// ==============================
// Dashboard: read from localStorage
// ==============================

function setupDashboard() {
    const currentMoodValue = document.getElementById("current-mood-value");
    const currentMoodTime = document.getElementById("current-mood-time");
    const avgMoodValue = document.getElementById("avg-mood-value");
    const phq9ScoreValue = document.getElementById("phq9-score-value");
    const phq9LevelText = document.getElementById("phq9-level-text");
    const gad7ScoreValue = document.getElementById("gad7-score-value");
    const gad7LevelText = document.getElementById("gad7-level-text");
    const chartCanvas = document.getElementById("emotion-history-chart");

    const positiveCount = document.getElementById("positive-count");
    const neutralCount = document.getElementById("neutral-count");
    const negativeCount = document.getElementById("negative-count");
    const totalCount = document.getElementById("total-count");

    if (!currentMoodValue || !currentMoodTime || !avgMoodValue || !phq9ScoreValue || !phq9LevelText || !gad7ScoreValue || !gad7LevelText || !chartCanvas) {
        return;
    }

    // Current mood
    try {
        const rawCurrent = localStorage.getItem("current_mood");
        if (rawCurrent) {
            const cm = JSON.parse(rawCurrent);
            currentMoodValue.textContent = cm.emotion || "--";
            currentMoodTime.textContent = `Last checked at ${new Date(cm.time).toLocaleTimeString()}`;
        }
    } catch (e) {
        console.warn("Could not read current mood:", e);
    }

    // Emotion history for average mood and chart
    let history = [];
    try {
        const raw = localStorage.getItem("emotionData") || "[]";
        history = JSON.parse(raw);
    } catch (e) {
        console.warn("Could not read emotion history:", e);
    }

    const moodScoreMap = {
        Happy: 3,
        Surprise: 2,
        Neutral: 1,
        Fear: 0,
        Sad: -1,
        Angry: -2,
    };

    // Calculate average mood for today
    if (history.length > 0) {
        const today = new Date();
        const todayStart = new Date(
            today.getFullYear(),
            today.getMonth(),
            today.getDate()
        ).getTime();
        let sum = 0;
        let count = 0;

        history.forEach((h) => {
            if (h.time >= todayStart) {
                const s = moodScoreMap[h.emotion];
                if (typeof s === "number") {
                    sum += s;
                    count++;
                }
            }
        });

        if (count > 0) {
            const avg = sum / count;
            let label = "Balanced";
            if (avg >= 2) label = "Mostly Positive";
            else if (avg >= 0.5) label = "Gently Positive";
            else if (avg <= -1.5) label = "Mostly Low";
            else if (avg <= -0.5) label = "Gently Low";
            avgMoodValue.textContent = label;
        } else {
            avgMoodValue.textContent = "--";
        }
    }

    // Calculate emotion counts for summary cards
    let positiveCountNum = 0;
    let neutralCountNum = 0;
    let negativeCountNum = 0;

    history.forEach((h) => {
        const score = moodScoreMap[h.emotion];
        if (score >= 2) {
            positiveCountNum++;
        } else if (score <= -1) {
            negativeCountNum++;
        } else {
            neutralCountNum++;
        }
    });

    // Update summary cards
    if (positiveCount) positiveCount.textContent = positiveCountNum;
    if (neutralCount) neutralCount.textContent = neutralCountNum;
    if (negativeCount) negativeCount.textContent = negativeCountNum;
    if (totalCount) totalCount.textContent = history.length;

    // Build history chart (last 30 emotions)
    const emotionOrder = ["Angry", "Fear", "Happy", "Neutral", "Sad", "Surprise"];
    const labels = [];
    const dataPoints = [];

    // Get last 30 emotions (or all if less than 30)
    const recentHistory = history.slice(-30);
    
    recentHistory.forEach((h, index) => {
        labels.push(`#${index + 1}`);
        const emotionIndex = emotionOrder.indexOf(h.emotion);
        dataPoints.push(emotionIndex !== -1 ? emotionIndex : 3); // Default to Neutral if not found
    });

    // Create chart with better visualization
    new Chart(chartCanvas, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Recent Emotions",
                    data: dataPoints,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.1)",
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: "#3b82f6",
                    pointBorderColor: "#ffffff",
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    ticks: {
                        callback: (value) => emotionOrder[value] || "",
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    min: 0,
                    max: emotionOrder.length - 1,
                    grid: {
                        color: "rgba(0,0,0,0.05)"
                    }
                },
                x: {
                    grid: {
                        color: "rgba(0,0,0,0.05)"
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const emotionIndex = context.parsed.y;
                            const emotionName = emotionOrder[emotionIndex] || "Unknown";
                            return `Emotion: ${emotionName}`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        },
    });

    // PHQ-9 and GAD-7 summary
    try {
        const phq9Data = JSON.parse(localStorage.getItem('phq9Data') || '[]');
        if (phq9Data.length > 0) {
            const latestPhq9 = phq9Data[phq9Data.length - 1];
            phq9ScoreValue.textContent = latestPhq9.score;
            phq9LevelText.textContent = `${latestPhq9.level} (last at ${new Date(
                latestPhq9.timestamp
            ).toLocaleTimeString()})`;
        }
    } catch (e) {
        console.warn("Could not read PHQ-9 result:", e);
    }

    try {
        const gad7Data = JSON.parse(localStorage.getItem('gad7Data') || '[]');
        if (gad7Data.length > 0) {
            const latestGad7 = gad7Data[gad7Data.length - 1];
            gad7ScoreValue.textContent = latestGad7.score;
            gad7LevelText.textContent = `${latestGad7.level} (last at ${new Date(
                latestGad7.timestamp
            ).toLocaleTimeString()})`;
        }
    } catch (e) {
        console.warn("Could not read GAD-7 result:", e);
    }

    // Load Complete Analysis History
    loadCompleteAnalysisHistory();
}

// Load Complete Analysis History from backend
function loadCompleteAnalysisHistory() {
    const container = document.getElementById('analysis-history-container');
    if (!container) return;

    fetch('/api/complete-analysis-history')
        .then(response => response.json())
        .then(data => {
            if (!data.sessions || data.sessions.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-12">
                        <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="clipboard-x" class="w-8 h-8 text-purple-600"></i>
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">No Complete Analysis Yet</h3>
                        <p class="text-gray-600 mb-4">Start your first comprehensive assessment to track your mental health journey.</p>
                        <a href="/complete-analysis/start?new=true" class="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all">
                            <i data-lucide="plus" class="w-5 h-5"></i>
                            <span>Start Complete Analysis</span>
                        </a>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            // Build history cards
            const historyHTML = data.sessions.map(session => {
                const gad7Color = getSeverityColor(session.gad7.severity);
                const phq9Color = getSeverityColor(session.phq9.severity);
                const emotionEmoji = getEmotionEmoji(session.emotion);

                return `
                    <div class="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-purple-300 hover:shadow-lg transition-all">
                        <div class="flex items-start justify-between mb-4">
                            <div>
                                <div class="flex items-center space-x-2 mb-1">
                                    <i data-lucide="calendar" class="w-4 h-4 text-gray-500"></i>
                                    <span class="text-sm font-semibold text-gray-900">${session.date}</span>
                                </div>
                                ${session.time ? `<p class="text-xs text-gray-500 ml-6">${session.time}</p>` : ''}
                            </div>
                            <div class="flex space-x-2">
                                <a href="/complete-analysis/report?session_id=${session.session_id}" class="text-purple-600 hover:text-purple-700 p-2 hover:bg-purple-50 rounded-lg transition-colors" title="View Report">
                                    <i data-lucide="eye" class="w-5 h-5"></i>
                                </a>
                                <a href="/chatbot/with-context/${session.session_id}" class="text-blue-600 hover:text-blue-700 p-2 hover:bg-blue-50 rounded-lg transition-colors" title="Chat with Jaya">
                                    <i data-lucide="message-circle" class="w-5 h-5"></i>
                                </a>
                                <button onclick="deleteCompleteAnalysisSession('${session.session_id}')" class="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors cursor-pointer" title="Clear Analysis">
                                    <i data-lucide="trash-2" class="w-5 h-5"></i>
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div class="bg-gray-50 rounded-lg p-3">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs text-gray-600">Anxiety (GAD-7)</span>
                                    <i data-lucide="activity" class="w-4 h-4 text-gray-400"></i>
                                </div>
                                <div class="text-2xl font-bold text-gray-900 mb-1">${session.gad7.score}<span class="text-sm text-gray-500">/21</span></div>
                                <span class="inline-block px-2 py-1 rounded-full text-xs font-semibold ${gad7Color}">${session.gad7.severity.charAt(0).toUpperCase() + session.gad7.severity.slice(1)}</span>
                            </div>

                            <div class="bg-gray-50 rounded-lg p-3">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs text-gray-600">Depression (PHQ-9)</span>
                                    <i data-lucide="heart" class="w-4 h-4 text-gray-400"></i>
                                </div>
                                <div class="text-2xl font-bold text-gray-900 mb-1">${session.phq9.score}<span class="text-sm text-gray-500">/27</span></div>
                                <span class="inline-block px-2 py-1 rounded-full text-xs font-semibold ${phq9Color}">${session.phq9.severity.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                            </div>
                        </div>

                        ${session.emotion ? `
                            <div class="mt-4 flex items-center justify-center space-x-2 text-sm text-gray-600 bg-purple-50 rounded-lg py-2">
                                <span class="text-xl">${emotionEmoji}</span>
                                <span>Emotion: <span class="font-semibold text-gray-900">${session.emotion.charAt(0).toUpperCase() + session.emotion.slice(1)}</span></span>
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('');

            container.innerHTML = `
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${historyHTML}
                </div>
            `;

            lucide.createIcons();
        })
        .catch(err => {
            console.error('Error loading analysis history:', err);
            container.innerHTML = `
                <div class="text-center py-12">
                    <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i data-lucide="alert-circle" class="w-8 h-8 text-red-600"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Failed to Load History</h3>
                    <p class="text-gray-600">Could not load your analysis history. Please try refreshing the page.</p>
                </div>
            `;
            lucide.createIcons();
        });
}

async function deleteCompleteAnalysisSession(sessionId) {
    if (!confirm('Kya aap is complete analysis session ko delete karna chahte hain?')) {
        return;
    }
    try {
        const response = await fetch(`/complete-analysis/clear/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (data.success) {
            loadCompleteAnalysisHistory();
        } else {
            alert('Failed to delete analysis: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('Error deleting analysis session:', err);
        alert('Failed to delete analysis session');
    }
}
window.deleteCompleteAnalysisSession = deleteCompleteAnalysisSession;

function getSeverityColor(severity) {
    const colors = {
        'minimal': 'bg-green-100 text-green-700',
        'mild': 'bg-yellow-100 text-yellow-700',
        'moderate': 'bg-orange-100 text-orange-700',
        'moderately_severe': 'bg-red-100 text-red-700',
        'severe': 'bg-red-200 text-red-800'
    };
    return colors[severity] || 'bg-gray-100 text-gray-700';
}

function getEmotionEmoji(emotion) {
    if (!emotion) return '😐';
    const emojis = {
        'happy': '😊',
        'sad': '🙁',
        'angry': '😠',
        'fearful': '😨',
        'neutral': '😐',
        'surprised': '😮',
        'disgusted': '🤢'
    };
    return emojis[emotion.toLowerCase()] || '😐';
}

// ==============================
// Floating Support Chatbot
// ==============================

function setupChatbotWidget() {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const closeBtn = document.getElementById("chatbot-close");
    const windowEl = document.getElementById("chatbot-window");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");
    const typingEl = document.getElementById("chatbot-typing");

    // Require only the core chat elements so this works on both
    // the floating widget and the full-page chat UI.
    if (!form || !input || !messages) {
        return;
    }

    function openChat() {
        windowEl.classList.remove("hidden");
        input.focus();
    }

    function closeChat() {
        windowEl.classList.add("hidden");
    }

    function addMessage(sender, text, isUser) {
        const wrapper = document.createElement("div");
        wrapper.className = "flex w-full mb-4";
        wrapper.classList.add(isUser ? "justify-end" : "justify-start");

        const bubble = document.createElement("div");
        bubble.className = "max-w-[85%] px-4 py-3 rounded-2xl text-sm shadow-sm leading-relaxed";
        
        // Add classes individually to avoid space issues
        if (isUser) {
            bubble.classList.add("bg-blue-600", "text-white", "rounded-br-none");
        } else {
            bubble.classList.add("bg-white", "text-gray-800", "border", "border-gray-200", "rounded-bl-none");
        }

        const textEl = document.createElement("p");
        textEl.textContent = text;

        bubble.appendChild(textEl);
        wrapper.appendChild(bubble);
        messages.appendChild(wrapper);
        messages.scrollTop = messages.scrollHeight;
    }

    // Initial greeting
    if (!messages.dataset.initialized) {
        addMessage(
            "Bot",
            "Hi, I'm a gentle support bot. I can't give professional advice, but you can share how you're feeling and I'll respond with simple, supportive messages.",
            false
        );
        messages.dataset.initialized = "true";
    }

    // Floating widget controls (if present)
    if (toggleBtn && windowEl) {
        toggleBtn.addEventListener("click", () => {
            if (windowEl.classList.contains("hidden")) {
                openChat();
            } else {
                closeChat();
            }
        });
    }

    if (closeBtn && windowEl) {
        closeBtn.addEventListener("click", closeChat);
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = (input.value || "").trim();
        if (!text) return;

        addMessage("You", text, true);
        input.value = "";

        try {
            if (typingEl) {
                typingEl.classList.remove("hidden");
            }
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
            });

            if (!res.ok) {
                addMessage(
                    "Bot",
                    "I'm having trouble responding right now. Please try again in a moment.",
                    false
                );
                return;
            }

            const data = await res.json();
            const reply = data.reply ||
                "Thank you for sharing. Even small steps to care for yourself matter.";
            addMessage("Bot", reply, false);
        } catch (err) {
            console.error("Error calling /chat:", err);
            addMessage(
                "Bot",
                "Something went wrong while contacting the support bot.",
                false
            );
        }
        finally {
            if (typingEl) {
                typingEl.classList.add("hidden");
            }
        }
    });
}

function setupMoodChecker() {
    const emojiButtons = document.querySelectorAll(".emoji-btn");
    const moodMessage = document.getElementById("mood-message");

    if (!emojiButtons || !moodMessage) return;

    emojiButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const message = btn.getAttribute("data-message") || "You are important and your feelings matter.";
            moodMessage.textContent = message;

            // Simple fade effect by toggling a CSS class
            moodMessage.classList.remove("fade");
            // Force reflow to restart the animation
            void moodMessage.offsetWidth;
            moodMessage.classList.add("fade");
        });
    });
}

// Deprecated helper (kept for backward compatibility; no-op now)
function setupBreathingText() {
    // Breathing text is now controlled by setupBreathingExercise.
}

// ==============================
// Enhanced Breathing Exercise
// ==============================

function setupBreathingExercise() {
    const breatheCircle = document.getElementById('breathe-circle');
    const breatheText = document.getElementById('breathe-text');
    const breathCount = document.getElementById('breath-count');
    const startBtn = document.getElementById('start-breathing');
    const pauseBtn = document.getElementById('pause-breathing');
    const resetBtn = document.getElementById('reset-breathing');

    if (!breatheCircle || !breatheText || !startBtn || !pauseBtn || !resetBtn) return;

    let isBreathing = false;
    let breathCounter = 0;
    let animationStartTime = null;
    let textUpdateInterval = null;
    let pausedAt = 0; // Store elapsed time when paused
    let lastCycleCount = 0; // Track completed cycles

    // Initialize with paused state
    breatheCircle.classList.add('paused');
    breatheText.textContent = 'Ready to start';
    updateBreathCount();

    function updateBreathCount() {
        if (breathCount) {
            breathCount.textContent = `Breaths: ${breathCounter}`;
        }
    }

    function updateBreathingText() {
        if (!isBreathing || !animationStartTime) return;
        
        const elapsed = Date.now() - animationStartTime;
        const cycleLength = 16000; // 16-second cycle (Box Breathing: 4-4-4-4)
        const cycleProgress = (elapsed % cycleLength) / cycleLength;
        
        // Count breaths based on elapsed cycles
        const currentCycleCount = Math.floor(elapsed / cycleLength);
        if (currentCycleCount > lastCycleCount) {
            lastCycleCount = currentCycleCount;
            breathCounter++;
            updateBreathCount();
            
            if (breathCounter === 6) showEncouragement('Great job! 6 breaths completed!');
            else if (breathCounter === 12) showEncouragement('Excellent! Keep going!');
        }
        
        if (cycleProgress < 0.25) {
            breatheText.textContent = 'Inhale';
        } else if (cycleProgress < 0.5) {
            breatheText.textContent = 'Hold';
        } else if (cycleProgress < 0.75) {
            breatheText.textContent = 'Exhale';
        } else {
            breatheText.textContent = 'Hold';
        }
    }

    function showEncouragement(message) {
        if (breathCount) {
            const originalText = breathCount.textContent;
            breathCount.textContent = message;
            breathCount.style.color = '#10b981'; // Green color
            setTimeout(() => {
                breathCount.textContent = originalText;
                breathCount.style.color = '';
            }, 2000);
        }
    }

    function startBreathing() {
        if (isBreathing) return;
        
        isBreathing = true;
        // Resume from where we left off (pausedAt is 0 initially or elapsed time if paused)
        animationStartTime = Date.now() - pausedAt;
        breatheCircle.classList.remove('paused');
        breatheText.textContent = 'Inhale';
        
        // Start text updates
        textUpdateInterval = setInterval(updateBreathingText, 100);
        
        // Visual feedback
        startBtn.classList.add('opacity-50');
        pauseBtn.classList.remove('opacity-50');
    }

    function pauseBreathing() {
        if (!isBreathing) return;
        
        isBreathing = false;
        pausedAt = Date.now() - animationStartTime; // Store progress
        breatheCircle.classList.add('paused');
        breatheText.textContent = 'Paused';
        
        // Stop text updates
        if (textUpdateInterval) {
            clearInterval(textUpdateInterval);
            textUpdateInterval = null;
        }
        
        // Visual feedback
        startBtn.classList.remove('opacity-50');
        pauseBtn.classList.add('opacity-50');
    }

    function resetBreathing() {
        pauseBreathing();
        breathCounter = 0;
        lastCycleCount = 0;
        pausedAt = 0;
        animationStartTime = null;
        updateBreathCount();
        breatheText.textContent = 'Ready to start';
        
        // Reset animation
        breatheCircle.style.animation = 'none';
        breatheCircle.offsetHeight; // Trigger reflow
        breatheCircle.style.animation = '';
        breatheCircle.classList.add('paused');
        
        // Visual feedback
        startBtn.classList.remove('opacity-50');
        pauseBtn.classList.remove('opacity-50');
    }

    // Event listeners
    startBtn.addEventListener('click', startBreathing);
    pauseBtn.addEventListener('click', pauseBreathing);
    resetBtn.addEventListener('click', resetBreathing);

    // Initialize button states
    pauseBtn.classList.add('opacity-50');
}

// Old camera brightness demo removed – not needed in streamlined version
