document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-timer-btn');
    const stopBtn = document.getElementById('stop-timer-btn');
    let timerInterval;
    if (startBtn && stopBtn) {
        startBtn.onclick = function() {
            fetch(`/tasks/${startBtn.dataset.taskId}/start_timer/`, {
                method: 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value}
            })
            .then(() => {
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
                timerInterval = setInterval(() => {
                    let el = document.getElementById('time-' + startBtn.dataset.taskId);
                    el.textContent = (parseFloat(el.textContent.replace(',', '.')) + 0.01).toFixed(2).replace('.', ',');
                }, 36000); // +0.01 ч = 36 сек
            });
        };
        stopBtn.onclick = function() {
            fetch(`/tasks/${stopBtn.dataset.taskId}/stop_timer/`, {
                method: 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value}
            })
            .then(() => {
                stopBtn.style.display = 'none';
                startBtn.style.display = 'inline-block';
                clearInterval(timerInterval);
                location.reload();
            });
        };
    }
}); 