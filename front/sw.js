self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : { title: 'مهمة جديدة', body: 'تذكير للعمل على مهامك' };

    const options = {
        body: data.body,
        icon: '/img/favicon.png', // Assuming there's a favicon, otherwise will fall back gracefully
        badge: '/img/badge.png',
        vibrate: [200, 100, 200, 100, 200, 100, 200],
        data: data.data || {},
        actions: [
            {
                action: 'snooze',
                title: '💤 غفوة (10 دقائق)',
            },
            {
                action: 'dismiss',
                title: '❌ إغلاق',
            }
        ],
        requireInteraction: true // keeps the notification open until user clicks it
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'snooze') {
        console.log('[ServiceWorker] Snooze clicked for reminder ID:', event.notification.data.id);
        // We defer real snooze to the main thread via message, 
        // to use existing tokens & fetch securely.
        event.waitUntil(
            self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
                if(clientList.length > 0) {
                    clientList[0].postMessage({
                        type: 'SNOOZE_REMINDER',
                        id: event.notification.data.id
                    });
                }
            })
        );
    } else if (event.action === 'dismiss') {
        console.log('[ServiceWorker] Dismiss clicked for reminder ID:', event.notification.data.id);
        event.waitUntil(
            self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
                if(clientList.length > 0) {
                    clientList[0].postMessage({
                        type: 'DISMISS_REMINDER',
                        id: event.notification.data.id
                    });
                }
            })
        );
    } else {
        // Just opened it normally
        event.waitUntil(
            self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
                for (var i = 0; i < clientList.length; i++) {
                    var client = clientList[i];
                    if (client.url == '/' && 'focus' in client)
                        return client.focus();
                }
                if (self.clients.openWindow)
                    return self.clients.openWindow('/html/tasks.html');
            })
        );
    }
});
