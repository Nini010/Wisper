document.addEventListener("DOMContentLoaded", () => {
    const usernameInput = document.getElementById("username");
    const usernameError = document.getElementById("usernameError");
    const submitButton = document.querySelector(".continue-btn");

    usernameInput.addEventListener("input", () => {
        const username = usernameInput.value;

        // Hide the error message while typing
        usernameError.style.display = "none";
        submitButton.disabled = false;

        if (username) {
            // Make an AJAX request to check the username
            fetch('/checkUsername', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.exists) {
                        // Show the error message and disable the submit button
                        usernameError.style.display = "block";
                        usernameError.textContent = "Username is already taken.";
                        submitButton.disabled = true;
                    } else {
                        // Ensure the submit button is enabled if the username is available
                        submitButton.disabled = false;
                    }
                })
                .catch((error) => {
                    console.error("Error checking username:", error);
                });
        }
    });
});