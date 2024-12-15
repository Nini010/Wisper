document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file');
    const previewImage = document.getElementById('preview');
    const messageDiv = document.getElementById('message');

    // Display the image preview and upload it immediately when a file is selected
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            // Show image preview
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            };
            reader.readAsDataURL(file);

            // Prepare to upload the image
            const formData = new FormData();
            formData.append('file', file);
            formData.append('currentPage', window.location.pathname);

            // Upload the file via AJAX
            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    // Clear the message div after successful upload
                    if (data.success) {
                        messageDiv.innerHTML = '';  // Remove any message
                    } else {
                        messageDiv.innerHTML = `<p style="color: red;">${data.message}</p>`;
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    messageDiv.innerHTML = '<p style="color: red;">An error occurred while uploading.</p>';
                });
        }
    });
});
