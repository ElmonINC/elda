function previewFile() {
    const preview = document.getElementById('preview-image');
    const fileInput = document.getElementById('fileInput');
    const previewArea = document.getElementById('preview-area');
    const filenameDisplay = document.getElementById('filename-display');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onloadend = function() {
            preview.src = reader.result;
            filenameDisplay.textContent = "File name: " + file.name;
            previewArea.style.display = 'block';
        }

        if (file.type.startsWith('image/')) {
            reader.readAsDataURL(file);
        } else {
            preview.src = 'path/to/default-file-icon.png'; // Add a default file icon for non-image files
            filenameDisplay.textContent = "File name: " + file.name;
            previewArea.style.display = 'block';
        }
    }
}