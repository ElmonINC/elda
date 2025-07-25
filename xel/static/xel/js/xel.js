document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('hide_upload');
    var form = document.getElementById('upload_form');
    if (btn && form) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            form.style.display = form.style.display === 'none' || form.style.display === '' ? 'block' : 'none';
        });
    }

    document.querySelectorAll('.delete-file').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var fileId = this.getAttribute('data-file-id');
            deleteFile(fileId);
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        fetch(`/xel/admin/delete/${fileId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`file-row-${fileId}`).remove();
                alert('File deleted successfully.');
            } else {
                alert('Error deleting file: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting file: ' + error.message);
        });
    }
}