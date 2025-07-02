

// botTree for SciPris
const botTree1 = {
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

const visa_or_master_card_used_scenario = {
    "OTP not Received": "Try again.",
    "Card Expired": "Try using different Visa card / Master card.",
    "Incorrect Card Detail Entered": "Please enter correct card details."
}

const bank_transfer_failure_flow = {
    "Visa / Master Card Used": {
        "Bank Declined the Transfer": "Contact your bank or support team.",
        "Amount deducted, but not confirmed": "Wait till 30-60 min., check with bank, or connect with the support team."
    },
    "Other Than Visa / Master Card Used": "Please try with Visa / Master card only."
}

// final SciPris botTree
const botTree = {

    "Payment Failure": {
        "Card Payment Failure": {
            "Card Declined / Blocked":{
                "Visa / Master Card Used": {
                    "OTP not Received": "Try again.",
                    "Card Expired": "Try using different Visa card / Master card.",
                    "Incorrect Card Detail Entered": "Please enter correct card details."
                },
                "Other Than Visa / Master Card Used": "Please try with Visa / Master card only.",
                "Authentication Error (e.g., OTP failed etc.)": "Try different Visa / Master card or retry again." 
            },
            "Payment timed out / frozen": {
                "Visa / Master Card Used": {
                    "OTP not Received": "Try again.",
                    "Card Expired": "Try using different Visa card / Master card.",
                    "Incorrect Card Detail Entered": "Please enter correct card details."
                },
                "Other Than Visa / Master Card Used": "Please try with Visa / Master card only."
            }

        },
        "Bank Transfer Failure": {
            "Visa / Master Card Used": {
                "Bank Declined the Transfer": "Contact your bank or support team.",
                "Amount deducted, but not confirmed": "Wait till 30-60 min., check with bank, or connect with the support team."
            },
            "Other Than Visa / Master Card Used": "Please try with Visa / Master card only."
        }
    },

    "Refund Issues": {
        "Refund Delay": {
            "Mode of Refund": {
                "Card": {
                    "Visa / Master Card Used": {
                        "OTP Not Received": "Try Again.",
                        "Card Expired": "Try different Visa / Master Card."
                    },
                    "Other Than Visa / Master Card Used": "Please try with Visa / Master card only."
                },
                "Bank Transfer": {
                    "Visa / Master Card Used": {
                        "Bank Declined the Transfer": "Contact your bank or support team.",
                        "Amount deducted, but not confirmed": "Wait till 30-60 min., check with bank, or connect with the support team."
                    },
                    "Other Than Visa / Master Card Used": "Please try with Visa / Master card only."
                }
            }
        },
        "Refund Status":{
            "Status in portal / email": {
                "Pending": "If you have any doubt, then please connect with our support team.",
                "Processed": "If you have any doubt, then please connect with our support team.",
                "Failed": "If you have any doubt, then please connect with our support team."
            },
            "Want refund status update from support?": "Please connect with our support team."
        }
    },

    "Invoice Requests": {
        "Invoice Not Received": {
            "Payer has not generated invoice": {
                "Payer unaware of request": {
                    "Support shares payment link": {
                        "Payer accepts request": "Please connect with support team for more clarification.",
                        "Payer declines request": "Please connect with support team for more clarification."
                    },
                    "Support assigns new payer": "Please connect with support team."
                },
                "Payer login/reset issue": {
                    "Reset link sent but failed": "Please connect with support team for more clarification.",
                    "Payer stuck in reset process": "Please connect with support team for more clarification."
                }
            },
            "Payer has not received email": {
                "Support verifies payer email": {
                    "Email correct": "Please check in spam folder.",
                    "Email incorrect": "Please update correct email."
                },
                "Support resends payment link": {
                    "Payer receives link and invoice": "Proceed further with the provided link.",
                    "Payer still does not receive email": "Ask support to provide payment link."
                }
            }
        },

        "Incorrect Invoice": {
            "Invoice shows wrong amount": {
                "Extra color figure charges": {
                    "Support queries figure count": "Connect with the support.",
                    "Support clarifies figures": "Connect with the support for more clarification."
                },
                "Unexpected page charges": {
                    "Support questions page charge": "Connect with the support.",
                    "Support explains charge": "Connect with support to discuss further."
                }
            },
            "Incorrect billing details": {
                "Wrong name or institution": {
                    "Author requests correction": "Connect with the support.",
                    "Support issues updated invoice": "Connect with the support.",
                },
                "Wrong address or tax details": {
                    "Author requests correction": "Connect with the support.",
                    "Support updates and sends invoice": "Connect with the support."
                }
            },
            "Wrong payer email": {
                "Author requests reassignment": {
                    "Payer receives new link": "Proceed with the provided link.",
                    "Payer declines new payment request": "connect with the support team."
                },
                "Support forwards reassignment request": "connect with the support team."
            }
        }
    },

    "Other Payment Queries": {
        
        "Payment Process Modification": {
            "Change Payer Request": {
                "Support Asks Which Payer To Change": {
                    "User Provides Accurate Details": {
                        "Support Verifies New Payer": {
                            "Support Updates System": "Support updates payment system with new payer.",
                            "Support Sends Confirmation": "Support sends confirmation of the change."
                        }
                    },
                    "User Provides Incorrect Details": {
                        "Support Requests Resubmission": "Support asks user to resend correct details.",
                        "Support Offers Assistance": "Support offers help filling out information."
                    }
                }
            },
            "Payment Method Change": {
                "User Wants To Switch To Bank Transfer": {
                    "Support Sends Bank Details": "Support sends bank account details for transfer.",
                    "Support Explains Steps": "Support explains how to complete bank payment."
                },
                "User Wants To Switch To Card": {
                    "Support Explains Card Payment Process": "Support describes how to pay by credit/debit card.",
                    "Support Asks For Card Type": "Support asks for Visa, MasterCard, or other card type."
                }
            }
        },

        "Receipts and Invoices": {
            "Receipt Request": {
                "User Requests Copy": {
                    "Support Asks For Transaction ID": {
                        "User Provides ID": {
                            "Support Verifies And Sends PDF": "Support verifies ID and sends receipt as PDF.",
                            "Support Asks If Further Help Needed": "Support checks if the user needs anything else."
                        },
                        "User Provides Wrong ID": {
                            "Support Asks To Resend": "Support asks the user to resend correct ID.",
                            "Support Offers Contact Option": "Support offers alternative ways to get help."
                        }
                    }
                },
                "User Requests Alternative Format": {
                    "Support Provides Format Options": "Support lists available formats (PDF, Excel, etc.).",
                    "Support Sends Requested Format": "Support sends receipt in requested format."
                }
            },
            "Invoice Correction": {
                "User Reports Wrong Info": {
                    "Support Asks What Is Incorrect": {
                        "User Reports Name Error": {
                            "Support Updates Invoice": "Support updates invoice with correct name.",
                            "Support Sends Updated Copy": "Support sends the corrected invoice."
                        },
                        "User Reports Amount Error": {
                            "Support Investigates": "Support checks records to verify amount.",
                            "Support Provides Clarification": "Support explains amount discrepancy."
                        }
                    }
                },
                "User Asks For New Invoice": {
                    "Support Asks Reason For Request": "Support asks why a new invoice is needed.",
                    "Support Confirms New Details": "Support confirms details for generating new invoice."
                }
            }
        },

        "Other Queries?": "Connect With the Support Team"
    }

}




// botTree for SciPR
// const botTree = {
//     "Submission or Revision Process": {
//         "Stuck during revision (e.g., Incomplete Status, Portal Crash, Can't Edit)": "Follow the standard resubmission steps: (1) Click 'Approve Submission' (2) Edit details & click 'Next' (3) Upload revised files",
//         "Manuscript submission locked or prematurely submitted": "Support team reverts manuscript to editable draft.",
//         "Abstract word count error blocking submission": "The word count issue has been fixed by the support team.",
//         "Co-author field warning persists after adding authors": "Ignore message and submit, fix is being developed.",
//         "Need to cancel/undo submission for fresh submission": "Support enables 'resubmission option' for existing manuscript."
//     },
//     "Manuscript Information":{
//         "Co-author's name wrongly registered post-submission":{
//             "Need to cancel/undo submission for fresh submission" :"Support enables 'resubmission option' for existing manuscript."
//         },
//         "Need to change the Corresponding Author": " The support team performs this update in the backend.",
//         "Trouble saving the Co-Author list": "The system auto-saves. No 'Save' button is needed. Close the window after adding."
//     },
//     "System Access or Reviewer Issues":{
//         "Peer Reviewer's invitation link is not working": "The support team resolves the technical access issue for the reviewer.",
//         " Manuscript doesn't appear on reviewer dashboard after self-assignment" : " Immediate: Backend rectified; Long-term: Replicating for permanent fix."
//     },
//     "Post Submission Process":{
//         "Automated system sends receipt confirmation to author": {
//             "Editor's Review": {
//                 "Manuscript passes initial in-house screening": "Manuscript sent to two independent peer reviewers"
//             }
//         },
//         "Submitting agent emails 'Author Form Package' to editor": {
//             "Editor's Review": {
//                 "Manuscript passes initial in-house screening": "Manuscript sent to two independent peer reviewers"
//             }
//         }
//     }

// };

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
    botLabel.textContent = "Eva";

    const greetingContent = document.createElement("div");
    greetingContent.textContent = "Hi, I'm Eva. How can I help you today?";

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






