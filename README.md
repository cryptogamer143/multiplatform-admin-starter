# Multi-Platform Social Media Admin - Starter

**What this is**
- Minimal starter admin panel to manage Instagram, Facebook, Twitter, and YouTube in one place.
- Contains a Flask backend (with placeholder OAuth endpoints) and a very simple frontend (single HTML file).
- Uses SQLite for ease of local testing. Replace with PostgreSQL in production.
- Uses APScheduler for simple background scheduling (no Celery required for a starter).

**What you MUST configure**
- Add your OAuth client IDs / secrets for each platform in `backend/.env` or environment variables.
- Implement the actual OAuth token exchange and platform-specific API calls where commented in the code.

**Quick start (local)**
1. Install Python 3.11+ and Node (optional, frontend is pure HTML/JS).
2. Create a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. From project root, run:
   ```bash
   export FLASK_APP=backend/app.py
   export FLASK_ENV=development
   flask run --port 5000
   ```
4. Open `frontend/admin.html` in your browser (or serve it via a simple static server).

**Files**
- backend/app.py            -> Flask backend with API endpoints and scheduling
- backend/requirements.txt -> Python dependencies
- frontend/admin.html      -> Simple admin UI to create/schedule posts and connect accounts
- docker-compose.yml       -> (optional) basic compose file to run the app in containers
- README.md                -> this file

**Next steps (recommended)**
- Replace placeholder OAuth flows with real OAuth for each platform (use references in your architecture doc).
- Implement media handling & storage (S3 or similar).
- Replace SQLite with PostgreSQL and add migrations (Alembic).
- Consider using Celery + Redis for robust background jobs in production.

If you'd like, I can:
- add real OAuth code for specific platforms (I will need your client IDs/secrets),
- or expand the frontend into a React app and connect it to the backend.

