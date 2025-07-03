# 💬 Django Chatbot with Real-Time Support

A modern chatbot system built with **Django 5.0**, **PostgreSQL**, and **WebSockets**, featuring a WhatsApp-style interface, hierarchical chatbot buttons, and real-time support team chat.

---

## 🚀 Features

### 🔐 User Authentication
- User Registration
- Login / Logout
- Session management with secure auth

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

### 💬 WhatsApp-style UI
- Modern chat interface styled to resemble WhatsApp
- Distinct views for users and support agents
- Responsive and user-friendly layout

### 🛠️ Admin/Support Dashboard
- Support team panel to monitor & respond to user chats
- Real-time updates of new incoming requests
- Search/sort/filter conversations

### 🌐 WebSocket Integration
- Real-time bidirectional communication using Django Channels or similar
- Instant message delivery between user and support team

### 🧱 Tech Stack
- Python 3.11
- Django 5.0 (Class-based views)
- PostgreSQL 17
- WebSockets
- HTML/CSS + JavaScript for frontend
- Bootstrap for styling

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/santosh12197/finalChatbot.git
cd django-chatbot-support

# Create virtual environment
python3.11 -m venv ienv
source ienv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL DB & configure settings.py
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (for admin panel)
python manage.py createsuperuser

# Run development server
python manage.py runserver

## Project structure
chatbot_project/
├── chatbot_app/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── consumers.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
├── chatbot_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── chatbot.html
│   └── support_team.html
└── manage.py
