// Fallback face-api.js loader
// This is a placeholder - in a real scenario, you would host the face-api.js library locally

console.log('Loading face-api.js fallback...');

// For now, let's try to load from a reliable CDN
(function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js';
    script.crossOrigin = 'anonymous';
    script.onerror = function() {
        console.error('Failed to load face-api.js from fallback CDN');
    };
    script.onload = function() {
        console.log('face-api.js loaded from fallback CDN');
    };
    document.head.appendChild(script);
})();
