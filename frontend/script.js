const input = document.getElementById('user-input');
const sendBtn = document.querySelector("button");
const messagesDiv = document.querySelector("#messages");

let API_URL = "http://127.0.0.1:8000/core/chat";  // Update URL if necessary

// Function to send the message
async function sendMessage() {
    if (input.value.length > 0) {
        const userMessage = input.value;
        input.value = "";  // Clear the input field

        // Display user's message
        let userChat = `
        <div class="chat message">
        <img src="frontend/img/user1.jpeg"> 
            <span>${userMessage}</span>
        </div>`;
        messagesDiv.insertAdjacentHTML("beforeend", userChat);

        // Display "Bot is typing" message
        let botResponsePlaceholder = `
        <div class="chat response">
            <span class="bot-typing">...</span>
        </div>`;
        messagesDiv.insertAdjacentHTML("beforeend", botResponsePlaceholder);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;  // Scroll to the bottom

        try {
            // Send message to the backend
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_message: userMessage }),
            };

            const response = await fetch(API_URL, requestOptions);
            const data = await response.json();

            // Replace the "Bot is typing" message with the actual response
            const botResponse = document.querySelector(".bot-typing");
            botResponse.innerHTML = `<img src="frontend/img/chatbot.jpg"> ${data.response}`;
            botResponse.classList.remove("bot-typing");

        } catch (error) {
            // In case of an error, show an error message
            const botResponse = document.querySelector(".bot-typing");
            botResponse.innerHTML = "Oops! An error occurred. Please try again.";
        }
    }
}

// Send message on button click
sendBtn.onclick = sendMessage;

// Send message on pressing the "Enter" key
input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();  // Prevent default action (form submission or other behavior)
        sendMessage();  // Call the function to send the message
    }
});
