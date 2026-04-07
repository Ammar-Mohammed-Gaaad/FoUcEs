// focus.js - Handles the Pomodoro Timer functionality with modern UI updates

const FocusTimer = {
    timer: null,
    timeLeft: 25 * 60,
    isRunning: false,
    currentMode: 'pomodoro', // 'pomodoro', 'shortBreak', 'longBreak'
    modes: {
        pomodoro: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    },

    elements: {
        display: document.getElementById('timerDisplay'),
        btnStartPause: document.getElementById('btnStartPause'),
        startText: document.getElementById('startText'),
        btnReset: document.getElementById('btnReset'),
        modePomodoro: document.getElementById('modePomodoro'),
        modeShortBreak: document.getElementById('modeShortBreak'),
        modeLongBreak: document.getElementById('modeLongBreak'),
        taskSelect: document.getElementById('focusTaskSelect'),
        statusMessage: document.getElementById('statusMessage'),
        // Settings Modal
        settingsModal: document.getElementById('settingsModal'),
        openSettingsBtn: document.getElementById('openSettingsBtn'),
        closeSettingsBtn: document.getElementById('closeSettingsBtn'),
        saveSettingsBtn: document.getElementById('saveSettingsBtn'),
        pomodoroTimeInput: document.getElementById('pomodoroTime'),
        shortBreakTimeInput: document.getElementById('shortBreakTime'),
        longBreakTimeInput: document.getElementById('longBreakTime')
    },

    init() {
        this.loadSettings();
        this.updateDisplay();
        this.bindEvents();
        this.loadTasks();
    },

    loadSettings() {
        const savedSettings = localStorage.getItem('focusTimerSettings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                if (settings.pomodoro) this.modes.pomodoro = settings.pomodoro * 60;
                if (settings.shortBreak) this.modes.shortBreak = settings.shortBreak * 60;
                if (settings.longBreak) this.modes.longBreak = settings.longBreak * 60;
            } catch(e) {
                console.error('Error loading settings', e);
            }
        }
        // Initialize timeLeft based on current mode
        this.timeLeft = this.modes[this.currentMode];
    },

    openSettings() {
        this.elements.pomodoroTimeInput.value = Math.floor(this.modes.pomodoro / 60);
        this.elements.shortBreakTimeInput.value = Math.floor(this.modes.shortBreak / 60);
        this.elements.longBreakTimeInput.value = Math.floor(this.modes.longBreak / 60);
        this.elements.settingsModal.classList.add('active');
    },

    closeSettings() {
        this.elements.settingsModal.classList.remove('active');
    },

    saveSettings() {
        const pMode = parseInt(this.elements.pomodoroTimeInput.value);
        const sMode = parseInt(this.elements.shortBreakTimeInput.value);
        const lMode = parseInt(this.elements.longBreakTimeInput.value);

        if (pMode > 0 && sMode > 0 && lMode > 0) {
            this.modes.pomodoro = pMode * 60;
            this.modes.shortBreak = sMode * 60;
            this.modes.longBreak = lMode * 60;

            localStorage.setItem('focusTimerSettings', JSON.stringify({
                pomodoro: pMode,
                shortBreak: sMode,
                longBreak: lMode
            }));
            
            // Only update current time if it's NOT running
            if (!this.isRunning) {
                this.timeLeft = this.modes[this.currentMode];
                this.updateDisplay();
            }
            
            this.closeSettings();
        } else {
            alert('يرجى إدخال قيم صحيحة للمؤقت.');
        }
    },

    async loadTasks() {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) return;

        try {
            const res = await fetch('/api/tasks/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const tasks = await res.json();
                this.populateTaskDropdown(tasks);
            }
        } catch (error) {
            console.error('[Focus] Error loading tasks:', error);
        }
    },

    populateTaskDropdown(tasks) {
        const pendingTasks = tasks.filter(t => t.status !== 'completed'); // Fixed missing status field match!
        const savedTask = localStorage.getItem('focus_selected_task');
        
        this.elements.taskSelect.innerHTML = '<option value="">-- اضغط لاختيار مهمة للتركيز عليها --</option>';
        this.elements.taskSelect.innerHTML += '<option value="CREATE_NEW">➕ + إضافة مهمة جديدة للتركيز عليها</option>';
        pendingTasks.forEach(task => {
            const opt = document.createElement('option');
            opt.value = task.id;
            opt.textContent = task.title;
            // Restore previously selected task if valid
            if (savedTask && savedTask == task.id) {
                opt.selected = true;
            }
            this.elements.taskSelect.appendChild(opt);
        });
    },

    bindEvents() {
        this.elements.btnStartPause.addEventListener('click', () => this.toggleTimer());
        this.elements.btnReset.addEventListener('click', () => this.resetTimer());

        this.elements.modePomodoro.addEventListener('click', () => this.setMode('pomodoro'));
        this.elements.modeShortBreak.addEventListener('click', () => this.setMode('shortBreak'));
        this.elements.modeLongBreak.addEventListener('click', () => this.setMode('longBreak'));

        // Settings Modal events
        if (this.elements.openSettingsBtn) {
            this.elements.openSettingsBtn.addEventListener('click', () => this.openSettings());
            this.elements.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
            this.elements.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
            
            // Allow clicking outside the modal content to close it
            this.elements.settingsModal.addEventListener('click', (e) => {
                if (e.target === this.elements.settingsModal) {
                    this.closeSettings();
                }
            });
        }

        // Task selection saves to localStorage OR triggers creation
        this.elements.taskSelect.addEventListener('change', async (e) => {
            if (e.target.value === 'CREATE_NEW') {
                const taskTitle = prompt('📝 أدخل اسم المهمة الجديدة التي تريد التركيز عليها الآن:');
                if (taskTitle && taskTitle.trim() !== '') {
                    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
                    try {
                        const res = await fetch('/api/tasks/', {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title: taskTitle.trim(), priority: 3 })
                        });
                        if (res.ok) {
                            const newTask = await res.json();
                            // Refresh tasks background cache or manually push to dropdown
                            const opt = document.createElement('option');
                            opt.value = newTask.id;
                            opt.textContent = newTask.title;
                            opt.selected = true;
                            this.elements.taskSelect.appendChild(opt);
                            localStorage.setItem('focus_selected_task', newTask.id);
                            alert('✅ تم إضافة المهمة للوحة التحكم ومزامنتها بنجاح!');
                        } else {
                            alert('❌ فشل إضافة المهمة! الرجاء المحاولة مرة أخرى.');
                            this.elements.taskSelect.selectedIndex = 0;
                        }
                    } catch(err) {
                        alert('❌ حدث خطأ في الاتصال بالخادم أثناء إضافة المهمة.');
                        this.elements.taskSelect.selectedIndex = 0;
                    }
                } else {
                    // Canceled prompt or empty input
                    this.elements.taskSelect.selectedIndex = 0;
                }
            } else {
                localStorage.setItem('focus_selected_task', e.target.value);
            }
        });
    },

    setMode(mode) {
        if (this.isRunning) {
            if (!confirm('المؤقت يعمل حالياً. هل أنت متأكد من تغيير وضع التركيز؟')) {
                return;
            }
            this.pauseTimer();
        }

        this.currentMode = mode;
        this.timeLeft = this.modes[mode];
        
        // Update UI
        this.elements.modePomodoro.classList.remove('active');
        this.elements.modeShortBreak.classList.remove('active');
        this.elements.modeLongBreak.classList.remove('active');

        if (mode === 'pomodoro') {
            this.elements.modePomodoro.classList.add('active');
        } else if (mode === 'shortBreak') {
            this.elements.modeShortBreak.classList.add('active');
        } else if (mode === 'longBreak') {
            this.elements.modeLongBreak.classList.add('active');
        }

        this.updateDisplay();
        this.elements.statusMessage.innerText = '';
    },

    toggleTimer() {
        if (this.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    },

    startTimer() {
        if (this.timeLeft <= 0) return;
        this.isRunning = true;
        this.elements.btnStartPause.innerHTML = '<i class="fas fa-pause"></i> <span id="startText">إيقاف</span>';
        
        // Add heartbeat animation
        document.body.classList.add('timer-running');

        this.timer = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
                this.updateDisplay();
            } else {
                this.completeTimer();
            }
        }, 1000);
    },

    pauseTimer() {
        this.isRunning = false;
        clearInterval(this.timer);
        this.elements.btnStartPause.innerHTML = '<i class="fas fa-play"></i> <span id="startText">استئناف</span>';
        document.body.classList.remove('timer-running');
    },

    resetTimer() {
        this.pauseTimer();
        this.timeLeft = this.modes[this.currentMode];
        this.updateDisplay();
        this.elements.btnStartPause.innerHTML = '<i class="fas fa-play"></i> <span id="startText">ابدأ</span>';
        this.elements.statusMessage.innerHTML = '';
    },

    completeTimer() {
        this.pauseTimer();
        this.elements.btnStartPause.innerHTML = '<i class="fas fa-play"></i> <span id="startText">ابدأ</span>';
        this.playAlarmSound();

        const taskName = this.elements.taskSelect.selectedIndex > 0 ? this.elements.taskSelect.options[this.elements.taskSelect.selectedIndex].text : '';
        
        if (this.currentMode === 'pomodoro') {
            const extraText = taskName ? `على المهمة: ${taskName}` : '';
            this.elements.statusMessage.innerText = `🎉 أحسنت! نجحت في إكمال جلسة تركيز ${extraText}. حان وقت الاستراحة.`;
            this.showNotification('🎉 انتهت جلسة التركيز', 'حان وقت الاستراحة القصيرة!');
            this.setMode('shortBreak');
        } else {
            this.elements.statusMessage.innerText = 'انتهت الاستراحة! حان وقت التركيز من جديد.';
            this.showNotification('⏰ انتهت الاستراحة', 'جاهز لجلسة تركيز جديدة؟');
            this.setMode('pomodoro');
        }
    },

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const displayString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        this.elements.display.innerText = displayString;
        document.title = `${displayString} - وضع التركيز`;
    },

    playAlarmSound() {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();

            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
            oscillator.frequency.setValueAtTime(1046.50, audioCtx.currentTime + 0.3); // C6
            
            gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
            gainNode.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 0.1);
            gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.8);

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            oscillator.start(audioCtx.currentTime);
            oscillator.stop(audioCtx.currentTime + 0.8);
        } catch(e) {
            console.warn('Audio play failed', e);
        }
    },

    showNotification(title, body) {
        if (!('Notification' in window)) return;
        
        if (Notification.permission === 'granted') {
            new Notification(title, { body, icon: '/img/favicon.png' });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(title, { body, icon: '/img/favicon.png' });
                }
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    FocusTimer.init();
});
