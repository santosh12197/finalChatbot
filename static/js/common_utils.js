


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

function scrollToBottom() {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
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

function greetUserWithBotTreeOptions(firstInteractionTimestamp, context = 'user') {
    const chatContainer = document.getElementById("chat-container")
    const greetingWrapper = document.createElement("div");
    greetingWrapper.className = "message-wrapper custom-greeting-wrapper";

    const greetingBubble = document.createElement("div");
    greetingBubble.className = "message-bubble custom-greeting-bubble bg-color-trans";

    const greetingText = document.createElement("div");
    greetingText.className = "message-text";

    const botLabel = document.createElement("div");
    botLabel.style.fontWeight = "bold";
    botLabel.textContent = "Robotica";

    const greetingContent = document.createElement("div");
    greetingContent.textContent = "Hi, I'm Robotica. How can I help you today?";

    greetingText.appendChild(botLabel);
    greetingText.appendChild(greetingContent);
    greetingBubble.appendChild(greetingText);
    greetingWrapper.appendChild(greetingBubble);

    if (context === 'support') {
        greetingWrapper.classList.add('support-msg');
    } else {
        greetingWrapper.classList.add('user-msg');
    }

    chatContainer.appendChild(greetingWrapper);

    const optionsWrapper = document.createElement("div");
    optionsWrapper.className = "message-wrapper custom-options-wrapper grey-bg-color";

    const optionsBubble = document.createElement("div");
    optionsBubble.className = "message-bubble custom-options-bubble";

    const buttonRow = document.createElement("div");
    buttonRow.className = "bubble-row";

    Object.keys(botTree).forEach(text => {
        const bubble = document.createElement("div");
        bubble.className = "bot-bubble-inline";
        bubble.textContent = text;
        buttonRow.appendChild(bubble);
    });

    const optionsTimestamp = document.createElement("div");
    optionsTimestamp.className = "timestamp custom-timestamp";
    optionsTimestamp.textContent = firstInteractionTimestamp;

    optionsBubble.appendChild(buttonRow);
    optionsBubble.appendChild(optionsTimestamp);
    optionsWrapper.appendChild(optionsBubble);

    if (context === 'support') {
        optionsWrapper.classList.add('support-msg');
    } else {
        optionsWrapper.classList.add('user-msg');
    }

    chatContainer.appendChild(optionsWrapper);

    scrollToBottom();
}






