PhishTrace local training demo
==============================

Requirements:
- Python 3.10 or newer
- Flask

Setup in Windows PowerShell:
1. Extract this ZIP to a folder, for example C:\Users\maste\PhishTrace.
2. Open PowerShell in that folder.
3. Install Flask:
   python -m pip install flask
4. Set local environment variables (use your own secret values):
   $env:FLASK_SECRET_KEY = "replace-with-a-long-random-secret"
   $env:ADMIN_PASSWORD = "choose-a-strong-local-admin-password"
5. Start the app:
   python app.py
6. Open:
   http://127.0.0.1:5000
   Admin: http://127.0.0.1:5000/admin/login

Database:
- phishtrace.db is created beside app.py on first run.
- The app automatically adds the username column if an older lab_events table lacks it.
- Back up any existing database before replacing files or changing the schema.

Safety:
- This is intended for an authorized, local training simulation.
- The demo records email and username only. It does not collect or store passwords.
- Keep it bound to 127.0.0.1; do not expose it publicly without a proper security review.
