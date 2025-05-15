class TaskTimer {
    constructor(taskId, userId) {
        this.taskId = taskId;
        this.userId = userId;
        this.socket = null;
        this.isRunning = false;
        this.connect();
    }

    connect() {
        this.socket = new WebSocket(
            `ws://${window.location.host}/ws/task/${this.taskId}/timer/`
        );

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'time_update') {
                this.updateDisplay(data.duration);
            }
        };
    }

    startTimer() {
        if (!this.isRunning) {
            this.socket.send(JSON.stringify({
                action: 'start_timer',
                user_id: this.userId
            }));
            this.isRunning = true;
        }
    }

    stopTimer() {
        if (this.isRunning) {
            this.socket.send(JSON.stringify({
                action: 'stop_timer',
                user_id: this.userId
            }));
            this.isRunning = false;
        }
    }

    updateDisplay(duration) {
        const timerElement = document.querySelector(`#timer-${this.taskId}`);
        if (timerElement) {
            timerElement.textContent = duration;
        }
    }
} 