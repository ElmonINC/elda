document.addEventListener('DOMContentLoaded', function() {
    var Btn = document.getElementById('hide_upload');
    var form = document.getElementById('upload_form');
    if (Btn && form) {
        Btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (form.style.display === 'none' || formD.style.display === '') {
                form.style.display = 'block';
            } else {
                form.style.display = 'none';
            }
        });
    }
});