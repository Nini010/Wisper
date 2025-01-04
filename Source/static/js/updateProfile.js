document.getElementById('submitButton').addEventListener('click', async function () {
    const name = document.getElementById('name').value;
    const dob = document.getElementById('dob').value;
    const email = document.getElementById('email').value;
    const number = document.getElementById('number').value;

    const formData = new FormData();
    formData.append('name', name);
    formData.append('dob', dob);
    formData.append('email', email);
    formData.append('number', number);

    try {
        const response = await fetch('/updateProfile', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            window.location.href = '/chats';
        } else {
            console.error('Failed to update profile', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
