// Modal open/close + status auto-submit
document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-open-modal]');
    if (opener) {
        e.preventDefault();
        const id = opener.getAttribute('data-open-modal');
        const modal = document.getElementById(id);
        if (modal) {
            modal.hidden = false;
        } else if (id === 'new-task') {
            window.location.href = '/';
        }
        return;
    }

    if (e.target.closest('[data-close-modal]')) {
        const modal = e.target.closest('.modal');
        if (modal) modal.hidden = true;
        return;
    }

    if (e.target.classList && e.target.classList.contains('modal')) {
        e.target.hidden = true;
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal:not([hidden])').forEach((m) => { m.hidden = true; });
    }
});

document.addEventListener('change', (e) => {
    const sel = e.target.closest('[data-auto-submit]');
    if (sel) {
        const form = sel.closest('form');
        if (form) form.submit();
    }
});
