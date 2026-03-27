/*
  Modular Button + Task manager - production-ready architecture
  - TaskService: state + persistence
  - TaskUI: rendering and animations
  - ButtonManager: event delegation + action registry
*/

class TaskService {
    constructor(storageKey = 'fakarni_tasks') {
        this.storageKey = storageKey;
        this.tasks = this._load() || [];
    }

    _load() {
        try {
            const item = localStorage.getItem(this.storageKey);
            return item ? JSON.parse(item) : [];
        } catch (err) {
            console.error('[TaskService] load failed', err);
            return [];
        }
    }

    _save() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.tasks));
        } catch (err) {
            console.error('[TaskService] save failed', err);
        }
    }

    getAll() {
        return [...this.tasks];
    }

    create(text) {
        const value = (text || '').trim();
        if (!value) throw new Error('Task text cannot be empty');

        const task = { id: Date.now().toString(), text: value, completed: false };
        this.tasks.push(task);
        this._save();
        return task;
    }

    remove(id) {
        this.tasks = this.tasks.filter((t) => t.id !== id);
        this._save();
    }

    toggleComplete(id) {
        this.tasks = this.tasks.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t));
        this._save();
    }
}

class TaskUI {
    constructor(taskService, containerSelector = '#tasksList') {
        this.taskService = taskService;
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            console.warn('[TaskUI] container missing', containerSelector);
        }
    }

    _createTaskCard(task) {
        const wrapper = document.createElement('div');
        wrapper.className = 'task-card';
        wrapper.dataset.taskId = task.id;
        wrapper.dataset.completed = String(task.completed);

        wrapper.innerHTML = `
            <div class="task-info">
                <div class="task-title">${task.text}</div>
            </div>
            <div class="task-actions">
                <button class="task-btn complete-btn" data-action="toggleTaskComplete" type="button">${task.completed ? '✅ تمت' : '✓ مكتملة'}</button>
                <button class="task-btn delete-btn" data-action="deleteTask" type="button">✕ حذف</button>
            </div>
        `;

        if (task.completed) {
            wrapper.classList.add('task-done');
        }

        wrapper.style.opacity = 0;
        requestAnimationFrame(() => {
            wrapper.style.transition = 'opacity 240ms ease, transform 240ms ease';
            wrapper.style.opacity = 1;
            wrapper.style.transform = 'translateY(0)';
        });

        return wrapper;
    }

    addTask(task) {
        if (!this.container) return;
        const card = this._createTaskCard(task);
        this.container.appendChild(card);
    }

    removeTask(id) {
        if (!this.container) return;
        const node = this.container.querySelector(`[data-task-id="${id}"]`);
        if (!node) return;

        node.style.transition = 'opacity 220ms ease, transform 220ms ease';
        node.style.opacity = 0;
        node.style.transform = 'translateY(-8px)';
        setTimeout(() => node.remove(), 230);
    }

    toggleTaskCompletion(id) {
        if (!this.container) return;
        const node = this.container.querySelector(`[data-task-id="${id}"]`);
        if (!node) return;

        const completed = node.dataset.completed === 'true';
        node.dataset.completed = String(!completed);

        const completeBtn = node.querySelector('[data-action="toggleTaskComplete"]');
        if (completeBtn) {
            completeBtn.textContent = completed ? '✓ مكتملة' : '✅ تمت';
        }

        node.classList.toggle('task-done', !completed);
    }

    renderAll() {
        if (!this.container) return;
        this.container.innerHTML = '';
        const tasks = this.taskService.getAll();
        tasks.forEach((task) => this.addTask(task));
    }
}

class ButtonManager {
    constructor(actionRegistry) {
        this.actionRegistry = actionRegistry;
        this.doubleClickTimeout = 600;
        this.debouncedElements = new WeakMap();
        this._bindGlobalClick();
        this._bindKeyboardAction();
    }

    _getActionTarget(target) {
        return target.closest('button, [data-action], a.nav-item, .task-btn, .filter-btn, .primary-action-btn, .icon-btn');
    }

    _executeAction(target, event) {
        const action = target.dataset.action;
        if (!action) return false;

        const handler = this.actionRegistry[action];
        if (typeof handler !== 'function') {
            console.warn('[ButtonManager] action not found', action);
            return false;
        }

        if (this.debouncedElements.has(target)) {
            return true;
        }

        this.debouncedElements.set(target, true);
        setTimeout(() => this.debouncedElements.delete(target), this.doubleClickTimeout);

        target.classList.add('active');
        setTimeout(() => target.classList.remove('active'), 120);

        try {
            handler(event, target);
        } catch (err) {
            console.error('[ButtonManager] action thrown', action, err);
            if (typeof window.showPopup === 'function') {
                window.showPopup('خطأ', 'حدث خطأ أثناء تنفيذ الإجراء');
            }
        }

        return true;
    }

    _bindGlobalClick() {
        document.body.addEventListener('click', (event) => {
            const target = this._getActionTarget(event.target);
            if (!target || target.disabled || target.getAttribute('aria-disabled') === 'true') return;

            const style = window.getComputedStyle(target);
            if (style.pointerEvents === 'none') return;

            if (this._executeAction(target, event)) {
                event.preventDefault();
                event.stopPropagation();
            }
        }, true);
    }

    _bindKeyboardAction() {
        document.body.addEventListener('keydown', (event) => {
            if (!['Enter', ' '].includes(event.key)) return;
            const target = this._getActionTarget(event.target);
            if (!target || target.disabled || target.getAttribute('aria-disabled') === 'true') return;

            event.preventDefault();
            target.click();
        }, true);
    }
}

(function () {
    const taskService = new TaskService();
    const taskUI = new TaskUI(taskService);

    const actions = {
        openTaskModal: () => document.getElementById('taskModal')?.classList.add('active'),
        closeTaskModal: () => document.getElementById('taskModal')?.classList.remove('active'),
        saveTask: () => {
            const input = document.querySelector('#newTaskInput');
            if (!input) {
                if (typeof window.showPopup === 'function') window.showPopup('خطأ', 'حقل المهمة غير موجود');
                return;
            }
            const value = input.value.trim();
            if (!value) {
                if (typeof window.showPopup === 'function') window.showPopup('تنبيه', 'أدخل نص المهمة');
                return;
            }

            try {
                const task = taskService.create(value);
                taskUI.addTask(task);
                input.value = '';
                input.focus();

                if (typeof window.showPopup === 'function') window.showPopup('نجاح', 'تم حفظ المهمة');
            } catch (err) {
                console.error(err);
                if (typeof window.showPopup === 'function') window.showPopup('خطأ', err.message);
            }
        },
        deleteTask: (event, target) => {
            const card = target.closest('.task-card');
            if (!card) return;
            const id = card.dataset.taskId;
            taskService.remove(id);
            taskUI.removeTask(id);
        },
        toggleTaskComplete: (event, target) => {
            const card = target.closest('.task-card');
            if (!card) return;
            const id = card.dataset.taskId;
            taskService.toggleComplete(id);
            taskUI.toggleTaskCompletion(id);
        },
        filterTasks: (event, target) => {
            const filter = target.dataset.filter || 'all';
            document.querySelectorAll('.filter-btn').forEach((btn) => btn.classList.remove('active'));
            target.classList.add('active');
            const tasks = taskService.getAll();
            const container = document.querySelector('#tasksList');
            if (!container) return;
            container.innerHTML = '';
            taskUI.container = container;
            taskUI.taskService = taskService;

            const filtered = filter === 'all' ? tasks : tasks.filter((t) => (filter === 'completed' ? t.completed : !t.completed));
            filtered.forEach((task) => taskUI.addTask(task));
        },
        switchTab: (event, target) => {
            const sectionName = target.dataset.section;
            if (!sectionName) return;
            document.querySelectorAll('.section-view').forEach((el) => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach((el) => el.classList.remove('active'));
            document.getElementById(sectionName)?.classList.add('active');
            target.classList.add('active');
        },
        closePopup: () => document.getElementById('customPopup')?.classList.remove('active'),
        toggleSignup: (event, target) => {
            const id = target.dataset.target;
            document.getElementById(id)?.dispatchEvent(new Event('change'));
        },
        goBack: () => window.history.back(),
        redirectHome: () => window.location.href = '/home',
        logout: () => {
            localStorage.clear();
            window.location.href = '/';
        }
    };

    const buttonManager = new ButtonManager(actions);
    taskUI.renderAll();
})();