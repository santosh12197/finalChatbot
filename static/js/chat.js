document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container")

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
    let chatSocket; // Declare it globally to be accessible in send/receive.

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
        saveMessageToDB(label, 'user', is_read=true, requested_for_support=false);

        // display and save other options by the bot
        if (typeof next === 'string') {
            // meaning that we are at the leaf of the botTree
            // display message, save to db, and then ask for satisfaction check
            appendMessage(next, 'bot');
            saveMessageToDB(next, 'bot', is_read=true, requested_for_support=false);

            // check user is satisfied by the response or not only at the leaf of the tree
            showSatisfactionOptions();
        } else {
            // meaning that we are not at the leaf of the botTree
            // first save key to db, and then call renderOptions() method so that we will reach till leaf of the botTree
            const keyList = Object.keys(next).join('; ');
            saveMessageToDB(keyList, 'bot', is_read=true, requested_for_support=false);
            renderOptions(next);
        }
        scrollToBottom();
    }

    function showSatisfactionOptions() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        appendMessage("Are you satisfied with the answer?", 'bot');
        saveMessageToDB("Are you satisfied with the answer?\n Yes, I am satisfied \n No, Connect with the Support Team", "bot", is_read=true, requested_for_support=false); 

        const yesBtn = document.createElement("button");
        yesBtn.className = "btn btn-success option-button";
        yesBtn.textContent = "Yes, I'm satisfied";
        yesBtn.onclick = () => {
            appendMessage("Yes, I'm satisfied", "user"); // Show user reply
            saveMessageToDB("Yes, I'm satisfied", "user", is_read=true, requested_for_support=false); // saving chat data for the user
            
            appendMessage("Thank you for connecting with SciPris Aptara.", "bot"); // Bot reply
            saveMessageToDB("Thank you for connecting with SciPris Aptara.; \n Hi! How can I help you today?; \n Payment Failure; \n Refund Issues; \n Invoice Requests; \n Other Payment Queries", "bot", is_read=true, requested_for_support=false); // saving to db
            
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
            saveMessageToDB("No, Connect with Support Team", "user", is_read=true, requested_for_support=true); // saving user

            appendMessage("Connecting you to our support team...", "bot"); 
            appendMessage("Successfully connected with the support team", "bot"); 
            saveMessageToDB("Connecting you to our support team...;\n Successfully connected with the support team", "bot", is_read=true, requested_for_support=true); // saving bot

            // connecting with the support team
            enableRealTimeChat();
        };
    
        wrapper.appendChild(yesBtn);
        wrapper.appendChild(supportBtn);
        chatContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function enableRealTimeChat() {
        // Input field and Send button will be added dynamically by JS inside in this
        const inputWrapper = document.getElementById('input-wrapper');
        if (inputWrapper.hasChildNodes()) return; // prevent duplicate input

        // Mark this user as having requested support in the backend
        fetch("/mark_support_request/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ requested: true })
        });

        // creating "input field" where user can type msg to chat with the support team
        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.placeholder = 'Type your message...';
        inputField.className = 'chat-input form-control';

        // creating "Send" button to send the msg
        const sendButton = document.createElement('button');
        sendButton.className = 'btn btn-primary';
        sendButton.textContent = 'Send';

        // inserting input field and Send button inside inputWrapper div
        inputWrapper.appendChild(inputField);
        inputWrapper.appendChild(sendButton);

        scrollToBottom();

        const roomName = "support_" + currentUserId; // currentUserId is from html file chat.html
        // websocket connection of current user
        chatSocket = new WebSocket(
            (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
            window.location.host +
            '/ws/support/' + roomName + '/'
        );

        // msg received from the backend by the frontend
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.message) {
                appendMessage(data.message, data.sender);
                // saveMessageToDB(data.message, sender);
                scrollToBottom();
            }
        };
    
        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        // user sends msg
        sendButton.onclick = () => {
            if (inputField.value.trim() !== '') {
                chatSocket.send(JSON.stringify({ // send msg over websocket to the backend
                    'message': inputField.value, 
                    'sender': "user",
                    'user_id': currentUserId
                }));
                inputField.value = '';
            }
        };
    
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendButton.click();
        });
    }
    

    function appendMessage(text, sender) {
        const message = document.createElement("div");
        if (sender === 'bot') {
            message.className = 'bot-message align-self-start';
        } else if (sender === 'support') {
            message.className = 'support-message align-self-start';
        } else {
            message.className = 'user-message align-self-end';
        }
        message.textContent = text;
        chatContainer.appendChild(message);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function saveMessageToDB(message, sender, is_read=false, requested_for_support=requested_for_support) {
        fetch("/save_message/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // CSRF is needed for POST in Django
            },
            body: JSON.stringify({
                user_id: currentUserId,
                message: message,
                sender: sender,
                is_read: is_read,
                requested_for_support: requested_for_support
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
