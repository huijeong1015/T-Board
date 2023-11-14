import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import os

PWD_LEN = 10
TBOARD_URL = "https://t-board.onrender.com/"
TBOARD_EMAIL = "ece444tboard@gmail.com"
TBOARD_PWD = "vjau nxth hark wjgo"


# Helper functions
# Generate a temporary password
def generate_temporary_pwd():
    pwd_length = 10
    return secrets.token_urlsafe(pwd_length)


def email_temporary_pwd(receiver, pwd):
    sender = TBOARD_EMAIL

    message = MIMEMultipart("alternative")
    message["Subject"] = "Temporary Password for T-Board Account"
    message["To"] = receiver
    message["From"] = sender

    text = f"Your temporary password for T-board is:\n{pwd}"
    html = f"""\
<html>
<body style="background-color:#202e44;display:flex;flex-direction:column;justify-items:center;align-items:center;gap:30px;padding:30px;">
<svg style="width:300px" viewBox="0 0 392 151" xmlns="http://www.w3.org/2000/svg">
<path d="m0.51221 32.166c0-4 2-6 6-6h47.4c4 0 6 2 6 6v1.65c0 4-2 6-6 6h-10.8c-4 0-6 2-6 6v82.05c0 4-2 6-6 6h-1.65c-4 0-6-2-6-6v-82.05c0-4-2-6-6-6h-10.95c-4 0-6-2-6-6v-1.65z" fill="white"/>
<path d="m102.66 83.317c0 4-2 6-6.0003 6h-27.75c-4 0-6-2-6-6v-2.25c0-4 2-6 6-6h27.75c4.0003 0 6.0003 2 6.0003 6v2.25zm57.779-15.45c2 2 3 4.45 3 7.35v43.2c0 2.9-1 5.35-3 7.35l-4.95 4.95c-2 2-4.45 3-7.35 3h-27.45c-4 0-6-2-6-6v-95.7c0-4 2-6 6-6h1.65c4 0 6 2 6 6v21.9c0 4 2 6 6 6h13.8c2.9 0 5.35 1 7.35 3l4.95 4.95zm-26.1 5.7c-4 0-6 2-6 6v34.5c0 4 2 6 6 6h9.45c4 0 6-2 6-6v-34.5c0-4-2-6-6-6h-9.45zm90.121-5.85c2 2.1 3 4.6 3 7.5v43.5c0 2.9-1 5.4-3 7.5l-4.8 4.8c-2 2-4.45 3-7.35 3h-18.6c-2.9 0-5.35-1-7.35-3l-4.95-4.95c-2-2-3-4.45-3-7.35v-43.5c0-2.9 1-5.35 3-7.35l4.95-4.95c2-2 4.45-3 7.35-3h18.6c2.9 0 5.35 1 7.35 3l4.8 4.8zm-10.65 11.85c0-4-2-6-6-6h-9.75c-4 0-6 2-6 6v34.8c0 4 2 6 6 6h9.75c4 0 6-2 6-6v-34.8zm43.913 54.3c-2.9 0-5.35-1-7.35-3l-4.95-4.95c-2-2-3-4.45-3-7.35v-17.4c0-1.5004 0.25-2.8004 0.75-3.9004 0.5-1.2 1.3-2.35 2.4-3.45l4.8-4.8c2-2 4.45-3 7.35-3h14.25c4 0 6-2 6-6v-0.45c0-4-2-6-6-6h-23.1c-4 0-6-2-6-6v-1.65c0-4 2-6 6-6h27.45c2.9 0 5.35 1 7.35 3l4.95 4.95c2 2 3 4.45 3 7.35v52.65c0 4-2 6-6 6h-27.9zm20.25-29.55c0-4-2-6.0004-6-6.0004h-9.9c-4 0-6 2.0004-6 6.0004v11.25c0 4 2 6 6 6h9.9c4 0 6-2 6-6v-11.25zm45.372 23.55c0 4-2 6-6 6h-1.65c-4 0-6-2-6-6v-52.65c0-2.9 1-5.35 3-7.35l4.95-4.95c2-2 4.45-3 7.35-3h2.7c4 0 6 2 6 6v1.65c0 4-1.7 6-5.1 6-1.7 0-3 0.55-3.9 1.65-0.9 1-1.35 2.45-1.35 4.35v48.3zm27.22-64.95c2-2 4.5-3 7.5-3h13.8c4 0 6-2 6-6v-21.6c0-4 2-6 6-6h1.65c4 0 6 2 6 6v95.7c0 4-2 6-6 6h-27.45c-2.9 0-5.35-1-7.35-3l-4.95-4.95c-2-2-3-4.45-3-7.35v-43.65c0-2.9 1-5.35 3-7.35l4.8-4.8zm5.85 51.45c0 4 2 6 6 6h9.45c4 0 6-2 6-6v-34.8c0-4-2-6-6-6h-9.45c-4 0-6 2-6 6v34.8z" fill="#A2B7CA"/>
</svg>
<div style="background-color:#ebebeb;display:flex;flex-direction:column;justify-items:center;align-items:center;height:fit-content;width:fit-content;padding:30px;border: 10px solid #786554;border-radius: 15px;">
<p style="font-family:Aptos;font-size:150%">Your temporary password for
<a href="http://localhost:5000/">T-Board</a> is:</p>
<p style="font-family:Aptos;font-size:200%;font-weight:bold">{pwd}</p>
</div>
</body>
</html>"""
    text = MIMEText(text, "plain")
    html = MIMEText(html, "html")
    message.attach(text)
    message.attach(html)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(sender, TBOARD_PWD)
    server.sendmail(sender, receiver, message.as_string())
    server.quit()
