let activeRoomName = null;
let supportChatSocket = null;

// Fetch active chats/users from backend API (you need to implement this API yourself)
fetch('/api/active_chats/')
    .then(response => response.json())
    .then(data => {
        const userList = document.getElementById('user-list');
        data.forEach(chat => {
            const userBtn = document.createElement('button');
            userBtn.className = 'user-button btn btn-light';
            userBtn.textContent = chat.username;
            userBtn.onclick = () => openChat(chat.room_name);
            userList.appendChild(userBtn);
        });
    });

function openChat(roomName) {
    if (supportChatSocket) {
        supportChatSocket.close();
    }

    activeRoomName = roomName;
    supportChatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/support/' + roomName + '/'
    );
    console.log("supportChatSocket: ", supportChatSocket)
    supportChatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.message) {
            const messages = document.getElementById('messages');
            const msgDiv = document.createElement('div');
            msgDiv.textContent = data.message;
            messages.appendChild(msgDiv);
        }
    };

    document.getElementById('support-send-button').onclick = () => {
        const input = document.getElementById('support-message-input');
        if (input.value.trim() !== '') {
            supportChatSocket.send(JSON.stringify({
                'message': input.value
            }));
            input.value = '';
        }
    };
}
