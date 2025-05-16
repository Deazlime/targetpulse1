document.addEventListener('DOMContentLoaded', function() {
    const notifBlock = document.getElementById('notification-block');
    if (!notifBlock) return;
    
    const userId = notifBlock.dataset.userId;
    const notifList = document.getElementById('notification-list');
    const notifIcon = document.getElementById('notification-icon');
    let notifCount = 0;
    let lastCheckTime = new Date().toISOString();

    function updateNotificationCount(count) {
        notifCount = count;
        notifIcon.textContent = `🔔 (${notifCount})`;
    }

    function addNotification(notification) {
        const item = document.createElement('div');
        item.className = 'notification-item';
        item.dataset.notifId = notification.id;
        item.innerHTML = `<a href="${notification.url}" style="text-decoration:none;color:inherit;display:block;">
            <b>${notification.message}</b><br><span style='font-size:0.85em;color:#888;'>${notification.created_at}</span>
        </a>`;
        item.addEventListener('click', function(e) {
            e.preventDefault();
            // Сохраняем id уведомления в localStorage
            localStorage.setItem('read_notification_id', notification.id);
            window.location.href = notification.url;
        });
        notifList.prepend(item);
    }

    async function checkNewNotifications() {
        try {
            const response = await fetch(`/api/notifications/check/?since=${lastCheckTime}`);
            const data = await response.json();
            
            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(notification => {
                    addNotification(notification);
                });
                updateNotificationCount(data.total_count);
                lastCheckTime = new Date().toISOString();
            }
        } catch (error) {
            console.error('Ошибка проверки уведомлений:', error);
        }
    }

    async function loadInitialNotifications() {
        try {
            const response = await fetch('/api/notifications/');
            const data = await response.json();
            
            if (data.notifications) {
                data.notifications.forEach(notification => {
                    addNotification(notification);
                });
                updateNotificationCount(data.total_count);
            }
        } catch (error) {
            console.error('Ошибка загрузки уведомлений:', error);
        }
    }

    notifIcon.onclick = function() {
        notifList.style.display = notifList.style.display === 'none' ? 'block' : 'none';
    };

    // Загружаем начальные уведомления
    loadInitialNotifications();

    // Проверяем новые уведомления каждые 30 секунд
    setInterval(checkNewNotifications, 30000);

    // После загрузки страницы проверяем localStorage
    const notifId = localStorage.getItem('read_notification_id');
    if (notifId) {
        fetch(`/api/notifications/read/${notifId}/`, {
            method: 'POST',
            headers: {'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]')||{}).value}
        }).finally(() => {
            localStorage.removeItem('read_notification_id');
        });
    }
}); 