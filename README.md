CSS Success Path – Backend

A Django REST Framework backend for a CSS English Precis & Composition exam preparation platform.

CSS Success Path is an educational platform designed to help CSS aspirants prepare for the English Precis & Composition examination through structured learning resources, practice assessments, mock tests, and AI-powered assistance.

This repository contains the backend application, which handles authentication, database operations, assessment management, API services, and AI integrations.

 Key Features

- User Authentication: User registration, login, and authentication.
- Password Recovery: OTP-based password reset functionality.
- MCQ Assessments: Generate, attempt, and evaluate multiple-choice questions.
- Subjective Assessments: Support for subjective questions and essay-based practice.
- Mock Tests: Practice exams with timed assessments.
- Learning Resources: Support for syllabus, past papers, and lecture-related content.
- AI Chatbot: AI-powered assistance for students.
- Results & Feedback: Assessment results and performance feedback.
- Admin Management: Manage users, questions, and learning content.
- Background Tasks: Celery and Redis integration for background processing and session cleanup.

 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Backend framework |
| Django REST Framework | REST API development |
| SQLite | Database |
| React | Frontend integration |
| Axios | API communication |
| Celery | Background task processing |
| Redis | Task queue and caching |
| OpenRouter | AI model integration |
| Git & GitHub | Version control |

 System Architecture

The application follows a client-server architecture.

- Frontend: React-based user interface.
- Backend: Django and Django REST Framework.
- Database: SQLite for storing application data.
- API Communication: REST APIs connecting the frontend and backend.
- AI Integration: OpenRouter API for AI-powered features.
- Background Processing: Celery and Redis.

 API Functionalities

The backend provides API endpoints for the following operations:

- User registration and authentication.
- JWT token generation.
- OTP-based password recovery.
- MCQ generation and evaluation.
- Subjective question and essay assessments.
- User and question management.
- AI-powered chatbot functionality.

 Installation & Setup

 1. Clone the Repository

```bash
git clone https://github.com/Musaddiq174/FYP-Backend.git
cd FYP-Backend
```

 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

Windows:
```bash
venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

 3. Install Dependencies

```bash
pip install -r requirements.txt
```

 4. Configure Environment Variables

Configure the required environment variables for external services, including AI integration and email/OTP functionality.

Keep API keys and credentials private. Never commit your `.env` file to GitHub.

 5. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

 6. Run the Development Server

```bash
python manage.py runserver
```

The backend will be available at:

```text
http://127.0.0.1:8000/
```

 Project Purpose

This project was developed as a Final Year Project (FYP) to provide CSS aspirants with a dedicated digital platform for preparing for the English Precis & Composition examination.

The main objective was to combine structured educational resources, interactive assessments, and AI-powered assistance into one learning environment.

 Contributors

Developed as a two-member Final Year Project.

Backend & Frontend Integration: Musaddiq Hussain

GitHub: [@Musaddiq174](https://github.com/Musaddiq174)

 Repository

[CSS Success Path – FYP Backend](https://github.com/Musaddiq174/FYP-Backend)

---

Developed as a Final Year Project at the University of Central Punjab.
