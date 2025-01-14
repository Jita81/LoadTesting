// Queue for batching clicks
let clickQueue = [];
const BATCH_SIZE = 100;
const BATCH_INTERVAL = 100; // ms
const BASE_URL = 'https://faithful-cat-production.up.railway.app';

// Statistics elements
const totalClicksElement = document.getElementById('totalClicks');
const clicksPerSecondElement = document.getElementById('clicksPerSecond');

// Function to send batched clicks to the server
async function sendBatchedClicks() {
    if (clickQueue.length === 0) return;
    
    try {
        const response = await fetch(`${BASE_URL}/api/log-click`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            console.error('Failed to log click');
        }
    } catch (error) {
        console.error('Error logging click:', error);
    }
}

// Function to update statistics
async function updateStats() {
    try {
        const response = await fetch(`${BASE_URL}/api/stats`);
        const data = await response.json();
        
        totalClicksElement.textContent = data.total_clicks;
        clicksPerSecondElement.textContent = data.clicks_per_second;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Set up click handler
document.getElementById('helloButton').addEventListener('click', function() {
    clickQueue.push(Date.now());
    
    if (clickQueue.length >= BATCH_SIZE) {
        sendBatchedClicks();
        clickQueue = [];
    }
});

// Set up periodic batch sending
setInterval(() => {
    if (clickQueue.length > 0) {
        sendBatchedClicks();
        clickQueue = [];
    }
}, BATCH_INTERVAL);

// Update statistics periodically
setInterval(updateStats, 1000); 