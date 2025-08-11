# Event Scheduler API (Django + Django REST Framework)

This is a simple backend application for scheduling events and managing reservations.  
It is built using Django and Django REST Framework (DRF).  
The application supports user signup, login, event creation, reservation, and cancellation, with concurrency-safe booking to prevent overbooking.

---

## Project Features

- User signup and login with token authentication.
- Event creation, listing, updating, and deletion.
- Event categories: Workshop, Sports, Literature, Arts.
- Reservation system with seat capacity limits.
- Prevents overbooking using database transactions.
- Event creator can view reservations for their events.
- Django admin panel for managing data.

---

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment support (`venv`)
- SQLite (default for local development) or PostgreSQL for production

---

## Setup Instructions

### 1. Project Structure

Place the files in the following structure:

scheduler_project/
├─ scheduler_project/
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ events/
│  ├─ models.py
│  ├─ serializers.py
│  ├─ views.py
│  ├─ permissions.py
│  ├─ urls.py
│  ├─ tests.py
│  └─ management/commands/create_sample_events.py
├─ manage.py
├─ requirements.txt
└─ Dockerfile

### 2. Create and activate a virtual environment

Windows (PowerShell):
python -m venv .venv
..venv\Scripts\Activate.ps1

### 3. Install dependencies

pip install -r requirements.txt

shell
Copy
Edit

### 4. Apply migrations

python manage.py makemigrations
python manage.py migrate

pgsql
Copy
Edit

### 5. Create a superuser (optional, for admin access)

python manage.py createsuperuser

less
Copy
Edit

Enter the username, email, and password when prompted.

### 6. Load sample data (optional)

This will create:
- A user: `sample_creator` with password `password123`
- Four sample events: Workshop, Sports, Literature, Arts

python manage.py create_sample_events

yaml
Copy
Edit

---

## Running the Server

python manage.py runserver

sql
Copy
Edit

The server will start at:
http://127.0.0.1:8000/

yaml
Copy
Edit

---

## Authentication

This project uses Token Authentication.

### 1. Signup

Send a POST request to `/api/signup/` with:
{
"username": "alice",
"password": "pass123",
"email": "alice@example.com"
}

css
Copy
Edit

You will receive a token in the response.

### 2. Login

Send a POST request to `/api/login/` with `username` and `password`.  
You will get a token for that user.

### 3. Authenticated requests

Include the token in the request header:
Authorization: Token your_token_here

yaml
Copy
Edit

---

## API Endpoints

| Method | Endpoint                          | Description |
|--------|-----------------------------------|-------------|
| POST   | `/api/signup/`                    | Create a new user account |
| POST   | `/api/login/`                     | Get token for an existing user |
| GET    | `/api/events/`                    | List all events |
| POST   | `/api/events/`                    | Create new event (authentication required) |
| GET    | `/api/events/{id}/`               | Retrieve event details |
| PUT    | `/api/events/{id}/`               | Update event (creator only) |
| DELETE | `/api/events/{id}/`               | Delete event (creator only) |
| POST   | `/api/events/{id}/reserve/`       | Reserve a seat (authentication required) |
| GET    | `/api/events/{id}/reservations/`  | View reservations (creator only) |
| GET    | `/api/reservations/`              | View your reservations |
| DELETE | `/api/reservations/{id}/`         | Cancel your reservation |

---

## Running Tests

To run all tests:

python manage.py test

pgsql
Copy
Edit

Tests include concurrency checks to ensure overbooking is prevented.
