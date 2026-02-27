# 📧 Flask SMTP Email Sender (Render Deployment)

A simple Flask-based SMTP email sender that supports:

-   Raw email sending\
-   Dynamic variable replacement (`[KEY]`)\
-   Date tokens (`[D=>%Y-%m-%d]`)\
-   `To: [*to]` and `Cc: [*to]` replacement\
-   Batch sending with delay

------------------------------------------------------------------------

# 🚀 Deploy on Render

## 1️⃣ Clone the Repository

git clone https://github.com/yourusername/yourrepo.git\
cd yourrepo

------------------------------------------------------------------------

## 2️⃣ Create requirements.txt

Flask==3.0.2\
gunicorn==21.2.0

------------------------------------------------------------------------

## 3️⃣ Update Your app.py

Make sure the app runs like this:

import os

if **name** == "**main**":\
port = int(os.environ.get("PORT", 5000))\
app.run(host="0.0.0.0", port=port)

Do NOT use debug=True in production.

------------------------------------------------------------------------

## 4️⃣ Secure SMTP Credentials (IMPORTANT)

Do NOT hardcode credentials.

Use environment variables instead:

import os

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")\
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

------------------------------------------------------------------------

## 5️⃣ Deploy on Render

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

(Replace app:app if your file name is different.)

------------------------------------------------------------------------

## 6️⃣ Add Environment Variables in Render

In Render → Environment → Add:

-   SMTP_USERNAME\
-   SMTP_PASSWORD\
-   SMTP_SERVER (optional)\
-   SMTP_PORT (optional)

------------------------------------------------------------------------

# 📩 API Endpoint

POST /send-email

Example JSON:

{ "raw_email": "From: Sender <sender@example.com>`\nTo`{=tex}:
\[\*to\]`\nSubject`{=tex}: Test`\n`{=tex}`\nHello`{=tex}", "to_emails":
\["test1@example.com", "test2@example.com"\], "variables": { "NAME":
"John" }, "batch_size": 2, "delay_ms": 1000 }

------------------------------------------------------------------------

# 🧑‍💻 Local Development

pip install -r requirements.txt\
python app.py

App runs on: http://localhost:5000
