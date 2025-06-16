document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });

        const data = await response.json();
        if (data.status === 'success') {
            alert('File uploaded successfully!');
            // Clear the form
            fileInput.value = '';
            document.getElementById('preview-container').style.display = 'none';
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        alert('Upload failed: ' + error.message);
    }
});

document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const filenameDisplay = document.getElementById('filename-display');

    if (file) {
        filenameDisplay.textContent = file.name;
        previewContainer.style.display = 'block';
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            previewImage.style.display = 'none';
        }
    } else {
        previewContainer.style.display = 'none';
    }
});