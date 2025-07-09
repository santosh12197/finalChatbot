# 💬 Django Chatbot with Real-Time Support

A modern chatbot system built with **Django 5.0**, **PostgreSQL**, and **WebSockets**, featuring a WhatsApp-style interface, hierarchical chatbot buttons, and real-time support team chat.

---

## 🚀 Features

### 🔐 User Side Chat
- Each time user clicks on chat bot icon, then it will ask for details like name, email, DOI / Article No, and start a new chat thread and closing the previous chat thread, if any.
- After above form submission, user is directed to chat bot tree (where user can interact with the bot)
- At the end of each branch in bot tree, user will be asked to connect with the support member for live chatting.
- once connected with support agent, thay can interact and chat in real time.
- User can also "Close" the chat.
  
### 🔐 Support Side Chat
- Support agent first needs to login for real time chat with the user. 
- At a time only one support member can chat. Here, support agent must "Connect" with the user in order to start the chat.
- Chat history of a user will be available when any support member clicks any user to chat. 
- One support member can assign other support member for chat.
- After issue is resolved, support agent can "Close" the chat.

### 🤖 Chatbot Interface
- Button-based, hierarchical query handling (focused on payment-related queries)
- Satisfaction check after resolution
- Option to escalate to live support

### 👥 Real-Time Support Chat
- Escalated chats handled by human support agents
- WebSocket-powered real-time messaging
- Support agents can handle multiple users

### 🗃️ Data Storage
- All conversations stored in PostgreSQL
- Stored user-wise
- Includes both bot responses and human support replies

### 🌐 WebSocket Integration
- Real-time bidirectional communication using Django Channels
- Instant message delivery between user and support team

### 🧱 Tech Stack
- Python 3.11
- Django 5.0
- PostgreSQL 17.4
- WebSockets
- HTML/CSS + JavaScript for frontend
- Bootstrap for styling


### Most Important
 inside settings.py file, do the following before production deployment:
 - Make "DEBUG = False" 
 - ALLOWED_HOSTS = [] (add hosts here)

### urls
 - /index: chatbot embedded on SciPris login page (user side)
 - /support_dashboard: support page (support side)

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/santosh12197/finalChatbot.git
cd django-chatbot-support

# Create virtual environment
python3.11 -m venv ienv
source ienv/bin/activate  # On Windows: venv\Scripts\activate

# Activate env
ienv\scripts\activate

# Install dependencies
pip install -r final_requirements.txt

# Create PostgreSQL DB & configure settings.py
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (for admin panel)
python manage.py createsuperuser

# Run development server
# python manage.py runserver
uvicorn chatbot_project.asgi:application --reload

