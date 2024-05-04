document.getElementById("login-form").addEventListener("submit", function(event) {
    event.preventDefault(); 

    const formData = new FormData(this);

    fetch("/login/", {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest", 
            "X-CSRFToken": "{{ csrf_token }}" 
        }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = response.url;
        } else {
            return response.json(); 
        }
    })
    .then(data => {
        const errorMessage = document.getElementById("error-message");
        errorMessage.textContent = data.message;
        errorMessage.style.color = "white";
        errorMessage.style.display = "block";
    })
    .catch(error => {
        console.error("Error:", error);
    });
});