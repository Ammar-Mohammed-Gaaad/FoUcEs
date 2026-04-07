// reminders.js - Handles polling for due reminders and firing notifications

const ReminderPoller = {
    pollInterval: null,
    swRegistration: null,

    async init() {
        console.log('[Reminders] Initializing...');
        
        // Check for Service Worker & Notification Support
        if (!('serviceWorker' in navigator) || !('Notification' in window)) {
            console.log('[Reminders] Browser does not support push notifications.');
            return;
        }

        try {
            // Register SW root relative to domain
            this.swRegistration = await navigator.serviceWorker.register('/sw.js');
            console.log('[Reminders] Service Worker registered:', this.swRegistration);
            
            // Ask permission immediately if default
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    console.log('[Reminders] Notification permission denied.');
                    return;
                }
            }

            if (Notification.permission === 'granted') {
                // Listen to SW messages (Snooze/Dismiss)
                navigator.serviceWorker.addEventListener('message', this.handleSWMessage.bind(this));
                
                // Start tracking / polling
                this.startPolling();
                console.log('[Reminders] Polling started.');
            }
        } catch (error) {
            console.error('[Reminders] Setup failed:', error);
        }
    },

    startPolling() {
        if (this.pollInterval) clearInterval(this.pollInterval);
        
        // Poll every 30 seconds
        this.pollInterval = setInterval(() => this.checkDueReminders(), 30000);
        
        // Also check immediately
        this.checkDueReminders();
    },

    async checkDueReminders() {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) return; // not logged in

        try {
            const res = await fetch('/api/reminders/due', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const dueReminders = await res.json();
                dueReminders.forEach(reminder => {
                    this.fireNotification(reminder);
                });
            }
        } catch (error) {
            console.error('[Reminders] Error checking due reminders:', error);
        }
    },

    playWakeupSound() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.type = 'triangle';
        oscillator.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.2); // E5
        
        gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
        gainNode.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 0.05);
        gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.start(audioCtx.currentTime);
        oscillator.stop(audioCtx.currentTime + 0.5);
    },

    async fireNotification(reminder) {
        // Prevent double firing if local storage flag is set recently
        const lockKey = `rem_fired_${reminder.id}`;
        const lastFired = localStorage.getItem(lockKey);
        if (lastFired && (Date.now() - parseInt(lastFired)) < 60000) {
            return; // fired < 1 minute ago
        }
        localStorage.setItem(lockKey, Date.now());

        // Play Sound
        this.playWakeupSound();

        // Show Notification via SW
        if (this.swRegistration) {
            this.swRegistration.showNotification('تذكير فكرني ⏰', {
                body: reminder.title,
                icon: '/img/favicon.png', // Fallback gracefully if not exists
                vibrate: [200, 100, 200, 100, 200, 100, 200],
                requireInteraction: true,
                data: { id: reminder.id },
                actions: [
                    { action: 'snooze', title: '💤 غفوة 10 دقائق ' },
                    { action: 'dismiss', title: '❌ تم' }
                ]
            });
        }
    },

    async handleSWMessage(event) {
        const data = event.data;
        if (!data || !data.id) return;

        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) return;

        if (data.type === 'SNOOZE_REMINDER') {
            const snoozeTo = new Date(Date.now() + 10 * 60000).toISOString();
            await fetch(`/api/reminders/${data.id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ snoozed_until: snoozeTo })
            });
            console.log(`[Reminders] Reminder ${data.id} snoozed.`);
        } 
        else if (data.type === 'DISMISS_REMINDER') {
            await fetch(`/api/reminders/${data.id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                // Turn off if not repeating, otherwise just clear snooze so it waits for next repeat
                body: JSON.stringify({ is_active: false }) 
            });
            console.log(`[Reminders] Reminder ${data.id} dismissed.`);
        }
    }
};

// Auto-start on load
document.addEventListener('DOMContentLoaded', () => {
    ReminderPoller.init();
});
