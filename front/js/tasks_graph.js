// Path: front/js/tasks_graph.js

// 1. خيارات الجراف الاحترافية مع تفعيل التحديد المتعدد
const graphOptions = {
    nodes: {
        shape: 'box',
        margin: 12,
        font: { size: 18, face: 'Cairo', multi: true },
        widthConstraint: { minimum: 140, maximum: 250 },
        borderWidth: 2,
        shadow: true
    },
    edges: {
        arrows: { to: { enabled: true, scaleFactor: 1.2 } },
        smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.5 },
        color: { color: '#cbd5e1', highlight: '#2563eb' }
    },
    layout: {
        hierarchical: {
            enabled: true,
            direction: 'UD',
            sortMethod: 'directed',
            nodeSpacing: 200,
            levelSeparation: 150
        }
    },
    interaction: {
        dragNodes: false,
        dragView: true,
        multiselect: true, // تفعيل التحديد المتعدد
        hover: true
    },
    physics: { enabled: false }
};

// 2. دالة إعادة الترتيب
function reorganizeGraph() {
    if (typeof network !== 'undefined') {
        network.setOptions({ layout: { hierarchical: { enabled: true } } });
        setTimeout(() => {
            network.setOptions({ layout: { hierarchical: false } });
            Swal.fire('تم الترتيب', 'رجعت الشجرة لأصلها المنظم', 'success');
        }, 1000);
    }
    closeGraphMenu();
}

// 3. التحكم في الحركة
let isMovementEnabled = false;
function toggleMovement() {
    isMovementEnabled = !isMovementEnabled;
    if (typeof network !== 'undefined') {
        network.setOptions({ interaction: { dragNodes: isMovementEnabled } });
        const msg = isMovementEnabled ? 'التحريك الحر مفعل' : 'التحريك مغلق (ثبات رأسي)';
        Swal.fire('وضع الحركة', msg, 'info');
    }
    closeGraphMenu();
}

// 4. إدارة القائمة السياقية
const graphContextMenu = document.getElementById('graphContextMenu');
let currentContextMenuNodes = [];

function closeGraphMenu() {
    if (graphContextMenu) graphContextMenu.style.display = 'none';
}
window.addEventListener('click', (e) => {
    if (!graphContextMenu?.contains(e.target)) closeGraphMenu();
});

// يُستدعى بعد إنشاء network مباشرة
function initContextMenuEvents(networkInstance) {
    if (!networkInstance) return;

    // 1. قفل قائمة المتصفح الافتراضية (Save image as...) على الـ Canvas نفسه
    const canvasElement = networkInstance.canvas.frame.canvas;
    canvasElement.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });

    // 2. تفعيل قائمة فكرني المخصصة
    networkInstance.on("oncontext", function (params) {
        params.event.preventDefault();

        const nodeId = this.getNodeAt(params.pointer.DOM);
        let selectedNodes = this.getSelectedNodes();

        // لو Right Click على نود مش متحددة → نحددها هي بس
        if (nodeId && !selectedNodes.includes(nodeId)) {
            this.selectNodes([nodeId]);
            selectedNodes = [nodeId];
        }

        currentContextMenuNodes = selectedNodes;

        const menu = document.getElementById('graphContextMenu');
        if (menu && selectedNodes.length > 0) {
            menu.style.display = 'block';
            // pageX/pageY لضمان ظهور القائمة تحت الماوس بالضبط
            menu.style.left = params.event.pageX + 'px';
            menu.style.top  = params.event.pageY + 'px';
        } else {
            closeGraphMenu();
        }
    });

    // 3. إخفاء القائمة عند أي حركة أخرى في الجراف
    networkInstance.on("click",      closeGraphMenu);
    networkInstance.on("dragStart",  closeGraphMenu);
    networkInstance.on("zoom",       closeGraphMenu);
}

// 5. تحديث الواجهة بعد أي عملية
function syncAllTasksUI() {
    if (typeof drawGoalsGraph === 'function') drawGoalsGraph();
    if (typeof fetchAndRenderTasks === 'function') fetchAndRenderTasks();
    else if (typeof loadTasks === 'function') loadTasks();
    else if (typeof fetchTasks === 'function') fetchTasks();
}

// 6. موزع الأوامر مع Loop على المحددين
async function handleMenuAction(action) {
    closeGraphMenu();
    if (currentContextMenuNodes.length === 0) return;

    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    try {
        if (action === 'delete') {
            const result = await Swal.fire({
                title: 'تأكيد الحذف',
                text: `سيتم حذف ${currentContextMenuNodes.length} مهمة/مهام نهائياً!`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                confirmButtonText: 'احذف',
                cancelButtonText: 'إلغاء'
            });
            if (result.isConfirmed) {
                for (const nodeId of currentContextMenuNodes) {
                    await fetch(`/api/tasks/${nodeId}`, { method: 'DELETE', headers });
                }
                syncAllTasksUI();
                Swal.fire('تم الحذف', '', 'success');
            }
        }
        else if (action === 'cut') {
            for (const nodeId of currentContextMenuNodes) {
                await fetch(`/api/tasks/${nodeId}`, {
                    method: 'PATCH',
                    headers,
                    body: JSON.stringify({ parent_id: null })
                });
            }
            syncAllTasksUI();
            Swal.fire('تم الفصل', 'تم فصل المهام عن أبائها', 'success');
        }
        else if (action === 'rename') {
            const { value: newTitle } = await Swal.fire({
                title: 'تعديل اسم المهمة',
                input: 'text',
                inputPlaceholder: 'الاسم الجديد...',
                showCancelButton: true,
                confirmButtonText: 'حفظ',
                cancelButtonText: 'إلغاء'
            });
            if (newTitle?.trim()) {
                for (const nodeId of currentContextMenuNodes) {
                    await fetch(`/api/tasks/${nodeId}`, {
                        method: 'PATCH',
                        headers,
                        body: JSON.stringify({ title: newTitle.trim() })
                    });
                }
                syncAllTasksUI();
            }
        }
        else if (action === 'child') {
            const { value: childTitle } = await Swal.fire({
                title: 'إضافة مهمة فرعية',
                input: 'text',
                inputPlaceholder: 'اسم المهمة الفرعية...',
                showCancelButton: true,
                confirmButtonText: 'إضافة',
                cancelButtonText: 'إلغاء'
            });
            if (childTitle?.trim()) {
                for (const nodeId of currentContextMenuNodes) {
                    await fetch(`/api/tasks/`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ title: childTitle.trim(), parent_id: nodeId })
                    });
                }
                syncAllTasksUI();
            }
        }
        else if (action === 'merge') {
            if (currentContextMenuNodes.length < 2) {
                Swal.fire('تنبيه', 'يجب تحديد مهمتين على الأقل لدمجهما!', 'warning');
                return;
            }
            const { value: mergeTitle } = await Swal.fire({
                title: 'دمج المهام',
                input: 'text',
                inputPlaceholder: 'اسم المهمة المدمجة...',
                showCancelButton: true,
                confirmButtonText: 'دمج',
                cancelButtonText: 'إلغاء'
            });
            if (mergeTitle?.trim()) {
                await fetch(`/api/tasks/merge`, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({ task_ids: currentContextMenuNodes, new_title: mergeTitle.trim() })
                });
                syncAllTasksUI();
                Swal.fire('تم الدمج', '', 'success');
            }
        }
        else if (action === 'fork') {
            for (const nodeId of currentContextMenuNodes) {
                await fetch(`/api/tasks/${nodeId}/fork`, { method: 'POST', headers });
            }
            syncAllTasksUI();
            Swal.fire('تم التشعب', `تم عمل ${currentContextMenuNodes.length} نسخة`, 'success');
        }
    } catch (error) {
        Swal.fire('خطأ', 'فشل الاتصال بقاعدة البيانات', 'error');
        console.error('[Graph Action Error]', error);
    }
}
