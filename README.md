# crobwebsite

Django site with accounts, per-user file storage, a to-do list, and a server
status page.

## Apps

- **main**: home page, register, login/logout, profile
- **fileManagement**: per-user file uploads/downloads
- **todo**: per-user to-do list with due dates and reminders
- **serverInfo**: server/system diagnostics page (staff only)

## Setup

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd crobwebsite
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/.

## Config

`SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` are read from the environment (defaults
are fine for local dev, see `.env.example`). Copy `.env.example` to `.env` in the
repo root to set them locally; it's picked up automatically and gitignored.

`db.sqlite3` and `media/` are gitignored too, since they're local data not code.

Server Info (`/server/`) is staff-only since it shows the hostname, DB path, IPs
etc. Make a user staff via `createsuperuser` or the `is_staff` flag in `/admin/`.
