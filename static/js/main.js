// it asks for confirmation before submitting any form marked with data-confirm
document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
        if (!confirm(form.dataset.confirm)) {
            e.preventDefault();
        }
    });
});

// it is for so that user can dismiss the flash message
document.querySelectorAll('.flash-close').forEach(function (closeBtn) {
    closeBtn.addEventListener('click', function () {
        var flash = closeBtn.closest('.flash');
        var stack = flash.closest('.flash-stack');
        flash.remove();
        if (stack && stack.querySelectorAll('.flash').length === 0) {
            stack.remove();
        }
    });
});
