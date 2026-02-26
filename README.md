# Mini StackOverflow API

A RESTful API inspired by StackOverflow, built with **Django** and **Django REST Framework**. This API enables users to ask questions, post answers, vote on content, and manage their profiles with OAuth2 authentication.

## Features

- **User Authentication** — OAuth2-based authentication using `django-oauth-toolkit`
- **Questions** — Create, read, update, and delete questions with title, body, and tags
- **Answers** — Post answers to questions with upvote/downvote support
- **Voting System** — Upvote and downvote questions and answers
- **Pagination** — Custom pagination for efficient data loading
- **Signals** — Django signals for automated side-effects (e.g., reputation updates)
- **Admin Panel** — Full Django admin interface for content management
- **RESTful Design** — Clean, well-structured API endpoints following REST conventions

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 3.2.8 |
| API Framework | Django REST Framework 3.12.4 |
| Authentication | Django OAuth Toolkit 1.5.0 |
| Language | Python 3.x |
| Database | SQLite (default) / PostgreSQL (production) |

## Project Structure

```
mini-stackoverflow-api/
├── core/                       # Main application
│   ├── models.py              # Data models (User, Question, Answer, Vote)
│   ├── views.py               # API views and viewsets
│   ├── serializers.py         # DRF serializers for data validation
│   ├── urls.py                # URL routing for API endpoints
│   ├── pagination.py          # Custom pagination classes
│   ├── signal.py              # Django signals for side-effects
│   ├── admin.py               # Admin panel configuration
│   ├── test.py                # Unit tests
│   ├── tests.py               # Integration tests
│   └── apps.py                # App configuration
├── mini_stackoverflow/         # Django project settings
│   ├── settings.py            # Project configuration
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI entry point
├── manage.py                   # Django management script
└── requirements.txt            # Python dependencies
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register/` | Register a new user |
| `POST` | `/api/login/` | Authenticate and get token |
| `GET` | `/api/questions/` | List all questions (paginated) |
| `POST` | `/api/questions/` | Create a new question |
| `GET` | `/api/questions/:id/` | Get question details |
| `PUT` | `/api/questions/:id/` | Update a question |
| `DELETE` | `/api/questions/:id/` | Delete a question |
| `POST` | `/api/questions/:id/answers/` | Post an answer |
| `POST` | `/api/questions/:id/vote/` | Vote on a question |
| `POST` | `/api/answers/:id/vote/` | Vote on an answer |

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/abhaysinhchavda/mini-stackoverflow-api.git
cd mini-stackoverflow-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

## Authentication

This API uses **OAuth2** via `django-oauth-toolkit`. To access protected endpoints:

1. Register an application in the Django admin (`/admin/`)
2. Obtain an access token via the OAuth2 flow
3. Include the token in your request headers:
   ```
   Authorization: Bearer <your-access-token>
   ```

## License

MIT

## Author

**Abhaysinh Chavda**

If you have any questions or suggestions, feel free to open an issue or reach out.
