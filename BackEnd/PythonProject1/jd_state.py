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
    "email": None,
    "app_password": None
}


