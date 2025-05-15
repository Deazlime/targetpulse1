document.addEventListener('DOMContentLoaded', function() {
    const notifBlock = document.getElementById('notification-block');
    if (!notifBlock) return;
    const userId = notifBlock.dataset.userId;
    const notifList = document.getElementById('notification-list');
    const notifIcon = document.getElementById('notification-icon');
    let notifCount = 0;

    // Открытие/закрытие списка уведомлений
    notifIcon.onclick = function() {
        notifList.style.display = notifList.style.display === 'none' ? 'block' : 'none';
    };

    // WebSocket
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsPath = `${wsScheme}://${window.location.host}/ws/notifications/${userId}/`;
    const socket = new WebSocket(wsPath);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        notifCount++;
        notifIcon.textContent = `🔔 (${notifCount})`;
        const item = document.createElement('div');
        item.className = 'notification-item';
        item.innerHTML = `<b>${data.message}</b><br><span style='font-size:0.85em;color:#888;'>${data.created_at}</span>`;
        notifList.prepend(item);
    };

    socket.onclose = function() {
        console.warn('WebSocket закрыт');
    };
}); 