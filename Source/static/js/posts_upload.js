document.addEventListener('DOMContentLoaded', () => {
    const addPostBtn = document.getElementById('addPostBtn');
    const fileInput = document.getElementById('file');
    const messageDiv = document.getElementById('message');

    // 1. click “Add Post” → open file chooser
    addPostBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // 2. file selected → upload immediately
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) {
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('currentPage', window.location.pathname);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = '';
                } else {
                    messageDiv.innerHTML = `<p style="color:red;">${data.message}</p>`;
                }
            })
            .catch(err => {
                console.error(err);
                messageDiv.innerHTML = `<p style="color:red;">Upload error</p>`;
            });
    });
});
