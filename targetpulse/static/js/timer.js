class TaskTimer {
    constructor(taskId) {
        this.taskId = taskId;
        this.timerId = null;
        this.startTime = null;
        this.timerElement = document.querySelector(`#timer-${taskId}`);
        this.startButton = document.querySelector(`#start-timer-${taskId}`);
        this.stopButton = document.querySelector(`#stop-timer-${taskId}`);
        this.displayElement = document.querySelector(`#timer-display-${taskId}`);
        
        this.init();
    }

    init() {
        this.startButton.addEventListener('click', () => this.startTimer());
        this.stopButton.addEventListener('click', () => this.stopTimer());
        this.checkStatus();
    }

    async checkStatus() {
        try {
            const response = await fetch(`/api/timer/status/${this.taskId}/`);
            const data = await response.json();
            
            if (data.status === 'running') {
                this.timerId = data.timer_id;
                this.startTime = new Date(data.start_time);
                this.startButton.style.display = 'none';
                this.stopButton.style.display = 'block';
                this.startDisplay();
            } else {
                this.startButton.style.display = 'block';
                this.stopButton.style.display = 'none';
            }
        } catch (error) {
            console.error('Error checking timer status:', error);
        }
    }

    async startTimer() {
        try {
            const response = await fetch(`/api/timer/start/${this.taskId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.timerId = data.timer_id;
                this.startTime = new Date(data.start_time);
                this.startButton.style.display = 'none';
                this.stopButton.style.display = 'block';
                this.startDisplay();
            }
        } catch (error) {
            console.error('Error starting timer:', error);
        }
    }

    async stopTimer() {
        try {
            const response = await fetch(`/api/timer/stop/${this.timerId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.startButton.style.display = 'block';
                this.stopButton.style.display = 'none';
                this.stopDisplay();
                this.displayElement.textContent = data.duration;
            }
        } catch (error) {
            console.error('Error stopping timer:', error);
        }
    }

    startDisplay() {
        this.displayInterval = setInterval(() => {
            const now = new Date();
            const diff = now - this.startTime;
            const hours = Math.floor(diff / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            this.displayElement.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopDisplay() {
        if (this.displayInterval) {
            clearInterval(this.displayInterval);
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Инициализация таймеров для всех задач на странице
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[id^="timer-"]').forEach(timerElement => {
        const taskId = timerElement.id.split('-')[1];
        new TaskTimer(taskId);
    });
}); 