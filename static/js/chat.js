document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    
    const botTree = {
        "Payment Failure": {
            "Card Payment Failure": {
                "MasterCard": "Thank you for connecting. You can retry again.",
                "Visa": "Thank you for connecting. You can retry again.",
                "Other Card": "We only use Visa or Master card for payment. Please use these cards only."
            },
            "Bank Transfer Failure": "Thank you for connecting. You can retry again."
        },
        "Refund Issues": {
            "Refund Status": "Your refund is being processed.",
            "Refund Delay": "Sorry for the delay, it's being reviewed.",
            "Refund Request": "Refund request submitted."
        },
        "Invoice Requests": {
            "Invoice not received": "We'll send your invoice shortly.",
            "Incorrect Invoice": "Please share the correct invoice details."
        },
        "Other Payment Queries": {
            "General Payment Enquiry": "Please describe your issue.",
            "payer change/modification": "We can help with that. Connecting...",
            "payment method Enquiry": "Available methods: Card, Bank, Wallet.",
            "membership/account inquiry": "Please specify your account issue.",
            "hold payment Request": "Your request has been noted.",
            "license / billing info": "Please provide your license ID.",
            "installments/discount": "Installments can be discussed further.",
            "Waiver/other Issues": "Our team will review your waiver.",
            "signed document Request": "Please upload your document.",
            "Payment receipt Request": "We will resend your receipt shortly."
        }
    };

    let conversationPath = []; // Tracks current path in the botTree

    function renderOptions(options) {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        Object.keys(options).forEach(option => {
            const btn = document.createElement("button");
            btn.className = "btn btn-outline-primary  option-button btn-custom-grey";
            btn.textContent = option;
            btn.addEventListener("click", () => handleOptionClick(option, options[option]));
            wrapper.appendChild(btn);
        });

        chatContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function handleOptionClick(label, next) {
        appendMessage(label, 'user');
        console.log("USer")
        saveMessageToDB(label, 'user');
        console.log("typeof next ", typeof next, next)
        if (typeof next === 'string') {
            appendMessage(next, 'bot');
            console.log("Bot")
            saveMessageToDB(next, 'bot');
            showSatisfactionOptions();
        } else {
            const keyList = Object.keys(next).join(', ');
            saveMessageToDB(keyList, 'bot');
            renderOptions(next);
        }
        scrollToBottom();
    }

    function showSatisfactionOptions() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        appendMessage("Are you satisfied with the answer?", 'bot');
        saveMessageToDB("Are you satisfied with the answer?", "bot"); 

        const yesBtn = document.createElement("button");
        yesBtn.className = "btn btn-success option-button";
        yesBtn.textContent = "Yes, I'm satisfied";
        yesBtn.onclick = () => {
            appendMessage("Yes, I'm satisfied", "user"); // Show user reply
            saveMessageToDB("Yes, I'm satisfied", "user"); // saving user
            
            appendMessage("Thank you for connecting with SciPrisAptara.", "bot"); // Bot reply
            saveMessageToDB("Thank you for connecting with SciPrisAptara.", "bot"); // saving bot reply to db
            
            appendMessage("Hi! How can I help you today?", "bot");
            renderOptions(botTree); // Restart options
        };

        // to change logic
        const supportBtn = document.createElement("button");
        supportBtn.className = "btn btn-warning option-button";
        supportBtn.textContent = "No, Connect with the Support Team";
        supportBtn.onclick = () => {
            appendMessage("No, Connect with Support Team", "user"); // Show user reply
            appendMessage("Connecting you to our support team...", "bot");
            window.location.href = "/support/"; // to change 
        };
    
        wrapper.appendChild(yesBtn);
        wrapper.appendChild(supportBtn);
        chatContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function appendMessage(text, sender) {
        const message = document.createElement("div");
        message.className = sender === 'bot' ? 'bot-message align-self-start' : 'user-message align-self-end';
        message.textContent = text;
        chatContainer.appendChild(message);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function saveMessageToDB(message, sender) {
        fetch("/save_message/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // CSRF is needed for POST in Django
            },
            body: JSON.stringify({
                message: message,
                sender: sender
            })
        });
    }
    
    function getCSRFToken() {
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
    }
    

    // Initial message
    appendMessage("Hi! How can I help you today?", "bot");
    renderOptions(botTree);
});
