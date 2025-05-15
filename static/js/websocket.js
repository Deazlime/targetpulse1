document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket('ws://' + window.location.host + '/ws/boards/');
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'task_update') {
            location.reload(); // Простое обновление; в продакшене обновлять DOM
        }
    };
});