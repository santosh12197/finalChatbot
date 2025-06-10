document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container")
    let chatSocket; // Declare it globally to be accessible in send/receive. 
    let support_agent_id = null;

    function renderOptions(options) {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper options-wrapper";

        const buttonContainer = document.createElement("div");
        buttonContainer.className = "button-container";  // Container to hold buttons in a row


        Object.keys(options).forEach(option => {
            const btn = document.createElement("button");
            btn.className = "btn btn-outline-primary option-button btn-custom-grey";
            btn.textContent = option;

            btn.addEventListener("click", async () => {
                // Disable all buttons when one is clicked
                const allButtons = wrapper.querySelectorAll("button");
                allButtons.forEach(button => button.disabled = true);

                await handleOptionClick(option, options[option]);
            });

            buttonContainer.appendChild(btn);
        });

        // Create a shared timestamp div
        const timestampSpan  = document.createElement("span");
        timestampSpan.className = "options-timestamp";
        timestampSpan.textContent = getCurrentFormattedTimestamp();

        wrapper.appendChild(buttonContainer);
        wrapper.appendChild(timestampSpan );
        chatContainer.appendChild(wrapper);
        scrollToBottom();
    }


    async function handleOptionClick(label, next) {
        // show the selected option by the user
        appendMessage(label, 'user', getCurrentFormattedTimestamp());

        // save the key of the botTree selected by user in the table sequentially
        await saveMessageToDB(label, 'user', is_read=true, requested_for_support=false, support_agent_id=null);

        // display and save other options by the bot
        if (typeof next === 'string') {
            // meaning that we are at the leaf of the botTree
            // display message, save to db, and then ask for satisfaction check
            appendMessage(next, 'bot', getCurrentFormattedTimestamp());
            await saveMessageToDB(next, 'bot', is_read=true, requested_for_support=false, support_agent_id=null);

            // check user is satisfied by the response or not only at the leaf of the tree
            // Ask for satisfaction only after bot response saved
            await showSatisfactionOptions();
        } else {
            // meaning that we are not at the leaf of the botTree
            // first save key to db, and then call renderOptions() method so that we will reach till leaf of the botTree
            const keyList = Object.keys(next).join('; ');
            await saveMessageToDB(keyList, 'bot', is_read=true, requested_for_support=false, support_agent_id=null);
            renderOptions(next);
        }
        scrollToBottom();
    }

    async function showSatisfactionOptions() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper";

        const question = "Are you satisfied with the answer?;\n Yes, I'm satisfied.; \n No, Connect with the Support Team";
        appendMessage("Are you satisfied with the answer?", 'bot', getCurrentFormattedTimestamp());
        await saveMessageToDB(question, "bot", is_read=true, requested_for_support=false, support_agent_id=null); 

        const yesBtn = document.createElement("button");
        yesBtn.className = "btn btn-success option-button";
        yesBtn.textContent = "Yes, I'm satisfied.";
        yesBtn.onclick = async () => {
            // Disable all buttons when one is clicked
            const allButtons = wrapper.querySelectorAll("button");
            allButtons.forEach(button => button.disabled = true);

            appendMessage("Yes, I'm satisfied", "user", getCurrentFormattedTimestamp()); // Show user reply
            await saveMessageToDB("Yes, I'm satisfied.", "user", is_read=true, requested_for_support=false, support_agent_id=null); // saving chat data for the user

            const thankYouMsg = "Thank you for connecting with SciPris Aptara.";
            const greetMsg = "Hi, I'm Robotica. How can I help you today?";
            const combined = `${thankYouMsg}; \n ${greetMsg}; \n Payment Failure; \n Refund Issues; \n Invoice Requests; \n Other Payment Queries`;

            appendMessage(thankYouMsg, "bot", getCurrentFormattedTimestamp()); // Bot reply
            await saveMessageToDB(combined, "bot", is_read=true, requested_for_support=false, support_agent_id=null); // saving to db
            
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
            await saveMessageToDB("No, Connect with Support Team", "user", is_read=true, requested_for_support=true, support_agent_id=null); // saving user

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
        // TODO: replace currentUserId with support agent involved
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
                        await saveMessageToDB(successMessage, "bot", true, true, support_agent_id=null);
                    }

                    if (!data.welcome_sent) {
                        // To check this section again
                        appendMessage(welcomeMessage, "support", getCurrentFormattedTimestamp());
                        await saveMessageToDB(welcomeMessage, "support", true, true, support_agent_id=null);
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
                appendMessage(data.message,  data.sender, data.timestamp, data.support_full_name);
                // saveMessageToDB(data.message, sender);
                scrollToBottom();
            }
        };
    
        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        // user sends msg
        sendButton.onclick = async () => {
            // get support agent id for this user having active chat
            const support_agent_id = await fetchAssignedSupportAgent();  // Wait for backend response

            if (inputField.value.trim() !== '') {
                chatSocket.send(JSON.stringify({ // send msg over websocket to the backend
                    'message': inputField.value, 
                    'sender': "user",
                    'user_id': currentUserId,
                    'support_agent_id': support_agent_id
                }));
                inputField.value = '';
            }
        };
    
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendButton.click();
        });
    }
    
    async function fetchAssignedSupportAgent() {
        return fetch("/get_assigned_support_agent/")
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    support_agent_id = data.support_agent_id;
                    return support_agent_id
                }else{
                    support_agent_id = null;
                    return support_agent_id
                }
            })
            .catch(error => {
                console.error("Error fetching support agent:", error);
                return null;
            });

    }

    function appendMessage(text, sender, timestampStr, supportFullName="") {
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

                // "Robotica " prefix in bold
                const botLabel = document.createElement("div");
                botLabel.style.fontWeight = "bold";
                botLabel.textContent = "Robotica ";

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

                const botLabel = document.createElement("div");
                botLabel.style.fontWeight = "bold";
                botLabel.textContent = "Robotica";

                const messageContent = document.createElement("span");
                messageContent.textContent = text;

                messageText.appendChild(botLabel);
                messageText.appendChild(messageContent);
            } else if (sender === 'support') {
                message.className = 'support-message align-self-start message-bubble';
                // Support name and msg are in seperate lines
                const supportName = document.createElement("div");
                supportName.style.fontWeight = "bold";
                supportName.textContent = supportFullName;

                const messageLine = document.createElement("div");
                messageLine.textContent = text;

                messageText.appendChild(supportName);
                messageText.appendChild(messageLine);
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

    function saveMessageToDB(message, sender, is_read=false, requested_for_support=requested_for_support, support_agent_id=null) {
        return fetch("/save_message/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // CSRF is needed for POST in Django
            },
            body: JSON.stringify({
                user_id: currentUserId,
                support_agent_id: support_agent_id,
                message: message,
                sender: sender,
                is_read: is_read,
                requested_for_support: requested_for_support
            })
        });
    }

    function renderGroupedMessages(messages) {
        if (!messages || messages.length === 0) return;

        messages.forEach(msg => {
            const sender = msg.sender;
            const supportName = msg.support_full_name || null;
            const content = msg.message;
            const timestamp = msg.timestamp;

            const wrapper = document.createElement("div");
            wrapper.classList.add("message-wrapper", "group-wrapper");

            // Alignment
            if (sender === 'user') {
                wrapper.classList.add("align-self-end", "user-group");
            } else if (sender === 'support') {
                wrapper.classList.add("align-self-start", "support-group");
            } else if (sender === 'bot') {
                wrapper.classList.add("align-self-start", "bot-group");
            }

            // Support name
            if (sender === 'support' && supportName) {
                const nameDiv = document.createElement("div");
                nameDiv.className = "support-name";
                nameDiv.textContent = supportName;
                wrapper.appendChild(nameDiv);
            }

            // Bot Label
            if (sender === 'bot') {
                const roboticaLabel = document.createElement("div");
                roboticaLabel.textContent = "Robotica";
                roboticaLabel.style.fontWeight = "bold";
                roboticaLabel.style.marginBottom = "6px";
                wrapper.appendChild(roboticaLabel);
            }

            const bubble = document.createElement("div");
            bubble.classList.add("message-bubble");

            // BOT: inline bubbles split by ;
            if (sender === 'bot' && content.includes(";")) {
                const row = document.createElement("div");
                row.className = "bubble-row";
                content.split(";").map(p => p.trim()).filter(Boolean).forEach(part => {
                    const partBubble = document.createElement("div");
                    partBubble.className = "bot-bubble-inline";
                    partBubble.textContent = part;
                    row.appendChild(partBubble);
                });
                bubble.appendChild(row);
            } else {
                // Single message for user/support/bot without semicolon
                const textDiv = document.createElement("div");
                textDiv.className = "message-text";
                textDiv.textContent = content;
                bubble.appendChild(textDiv);
            }

            // Timestamp
            const ts = document.createElement("div");
            ts.className = "bubble-timestamp";
            ts.textContent = timestamp;
            bubble.appendChild(ts);

            wrapper.appendChild(bubble);
            chatContainer.appendChild(wrapper);
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
                // Load past chat messages
                renderGroupedMessages(data.messages); // Use updated function here
                // Connect with the support team
                enableRealTimeChat();
            } else {
                // Start chatbot normally
                appendMessage("Hi, I'm Robotica. How can I help you today?", "bot", getCurrentFormattedTimestamp());
                renderOptions(botTree);
            }
        });
        
});
