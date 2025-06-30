document.addEventListener('DOMContentLoaded', function() {
    var showBtn = document.getElementById('show-upload-form');
    var formDiv = document.getElementById('upload-form-container');
    if (showBtn && formDiv) {
        showBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (formDiv.style.display === 'none' || formDiv.style.display === '') {
                formDiv.style.display = 'block';
            } else {
                formDiv.style.display = 'none';
            }
        });
    }
});