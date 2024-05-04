document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username');
    const signUpButton = document.querySelector('button[type="submit"]');
    const passwordInput = document.getElementById('password1');
    const confirmPasswordInput = document.getElementById('password2');
    const passwordMatchMessage = document.getElementById('password-match-message');
    const errorMessage = document.getElementById('username-message');

    function updateButtonStatus() {
        const isEmpty = Array.from(document.querySelectorAll('input')).some(input => input.value.trim() === '');
        if (isEmpty || passwordInput.value !== confirmPasswordInput.value) {
            signUpButton.disabled = true;
        } else {
            signUpButton.disabled = false;
        }
    }

    function checkPasswordMatch() {
        if (passwordInput.value !== confirmPasswordInput.value) {
            passwordMatchMessage.textContent = 'Passwords do not match.';
            passwordMatchMessage.style.display = 'block';
            signUpButton.disabled = true;
        } else {
            passwordMatchMessage.textContent = '';
            passwordMatchMessage.style.display = 'none';
            updateButtonStatus();
        }
    }

    signUpButton.addEventListener('click', function() {
        checkPasswordMatch();
    });

    passwordInput.addEventListener('input', function() {
        checkPasswordMatch();
    });

    confirmPasswordInput.addEventListener('input', function() {
        checkPasswordMatch();
    });


    updateButtonStatus();
});