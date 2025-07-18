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
    // Bind click event to delete buttons
    document.querySelectorAll('.delete-file').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var fileId = this.getAttribute('data-file-id');
            deleteFile(fileId);
        });
    });
});

// Function to get the value of a cookie by name
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

// Function to delete a file by its ID
function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        fetch(`/xel/admin/delete/${fileId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
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