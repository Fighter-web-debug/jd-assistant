import os
import re
import requests
import datetime
import pyjokes
import wikipedia
from langdetect import detect
from deep_translator import GoogleTranslator
from email.message import EmailMessage
import smtplib
from jd_state import user_session
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

EMAIL = "astitvat3@gmail.com"
PASSWORD = os.getenv("JD_GMAIL_APP_PASSWORD")

def sanitize_email(input_text):
    email = input_text.lower().replace(" at ", "@").replace(" dot ", ".")
    return re.sub(r'\s+', '', email)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def send_email(receiver, subject, message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    email = EmailMessage()
    email['From'] = EMAIL
    email['To'] = receiver
    email['Subject'] = subject
    email.set_content(message)
    server.send_message(email)
    server.quit()

def search_gutenberg(book_name):
    url = f"https://gutendex.com/books/?search={book_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if data['count'] == 0:
        return None
    book = data['results'][0]
    for fmt, link in book['formats'].items():
        if 'text/plain' in fmt:
            return link
    return None

def get_ai_response(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are JD, a helpful and funny AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {e}"

def handle_command(command):
    command = command.strip().lower()
    command = translate_to_english(command)

    # ----------------- Stop Book Reading -------------------
    if command == "stop" and user_session["mode"] == "book":
        user_session["mode"] = None
        return "Stopped reading the book."

    # ----------------- Email Mode -------------------
    if user_session["mode"] == "email":
        if not user_session["email"]["to"]:
            user_session["email"]["to"] = sanitize_email(command)
            if not is_valid_email(user_session["email"]["to"]):
                user_session["email"]["to"] = None
                return "Invalid email address. Please say it again."
            return "Got it. What's the subject?"

        elif not user_session["email"]["subject"]:
            user_session["email"]["subject"] = command
            return "And what should the email say?"

        elif not user_session["email"]["message"]:
            user_session["email"]["message"] = command
            try:
                send_email(
                    user_session["email"]["to"],
                    user_session["email"]["subject"],
                    user_session["email"]["message"]
                )
                user_session["mode"] = None
                user_session["email"] = {"to": None, "subject": None, "message": None}
                return "Email has been sent successfully."
            except Exception as e:
                user_session["mode"] = None
                return f"Failed to send the email. Error: {e}"

    # ----------------- Book Reading Mode -------------------
    if user_session["mode"] == "book":
        if not user_session["book"]["name"]:
            book_name = command
            book_link = search_gutenberg(book_name)
            if not book_link:
                user_session["mode"] = None
                return f"Sorry, I couldn't find '{book_name}' on Project Gutenberg."

            response = requests.get(book_link)
            response.encoding = 'utf-8'
            book_text = response.text

            # Try to start from Chapter 1
            start_idx = book_text.find("CHAPTER 1")
            if start_idx == -1:
                start_idx = book_text.lower().find("chapter i")
            if start_idx == -1:
                start_idx = 0

            book_text = book_text[start_idx:]

            # Store book session
            user_session["book"].update({
                "name": book_name,
                "text": book_text,
                "position": 0
            })
            return f"Book '{book_name}' loaded. Should I start from Chapter 1 or resume from last position?"

        if command in ["resume", "yes"]:
            pos = user_session["book"]["position"]
        elif command in ["start over", "restart", "chapter 1", "no"]:
            pos = 0
            user_session["book"]["position"] = 0
        else:
            pos = user_session["book"]["position"]

        # Read next chunk (approx 500–1000 chars)
        next_pos = user_session["book"]["text"].find("\n\n", pos + 1000)
        if next_pos == -1:
            next_pos = len(user_session["book"]["text"])

        reading_chunk = user_session["book"]["text"][pos:next_pos]
        user_session["book"]["position"] = next_pos
        return f"Reading from {user_session['book']['name']}:\n{reading_chunk.strip()}"

    # ----------------- Command Triggers -------------------
    if "email" in command or "i want to send email" in command:
        user_session["mode"] = "email"
        return "Sure. Who is the recipient?"

    if "read" in command or "i want to read" in command:
        user_session["mode"] = "book"
        user_session["book"] = {"name": None, "text": "", "position": 0}
        return "Which book would you like to read?"

    if "play" in command:
        song = command.replace("play", "").strip()
        return f"Playing {song} on YouTube."

    if "joke" in command:
        return pyjokes.get_joke()

    if "time" in command:
        return datetime.datetime.now().strftime("The time is %I:%M %p")

    if "tell me about" in command:
        person = command.replace("tell me about", "").strip()
        try:
            return wikipedia.summary(person, 1)
        except:
            return "Couldn't find clear information. Please be more specific."

    # ----------------- Fallback AI -------------------
    return get_ai_response(command)





