// ============================================================
// tasks_graph.js — Interactive Graph Editor for Fakarni
// Features: drag-to-connect, edge-click-to-delete, mark done,
//           dark/light mode, Arabic/English support
// ============================================================

// ── الثيمات (تعمل مع dark-mode و light-mode) ────────────────
function getGraphTheme() {
    const isLight = document.documentElement.classList.contains('light-mode') ||
                    document.body.classList.contains('light-mode');
    return {
        nodePlanned:    { background: isLight ? '#f1f5f9' : '#1e293b', border: isLight ? '#94a3b8' : '#475569', font: isLight ? '#1e293b' : '#e2e8f0' },
        nodeProgress:   { background: isLight ? '#fef3c7' : '#78350f', border: isLight ? '#f59e0b' : '#d97706', font: isLight ? '#92400e' : '#fde68a' },
        nodeDone:       { background: isLight ? '#dcfce7' : '#14532d', border: isLight ? '#10b981' : '#16a34a', font: isLight ? '#065f46' : '#86efac' },
        edgeNormal:     { color: isLight ? '#94a3b8' : '#475569', highlight: '#6366f1' },
        edgeManip:      '#6366f1',
        background:     isLight ? '#ffffff' : '#0f172a',
    };
}

// ── دالة إنشاء لون النود حسب الحالة ───────────────────────
function nodeColor(status, theme) {
    if (status === 'completed' || status === 'done') return theme.nodeDone;
    if (status === 'in_progress')                   return theme.nodeProgress;
    return theme.nodePlanned;
}

// ── خيارات الجراف الاحترافية ─────────────────────────────
function buildGraphOptions(theme) {
    return {
        nodes: {
            shape: 'box',
            margin: { top: 10, right: 14, bottom: 10, left: 14 },
            font: { size: 14, face: 'Cairo, Poppins, sans-serif', bold: true, multi: true },
            widthConstraint: { minimum: 120, maximum: 240 },
            borderWidth: 2,
            borderWidthSelected: 3,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.12)', size: 8 }
        },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 1.1 } },
            smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 },
            color: theme.edgeNormal,
            width: 2,
            selectionWidth: 3,
            hoverWidth: 3
        },
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'UD',
                sortMethod: 'directed',
                nodeSpacing: 200,
                levelSeparation: 150,
                shakeTowards: 'roots'
            }
        },
        interaction: {
            dragNodes: true,
            dragView: true,
            multiselect: true,
            hover: true,
            selectConnectedEdges: true,
            tooltipDelay: 200
        },
        physics: { enabled: false },
        manipulation: {
            enabled: false,  // نفتحه يدوياً من زرار "وضع التوصيل"
            initiallyActive: false,
            addEdge: function(edgeData, callback) {
                // منع ربط نود بنفسها
                if (edgeData.from === edgeData.to) {
                    callback(null);
                    return;
                }
                handleEdgeAdd(edgeData.from, edgeData.to, callback);
            },
            deleteEdge: false,  // بنتعامل مع الحذف يدوياً
            editEdge: false,
            addNode: false
        }
    };
}

// ── إدارة الـ network كـ global ──────────────────────────
let graphNetwork = null;
let graphNodes = null;
let graphEdges = null;
let connectModeActive = false;

// ── وضع التوصيل (Connect Mode) ─────────────────────────
function toggleConnectMode() {
    connectModeActive = !connectModeActive;
    if (!graphNetwork) return;

    if (connectModeActive) {
        graphNetwork.setOptions({ manipulation: { enabled: true } });
        graphNetwork.addEdgeMode();
        showGraphToast(window._i18n?.connect_mode_on || 'وضع التوصيل: اسحب من نود لأخرى');
    } else {
        graphNetwork.setOptions({ manipulation: { enabled: false } });
        graphNetwork.disableEditMode();
        showGraphToast(window._i18n?.connect_mode_off || 'خرجت من وضع التوصيل');
    }
    closeGraphMenu();
}

// ── ربط edge جديدة (drag-to-connect) ──────────────────
async function handleEdgeAdd(fromId, toId, callback) {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

    try {
        // toId يصبح ابن (child) لـ fromId
        const res = await fetch(`/api/tasks/${toId}/reparent`, {
            method: 'PATCH', headers,
            body: JSON.stringify({ new_parent_id: fromId })
        });
        if (res.ok) {
            const theme = getGraphTheme();
            const toTask = graphNodes.get(toId);
            callback({
                from: fromId, to: toId,
                arrows: 'to',
                color: theme.edgeNormal,
                dashes: false,
                id: `e_${fromId}_${toId}`
            });
            showGraphToast(window._i18n?.edge_added || 'تم الربط بنجاح');
        } else {
            callback(null);
            showGraphToast(window._i18n?.edge_error || 'فشل الربط', true);
        }
    } catch (e) {
        callback(null);
        console.error('[Graph] Edge add failed:', e);
    }

    // الخروج من وضع التوصيل بعد the add
    if (connectModeActive) {
        connectModeActive = false;
        if (graphNetwork) {
            graphNetwork.setOptions({ manipulation: { enabled: false } });
            graphNetwork.disableEditMode();
        }
    }
}

// ── حذف edge (فصل) برسالة تأكيد ──────────────────────
async function handleEdgeDelete(edgeId) {
    if (!graphEdges) return;
    const edge = graphEdges.get(edgeId);
    if (!edge) return;

    const childId = edge.to;
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

    const result = await Swal.fire({
        title: window._i18n?.detach_title || 'فصل المهمة؟',
        text: window._i18n?.detach_msg || 'ستصبح مهمة مستقلة',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: window._i18n?.yes_detach || 'فصل',
        cancelButtonText: window._i18n?.cancel || 'إلغاء',
        confirmButtonColor: '#f59e0b'
    });
    if (!result.isConfirmed) return;

    try {
        const res = await fetch(`/api/tasks/${childId}/reparent`, {
            method: 'PATCH', headers,
            body: JSON.stringify({ new_parent_id: null })
        });
        if (res.ok) {
            graphEdges.remove(edgeId);
            showGraphToast(window._i18n?.detach_ok || 'تم الفصل');
        }
    } catch (e) {
        console.error('[Graph] Edge delete failed:', e);
    }
}

// ── إدارة القائمة السياقية ───────────────────────────
let currentContextMenuNodes = [];
let currentContextMenuEdge  = null;

function closeGraphMenu() {
    const menu = document.getElementById('graphContextMenu');
    const edgeMenu = document.getElementById('graphEdgeMenu');
    if (menu) menu.style.display = 'none';
    if (edgeMenu) edgeMenu.style.display = 'none';
}
window.addEventListener('click', (e) => {
    const nm  = document.getElementById('graphContextMenu');
    const em  = document.getElementById('graphEdgeMenu');
    if (!nm?.contains(e.target) && !em?.contains(e.target)) closeGraphMenu();
});

// ── تهيئة أحداث الجراف ──────────────────────────────
function initContextMenuEvents(networkInstance) {
    if (!networkInstance) return;

    // منع قائمة المتصفح الافتراضية
    const canvas = networkInstance.canvas.frame.canvas;
    canvas.addEventListener('contextmenu', e => e.preventDefault());

    // ── كليك يمين على نود → قائمة Node ──
    networkInstance.on('oncontext', function(params) {
        params.event.preventDefault();
        closeGraphMenu();

        const nodeId = this.getNodeAt(params.pointer.DOM);
        const edgeId = this.getEdgeAt(params.pointer.DOM);

        if (nodeId !== undefined) {
            let sel = this.getSelectedNodes();
            if (!sel.includes(nodeId)) { this.selectNodes([nodeId]); sel = [nodeId]; }
            currentContextMenuNodes = sel;
            currentContextMenuEdge  = null;

            const menu = document.getElementById('graphContextMenu');
            if (menu) {
                menu.style.display = 'block';
                menu.style.left = params.event.pageX + 'px';
                menu.style.top  = params.event.pageY + 'px';
            }
        } else if (edgeId !== undefined) {
            // ── كليك يمين على edge → قائمة Edge ──
            currentContextMenuEdge  = edgeId;
            currentContextMenuNodes = [];
            const em = document.getElementById('graphEdgeMenu');
            if (em) {
                em.style.display = 'block';
                em.style.left = params.event.pageX + 'px';
                em.style.top  = params.event.pageY + 'px';
            }
        }
    });

    networkInstance.on('click',     closeGraphMenu);
    networkInstance.on('dragStart', closeGraphMenu);
    networkInstance.on('zoom',      closeGraphMenu);
}

// ── تحديث الـ UI بعد أي عملية ───────────────────────
function syncAllTasksUI() {
    if (typeof drawGoalsGraph    === 'function') drawGoalsGraph();
    if (typeof fetchAndRenderTasks === 'function') fetchAndRenderTasks();
}

// ── Toast خفيف ──────────────────────────────────────
function showGraphToast(msg, isError = false) {
    const existing = document.getElementById('graphToast');
    if (existing) existing.remove();
    const t = document.createElement('div');
    t.id = 'graphToast';
    t.style.cssText = `
        position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
        background:${isError ? '#ef4444' : '#10b981'}; color:#fff;
        padding:10px 22px; border-radius:24px; font-family:Cairo,sans-serif;
        font-size:14px; z-index:9999; box-shadow:0 4px 16px rgba(0,0,0,0.2);
        animation: slideUp 0.3s ease;
    `;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
}

// ── موزع الأوامر الرئيسي للقائمة السياقية ──────────
async function handleMenuAction(action) {
    closeGraphMenu();
    if (action === 'edge_delete') {
        if (currentContextMenuEdge) await handleEdgeDelete(currentContextMenuEdge);
        return;
    }
    if (currentContextMenuNodes.length === 0) return;

    const token   = localStorage.getItem('access_token') || localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

    try {
        // ── حذف ──
        if (action === 'delete') {
            const r = await Swal.fire({
                title: window._i18n?.del_title || 'تأكيد الحذف',
                text: `${window._i18n?.del_msg || 'سيتم حذف'} ${currentContextMenuNodes.length} ${window._i18n?.tasks_word || 'مهمة'}`,
                icon: 'warning', showCancelButton: true,
                confirmButtonColor: '#ef4444',
                confirmButtonText: window._i18n?.delete_btn || 'احذف',
                cancelButtonText:  window._i18n?.cancel     || 'إلغاء'
            });
            if (r.isConfirmed) {
                for (const id of currentContextMenuNodes)
                    await fetch(`/api/tasks/${id}`, { method: 'DELETE', headers });
                syncAllTasksUI();
                showGraphToast(window._i18n?.deleted_ok || 'تم الحذف');
            }
        }
        // ── فصل ──
        else if (action === 'cut') {
            for (const id of currentContextMenuNodes)
                await fetch(`/api/tasks/${id}/reparent`, {
                    method: 'PATCH', headers,
                    body: JSON.stringify({ new_parent_id: null })
                });
            syncAllTasksUI();
            showGraphToast(window._i18n?.detach_ok || 'تم الفصل');
        }
        // ── تعديل اسم ──
        else if (action === 'rename') {
            const { value: newTitle } = await Swal.fire({
                title: window._i18n?.rename_title || 'تعديل اسم المهمة',
                input: 'text', inputPlaceholder: window._i18n?.rename_ph || 'الاسم الجديد...',
                showCancelButton: true,
                confirmButtonText: window._i18n?.save || 'حفظ',
                cancelButtonText:  window._i18n?.cancel || 'إلغاء'
            });
            if (newTitle?.trim()) {
                for (const id of currentContextMenuNodes)
                    await fetch(`/api/tasks/${id}`, {
                        method: 'PATCH', headers,
                        body: JSON.stringify({ title: newTitle.trim() })
                    });
                syncAllTasksUI();
            }
        }
        // ── إضافة ابن ──
        else if (action === 'child') {
            const { value: childTitle } = await Swal.fire({
                title: window._i18n?.add_child || 'إضافة مهمة فرعية',
                input: 'text', inputPlaceholder: window._i18n?.child_ph || 'اسم المهمة الفرعية...',
                showCancelButton: true,
                confirmButtonText: window._i18n?.add || 'إضافة',
                cancelButtonText:  window._i18n?.cancel || 'إلغاء'
            });
            if (childTitle?.trim()) {
                for (const id of currentContextMenuNodes)
                    await fetch(`/api/tasks/`, {
                        method: 'POST', headers,
                        body: JSON.stringify({ title: childTitle.trim(), parent_id: id })
                    });
                syncAllTasksUI();
                showGraphToast(window._i18n?.child_added || 'تمت الإضافة');
            }
        }
        // ── تعليم "تمت" ──
        else if (action === 'done') {
            for (const id of currentContextMenuNodes)
                await fetch(`/api/tasks/${id}`, {
                    method: 'PATCH', headers,
                    body: JSON.stringify({ status: 'completed' })
                });
            syncAllTasksUI();
            showGraphToast(window._i18n?.marked_done || 'تم! أحسنت');
        }
        // ── إلغاء "تمت" ──
        else if (action === 'undone') {
            for (const id of currentContextMenuNodes)
                await fetch(`/api/tasks/${id}`, {
                    method: 'PATCH', headers,
                    body: JSON.stringify({ status: 'pending' })
                });
            syncAllTasksUI();
            showGraphToast(window._i18n?.marked_pending || 'عادت للحالة المعلقة');
        }
        // ── دمج ──
        else if (action === 'merge') {
            if (currentContextMenuNodes.length < 2) {
                Swal.fire(window._i18n?.warning || 'تنبيه', window._i18n?.merge_min || 'يجب تحديد مهمتين على الأقل', 'warning');
                return;
            }
            const { value: mergeTitle } = await Swal.fire({
                title: window._i18n?.merge_title || 'دمج المهام',
                input: 'text', inputPlaceholder: window._i18n?.merge_ph || 'اسم المهمة المدمجة...',
                showCancelButton: true,
                confirmButtonText: window._i18n?.merge_btn || 'دمج',
                cancelButtonText:  window._i18n?.cancel || 'إلغاء'
            });
            if (mergeTitle?.trim()) {
                await fetch(`/api/tasks/merge`, {
                    method: 'POST', headers,
                    body: JSON.stringify({ task_ids: currentContextMenuNodes, new_title: mergeTitle.trim() })
                });
                syncAllTasksUI();
                showGraphToast(window._i18n?.merged_ok || 'تم الدمج');
            }
        }
        // ── فورك ──
        else if (action === 'fork') {
            for (const id of currentContextMenuNodes)
                await fetch(`/api/tasks/${id}/fork`, { method: 'POST', headers });
            syncAllTasksUI();
            showGraphToast(`${window._i18n?.forked_ok || 'تم التشعب'} (${currentContextMenuNodes.length})`);
        }
        // ── وضع التوصيل ──
        else if (action === 'connect_mode') {
            toggleConnectMode();
        }

    } catch (err) {
        Swal.fire(window._i18n?.error || 'خطأ', window._i18n?.db_error || 'فشل الاتصال بقاعدة البيانات', 'error');
        console.error('[Graph Action Error]', action, err);
    }
}

// ── إعادة الترتيب ────────────────────────────────────
function reorganizeGraph() {
    if (!graphNetwork) return;
    graphNetwork.setOptions({ layout: { hierarchical: { enabled: true, direction: 'UD' } } });
    showGraphToast(window._i18n?.reorganized || 'تم إعادة الترتيب');
    closeGraphMenu();
}

// ── تفعيل/إيقاف التحريك الحر ───────────────────────
let isMovementEnabled = false;
function toggleMovement() {
    isMovementEnabled = !isMovementEnabled;
    if (graphNetwork) {
        graphNetwork.setOptions({ interaction: { dragNodes: isMovementEnabled } });
        showGraphToast(isMovementEnabled
            ? (window._i18n?.drag_on  || 'التحريك الحر مفعل')
            : (window._i18n?.drag_off || 'التحريك مغلق'));
    }
    closeGraphMenu();
}
