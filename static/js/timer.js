document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[id^="timer-"]').forEach(timerElement => {
        const taskId = timerElement.id.split('-')[1];
        const btn = document.getElementById(`timer-btn-${taskId}`);
        const display = document.getElementById(`timer-display-${taskId}`);
        let timerInterval = null;
        let startTime = null;
        let running = false;
        let timerEntryId = null;

        if (!btn) {
            console.log('Таймер: кнопка не найдена для задачи', taskId);
            return;
        }
        console.log('Таймер: инициализация для задачи', taskId);

        async function checkStatus() {
            try {
                const response = await fetch(`/api/timer/status/${taskId}/`);
                const data = await response.json();
                if (data.status === 'running') {
                    running = true;
                    timerEntryId = data.timer_id;
                    startTime = new Date(data.start_time);
                    btn.textContent = 'Остановить таймер';
                    startDisplay();
                } else {
                    running = false;
                    btn.textContent = 'Запустить таймер';
                    stopDisplay();
                    display.textContent = '00:00:00';
                }
            } catch (e) {
                btn.textContent = 'Запустить таймер';
                stopDisplay();
                display.textContent = '00:00:00';
            }
        }

        async function startTimer() {
            console.log('Таймер: старт для задачи', taskId);
            try {
                const response = await fetch(`/api/timer/start/${taskId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    }
                });
                const data = await response.json();
                if (data.status === 'success') {
                    running = true;
                    timerEntryId = data.timer_id;
                    startTime = new Date(data.start_time);
                    btn.textContent = 'Остановить таймер';
                    startDisplay();
                } else {
                    console.log('Ошибка запуска таймера:', data);
                }
            } catch (e) { console.log('Ошибка AJAX старта таймера', e); }
        }

        async function stopTimer() {
            console.log('Таймер: стоп для задачи', taskId);
            try {
                const response = await fetch(`/api/timer/stop/${timerEntryId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    }
                });
                const data = await response.json();
                if (data.status === 'success') {
                    running = false;
                    btn.textContent = 'Запустить таймер';
                    stopDisplay();
                    display.textContent = data.duration || '00:00:00';
                    fetch(`/api/task/${taskId}/set_status/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: 'status=Завершено'
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    console.log('Ошибка остановки таймера:', data);
                }
            } catch (e) { console.log('Ошибка AJAX стопа таймера', e); }
        }

        function startDisplay() {
            stopDisplay();
            timerInterval = setInterval(() => {
                const now = new Date();
                const diff = now - startTime;
                display.textContent = formatDuration(diff);
            }, 1000);
        }
        function stopDisplay() {
            if (timerInterval) clearInterval(timerInterval);
        }
        function formatDuration(ms) {
            const hours = Math.floor(ms / 3600000);
            const minutes = Math.floor((ms % 3600000) / 60000);
            const seconds = Math.floor((ms % 60000) / 1000);
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        btn.addEventListener('click', () => {
            console.log('Таймер: клик по кнопке для задачи', taskId, 'running:', running);
            if (!running) {
                startTimer();
            } else {
                stopTimer();
            }
        });

        checkStatus();
    });
});