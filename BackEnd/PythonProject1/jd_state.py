# jd_state.py

user_session = {
    "mode": None,
    "email_data": {"to": None, "subject": None, "message": None},  # renamed for clarity
    "book": {
        "name": None,
        "text": "",
        "position": 0,
        "chapter_titles": [],
        "chapter_indices": [],
        "resume": False
    },
    "logged_in": False,
    "username": None,
    "email": None,           # logged-in user's email (sender)
    "app_password": None     # logged-in user's app password (for SMTP)
}


