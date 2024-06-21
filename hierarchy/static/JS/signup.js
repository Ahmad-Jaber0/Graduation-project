document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password1');
    const confirmPasswordInput = document.getElementById('password2');
    const passwordMatchMessage = document.createElement('p');
    passwordMatchMessage.id = 'password-match-message';
    passwordMatchMessage.style.color = 'red';
    passwordInput.parentNode.appendChild(passwordMatchMessage);

    function updateButtonStatus() {
        const isEmpty = Array.from(document.querySelectorAll('input')).some(input => input.value.trim() === '');
        if (isEmpty || passwordInput.value !== confirmPasswordInput.value) {
            document.getElementById('signupButton').disabled = true;
        } else {
            document.getElementById('signupButton').disabled = false;
        }
    }

    function checkPasswordMatch() {
        if (passwordInput.value !== confirmPasswordInput.value) {
            passwordMatchMessage.textContent = 'Passwords do not match.';
            passwordMatchMessage.style.display = 'block';
            document.getElementById('signupButton').disabled = true;
        } else {
            passwordMatchMessage.textContent = '';
            passwordMatchMessage.style.display = 'none';
            updateButtonStatus();
        }
    }

    passwordInput.addEventListener('input', checkPasswordMatch);
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    updateButtonStatus();
});
