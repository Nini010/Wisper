document.addEventListener('DOMContentLoaded', () => {
    const sentButton = document.getElementById('sentButton');
    const receivedButton = document.getElementById('receivedButton');

    sentButton.addEventListener('click', () => {
        sentButton.classList.add('active');
        receivedButton.classList.remove('active');
    });

    receivedButton.addEventListener('click', () => {
        receivedButton.classList.add('active');
        sentButton.classList.remove('active');
    });
});
