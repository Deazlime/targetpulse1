document.addEventListener('DOMContentLoaded', () => {
    const timers = {};

    document.querySelectorAll('.timer-btn').forEach(button => {
        button.addEventListener('click', () => {
            const taskId = button.getAttribute('data-task-id');
            toggleTimer(taskId, button);
        });
    });

    async function toggleTimer(taskId, button) {
        if (button.textContent === 'Запустить таймер') {
            button.textContent = 'Остановить таймер';
            timers[taskId] = setInterval(() => {
                const timeSpan = document.getElementById(`time-${taskId}`);
                let time = parseFloat(timeSpan.textContent) || 0;
                time += 1/3600; // Увеличиваем на 1 секунду в часах
                timeSpan.textContent = time.toFixed(2);
                fetch(`/task/${taskId}/update_time/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                    },
                    body: JSON.stringify({ time_spent: time })
                });
            }, 1000);
        } else {
            button.textContent = 'Запустить таймер';
            clearInterval(timers[taskId]);
        }
    }
});