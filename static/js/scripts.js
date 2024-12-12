document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");

    sendButton.addEventListener("click", () => {
        envoyerMessage();
    });

    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            envoyerMessage();
        }
    });

    function envoyerMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        afficherMessage("user", message);
        userInput.value = "";

        fetch("/api/message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            afficherMessage("bot", data.response);
        })
        .catch(error => {
            console.error("Erreur:", error);
            afficherMessage("bot", "Désolé, une erreur est survenue.");
        });
    }

    function afficherMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);

        const textDiv = document.createElement("div");
        textDiv.classList.add("text");
        textDiv.innerHTML = text;

        messageDiv.appendChild(textDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
