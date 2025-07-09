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

function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        fetch(`/xel/delete_file/${fileId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: fileId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`file-row-${fileId}`).remove();
                alert('File deleted successfully.');
            } else {
                alert('Error deleting file: ' + data.error);
            }
        });
    }
}