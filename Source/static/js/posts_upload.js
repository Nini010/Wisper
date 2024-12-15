document.addEventListener('DOMContentLoaded', () => {
    const addPostBtn = document.getElementById('addPostBtn');
    const fileInput = document.getElementById('file');
    const previewImage = document.getElementById('preview');
    const messageDiv = document.getElementById('message');

    // Trigger file input click when the Add Post button is clicked
    addPostBtn.addEventListener('click', () => {
        fileInput.click();  // Triggers the file input selection
    });

    // Display the image preview and upload it immediately when a file is selected
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            reader.readAsDataURL(file);

            // Prepare to upload the image
            const formData = new FormData();
            formData.append('file', file);
            formData.append('currentPage', window.location.pathname); // Optional: Send current page info

            // Upload the file via AJAX
            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        messageDiv.innerHTML = '';  // Clear any message
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
