document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container")

    const botTree = {
        "Payment Failure": {
            "Card Payment Failure": {
                "Master Card": "Thank you for connecting. You can try again with Master Card.",
                "Visa Card": "Thank you for connecting. You can try again. You can try again with Visa Card.",
                "Other Card": "We only use Visa or Master card for payment. Please use these cards only."
            },
            "Bank Transfer Failure": "Thank you for connecting. Pls try again."
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
            btn.className = "btn btn-outline-primary option-button btn-custom-grey";
            btn.textContent = option;

            // Create a timestamp span
            const timestampSpan = document.createElement("span");
            timestampSpan.className = "option-timestamp";
            timestampSpan.textContent = getCurrentFormattedTimestamp();

            btn.addEventListener("click", async () => {
                // Disable all buttons when one is clicked
                const allButtons = wrapper.querySelectorAll("button");
                allButtons.forEach(button => button.disabled = true);

                await handleOptionClick(option, options[option]);
            });

            // Append the timestamp inside the button
            btn.appendChild(timestampSpan);

            wrapper.appendChild(btn);
        });

        chatContainer.appendChild(wrapper);
        scrollToBottom();
    }


    async function handleOptionClick(label, next) {
        // show the selected option by the user
        appendMessage(label, 'user', getCurrentFormattedTimestamp());

        // save the key of the botTree selected by user in the table sequentially
        await saveMessageToDB(label, 'user', is_read=true, requested_for_support=false);

        // display and save other options by the bot
        if (typeof next === 'string') {
            // meaning that we are at the leaf of the botTree
            // display message, save to db, and then ask for satisfaction check
            appendMessage(next, 'bot', getCurrentFormattedTimestamp());
            await saveMessageToDB(next, 'bot', is_read=true, requested_for_support=false);

            // check user is satisfied by the response or not only at the leaf of the tree
            // Ask for satisfaction only after bot response saved
            await showSatisfactionOptions();
        } else {
            // meaning that we are not at the leaf of the botTree
            // first save key to db, and then call renderOptions() method so that we will reach till leaf of the botTree
            const keyList = Object.keys(next).join('; ');
            await saveMessageToDB(keyList, 'bot', is_read=true, requested_for_support=false);
            renderOptions(next);
        }
        scrollToBottom();
    }

    async function showSatisfactionOptions() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        const question = "Are you satisfied with the answer?;\n Yes, I'm satisfied.; \n No, Connect with the Support Team";
        appendMessage("Are you satisfied with the answer?", 'bot', getCurrentFormattedTimestamp());
        await saveMessageToDB(question, "bot", is_read=true, requested_for_support=false); 

        const yesBtn = document.createElement("button");
        yesBtn.className = "btn btn-success option-button";
        yesBtn.textContent = "Yes, I'm satisfied.";
        yesBtn.onclick = async () => {
            // Disable all buttons when one is clicked
            const allButtons = wrapper.querySelectorAll("button");
            allButtons.forEach(button => button.disabled = true);

            appendMessage("Yes, I'm satisfied", "user", getCurrentFormattedTimestamp()); // Show user reply
            await saveMessageToDB("Yes, I'm satisfied.", "user", is_read=true, requested_for_support=false); // saving chat data for the user

            const thankYouMsg = "Thank you for connecting with SciPris Aptara.";
            const greetMsg = "Hi! How can I help you today?";
            const combined = `${thankYouMsg}; \n ${greetMsg}; \n Payment Failure; \n Refund Issues; \n Invoice Requests; \n Other Payment Queries`;

            appendMessage(thankYouMsg, "bot", getCurrentFormattedTimestamp()); // Bot reply
            await saveMessageToDB(combined, "bot", is_read=true, requested_for_support=false); // saving to db
            
            appendMessage(greetMsg, "bot", getCurrentFormattedTimestamp());
            renderOptions(botTree); // Restart options
        };

        // when user is not satisfied with the bot response
        // connect with the support team
        const supportBtn = document.createElement("button");
        supportBtn.className = "btn btn-warning option-button";
        supportBtn.textContent = "No, Connect with the Support Team";
        supportBtn.onclick = async () => {
            // Disable all buttons when one is clicked
            const allButtons = wrapper.querySelectorAll("button");
            allButtons.forEach(button => button.disabled = true);
            
            appendMessage("No, Connect with Support Team", "user", getCurrentFormattedTimestamp()); // Show user reply
            await saveMessageToDB("No, Connect with Support Team", "user", is_read=true, requested_for_support=true); // saving user

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

        // Once connected, send initial support welcome message
        chatSocket.onopen = async () => {
            try {
                const response = await fetch("/has_welcome_messages/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ user_id: currentUserId })
                });

                const data = await response.json();

                if (!data.both_sent) {
                    const successMessage = "Successfully connected with the support team.";
                    const welcomeMessage = "Welcome to SciPris. How can I help you?";

                    if (!data.success_sent) {
                        appendMessage(successMessage, "bot", getCurrentFormattedTimestamp());
                        await saveMessageToDB(successMessage, "bot", true, true);
                    }

                    if (!data.welcome_sent) {
                        appendMessage(welcomeMessage, "support", getCurrentFormattedTimestamp());
                        await saveMessageToDB(welcomeMessage, "support", true, true);
                    }
                }
                scrollToBottom();

            } catch (error) {
                console.error("Error checking welcome messages:", error);
            }
        };

        // msg received from the backend by the frontend
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.message && data.timestamp) {
                appendMessage(data.message,  data.sender, data.timestamp);
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
    

    function appendMessage(text, sender, timestampStr) {
        const messageWrapper = document.createElement("div");
        messageWrapper.classList.add("message-wrapper");

        // Check if bot message has semicolons
        if (sender === 'bot' && text.includes(';')) {
            const parts = text.split(';').map(part => part.trim()).filter(part => part !== "");

            parts.forEach(part => {
                // Create a separate message bubble for each part
                const message = document.createElement("div");
                const messageText = document.createElement("div");
                const timestamp = document.createElement("div");

                messageText.className = "message-text";
                timestamp.className = "timestamp";

                message.className = 'bot-message align-self-start message-bubble';

                // "Bot: " prefix in bold
                const botLabel = document.createElement("span");
                botLabel.style.fontWeight = "bold";
                botLabel.textContent = "Bot: ";

                const messageContent = document.createElement("span");
                messageContent.textContent = part;

                messageText.appendChild(botLabel);
                messageText.appendChild(messageContent);

                timestamp.textContent = timestampStr;

                message.appendChild(messageText);
                message.appendChild(timestamp);
                messageWrapper.appendChild(message);
            });

        } else {
            // Single message bubble (bot/user/support) - normal flow
            const message = document.createElement("div");
            const messageText = document.createElement("div");
            const timestamp = document.createElement("div");

            messageText.className = "message-text";
            timestamp.className = "timestamp";

            if (sender === 'bot') {
                message.className = 'bot-message align-self-start message-bubble';

                const botLabel = document.createElement("span");
                botLabel.style.fontWeight = "bold";
                botLabel.textContent = "Bot: ";

                const messageContent = document.createElement("span");
                messageContent.textContent = text;

                messageText.appendChild(botLabel);
                messageText.appendChild(messageContent);
            } else if (sender === 'support') {
                message.className = 'support-message align-self-start message-bubble';
                messageText.textContent = text;
            } else {
                message.className = 'user-message align-self-end message-bubble';
                messageText.textContent = text;
            }

            timestamp.textContent = timestampStr;

            message.appendChild(messageText);
            message.appendChild(timestamp);
            messageWrapper.appendChild(message);
        }

        chatContainer.appendChild(messageWrapper);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function saveMessageToDB(message, sender, is_read=false, requested_for_support=requested_for_support) {
        return fetch("/save_message/", {
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
    
    function getCurrentFormattedTimestamp() {
        const now = new Date();
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();

        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'

        const hourStr = String(hours).padStart(2, '0');

        return `${day}/${month}/${year} ${hourStr}:${minutes} ${ampm}`;
    }

    function greetUserWithBotTreeOptions(firstInteractionTimestamp) {
        // First line: greeting
        const greeting = "Hi! How can I help you today?";
        appendMessage(greeting, "bot", firstInteractionTimestamp);

        // Four lines: each top-level key of the botTree
        Object.keys(botTree).forEach(key => {
            appendMessage(`${key}`, "bot", firstInteractionTimestamp);
        });

        scrollToBottom();
    }

    // On page load
    // if user already has a support chat session, then load chat history and connect with support team for real chat
    // otherwise, start a new chat with bot
    fetch('/check_support_chat/')
        .then(response => response.json())
        .then(data => {
            firstInteractionTimestamp = data.first_interaction_timestamp;
            // if user has already started chat with support team
            // then load the chat history and, then connect with the support team
            // otherwise, start with the fresh chat
            if (data.support_chat_exists) {
                // first greeting lines and then options to start chat with the bot
                greetUserWithBotTreeOptions(firstInteractionTimestamp);
                // Load past support messages
                data.messages.forEach(msg => {
                    appendMessage(msg.message, msg.sender, msg.timestamp);
                });

                // Connect with the support team
                enableRealTimeChat();
            } else {
                // Start chatbot normally
                appendMessage("Hi! How can I help you today?", "bot", getCurrentFormattedTimestamp());
                renderOptions(botTree);
            }
        });
        
});
