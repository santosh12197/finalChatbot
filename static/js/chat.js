document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    
    const botTree = {
        "Payment Failure": {
            "Card Payment Failure": {
                "Master Card": "Thank you for connecting. You can try again.",
                "Visa Card": "Thank you for connecting. You can try again.",
                "Other Card": "We only use Visa or Master card for payment. Please use these cards only."
            },
            "Bank Transfer Failure": "Thank you for connecting. You can try again."
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
            "General Payment Inquiry": "Please describe your issue.",
            "Payer Change/Modification": "We can help with that. Connecting...",
            "Payment Method Inquiry": "Available methods: Card, Bank, Wallet.",
            "Membership/Account Inquiry": "Please specify your account issue.",
            "Hold Payment Request": "Your request has been noted.",
            "License / Billing Info": "Please provide your license ID.",
            "Installments/Discount": "Installments can be discussed further.",
            "Waiver/Other Issues": "Our team will review your waiver.",
            "Signed Document Request": "Please upload your document.",
            "Payment Receipt Request": "We will resend your receipt shortly."
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
        // show the selected option by the user
        appendMessage(label, 'user');

        // save the key of the botTree selected by user in the table
        saveMessageToDB(label, 'user');

        // display and save other options by the bot
        if (typeof next === 'string') {
            // meaning that we are at the leaf of the botTree
            // display message, save to db, and then ask for satisfaction check
            appendMessage(next, 'bot');
            saveMessageToDB(next, 'bot');

            // check user is satisfied by the response or not only at the leaf of the tree
            showSatisfactionOptions();
        } else {
            // meaning that we are not at the leaf of the botTree
            // first save key to db, and then call renderOptions() method so that we will reach till leaf of the botTree
            const keyList = Object.keys(next).join('; ');
            saveMessageToDB(keyList, 'bot');
            renderOptions(next);
        }
        scrollToBottom();
    }

    function showSatisfactionOptions() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        appendMessage("Are you satisfied with the answer?", 'bot');
        saveMessageToDB("Are you satisfied with the answer?\n Yes, I am satisfied \n No, Connect with the Support Team", "bot"); 

        const yesBtn = document.createElement("button");
        yesBtn.className = "btn btn-success option-button";
        yesBtn.textContent = "Yes, I'm satisfied";
        yesBtn.onclick = () => {
            appendMessage("Yes, I'm satisfied", "user"); // Show user reply
            saveMessageToDB("Yes, I'm satisfied", "user"); // saving chat data for the user
            
            appendMessage("Thank you for connecting with SciPris Aptara.", "bot"); // Bot reply
            saveMessageToDB("Thank you for connecting with SciPris Aptara.; \n Hi! How can I help you today?; \n Payment Failure; \n Refund Issues; \n Invoice Requests; \n Other Payment Queries", "bot"); // saving to db
            
            appendMessage("Hi! How can I help you today?", "bot");
            renderOptions(botTree); // Restart options
        };

        // when user is not satisfied with the bot response
        // connect with the support team
        const supportBtn = document.createElement("button");
        supportBtn.className = "btn btn-warning option-button";
        supportBtn.textContent = "No, Connect with the Support Team";
        supportBtn.onclick = () => {
            appendMessage("No, Connect with Support Team", "user"); // Show user reply
            saveMessageToDB("No, Connect with Support Team", "user"); // saving user

            appendMessage("Connecting you to our support team...", "bot"); 
            saveMessageToDB("Connecting you to our support team...", "bot"); // saving bot

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
