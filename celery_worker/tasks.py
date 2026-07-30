from email.message import EmailMessage
import smtplib
import os
from fastapi import HTTPException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from celery_worker.celery_app import celery_app

# Force the Celery worker process to load your updated .env file
load_dotenv()


def create_message(name: str, username: str, password: str):
    plain_text_body = (
        f"Hello {name},\n\n"
        f"Your account has been successfully created. Here are your login details:\n\n"
        f"Username: {username}\n"
        f"Password: {password}\n\n"
        f"Please make sure to change your password immediately after logging in."
    )

    return plain_text_body


# @celery_app.task(bind=True, max_retries=3)
def send_email(name: str, email: str, username: str, password: str):
    # Grab the API key from environment variables
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        print("Error: SENDGRID_API_KEY is not set in the environment.")
        return "Failed: Missing API Key"

    print(f"Preparing to send email to: {email}")

    # Build the payload for SendGrid using plain_text_content
    message = Mail(
        # Must match your verified sender exactly
        from_email="dextrosage.web@gmail.com",
        to_emails=email,
        subject="Welcome to our platform!",
        # Pass the plain text string here
        plain_text_content=create_message(name, username, password)
    )

    try:
        # Initialize the SendGrid client and fire off the request
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        # SendGrid returns a 202 status code when they successfully accept the email queue
        print(
            f"Successfully sent via SendGrid. Status Code: {response.status_code}")
        return "Email sent"

    except Exception as e:
        print(f"Failed to send email via SendGrid: {e}")
        raise HTTPException(status_code=500, detail=e)
        # If the API drops or there's a temporary network hiccup, retry in 60 seconds
        # raise self.retry(exc=e, countdown=60)


def create_message_for_smtp(
    name: str,
    from_email: str,
    to_email: str,
    username: str,
    password: str,
) -> EmailMessage:

    msg = EmailMessage()

    msg["Subject"] = "Welcome to DextroSage"
    msg["From"] = from_email
    msg["To"] = to_email

    msg.set_content(
        f"""
Hello {name},

Welcome to DextroSage!

Your account has been created successfully.

-----------------------------------
Username: {username}
Password: {password}
-----------------------------------

Please change your password after your first login.

Login:
https://dextro-sage-website.vercel.app/login

Regards,
The DextroSage Team
"""
    )

    msg.add_alternative(
        f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0;padding:40px;background:#f3f6fb;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellspacing="0" cellpadding="0">
<tr>
<td align="center">

<table width="600" cellspacing="0" cellpadding="0"
style="background:#ffffff;border-radius:12px;overflow:hidden;
box-shadow:0 6px 20px rgba(0,0,0,0.08);">

<!-- Header -->
<tr>
<td align="center"
style="background:#2563eb;padding:35px;">

<h1 style="color:white;margin:0;font-size:30px;">
DextroSage
</h1>

<p style="margin-top:10px;color:#dbeafe;font-size:16px;">
Welcome to the platform
</p>

</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:40px;">

<h2 style="margin-top:0;color:#222;">
Hello {name},
</h2>

<p style="font-size:16px;color:#444;line-height:1.7;">
Your account has been created successfully.
Below are your login credentials.
</p>

<table width="100%"
style="border:1px solid #e5e7eb;
border-radius:8px;
border-collapse:collapse;
margin:30px 0;">

<tr style="background:#f8fafc;">
<td style="padding:15px;font-weight:bold;width:35%;">
Username
</td>

<td style="padding:15px;">
{username}
</td>
</tr>

<tr>
<td style="padding:15px;font-weight:bold;">
Password
</td>

<td style="padding:15px;">
{password}
</td>
</tr>

</table>

<div
style="
background:#fff8e6;
border-left:5px solid #f59e0b;
padding:18px;
margin-bottom:30px;
">

<strong>Security Notice</strong>

<p style="margin:10px 0 0 0;color:#555;">
For your security, please change your password immediately after logging in.
Never share your password with anyone.
</p>

</div>

<table cellspacing="0" cellpadding="0" align="center">
<tr>
<td align="center"
style="
background:#2563eb;
border-radius:8px;
">

<a href="https://dextro-sage-website.vercel.app/login"
style="
display:inline-block;
padding:15px 35px;
color:white;
font-weight:bold;
font-size:16px;
text-decoration:none;
">
Login to DextroSage
</a>

</td>
</tr>
</table>

<p style="margin-top:30px;font-size:14px;color:#666;">
If the button doesn't work, copy and paste this link into your browser:
</p>

<p style="word-break:break-all;">
<a
href="https://dextro-sage-website-amber.vercel.app/login"
style="color:#2563eb;">
https://dextro-sage-website-amber.vercel.app/login
</a>
</p>

<p
style="
margin-top:40px;
font-size:14px;
color:#777;
line-height:1.6;
">

If you did not request this account,
please contact the administrator immediately.

</p>

</td>
</tr>

<!-- Footer -->
<tr>
<td
align="center"
style="
padding:25px;
background:#f8fafc;
font-size:13px;
color:#888;
">

© 2026 DextroSage. All rights reserved.

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
""",
        subtype="html",
    )

    return msg

# Send email by smtp


def send_email_smtp(name: str, email: str, username: str, password: str):
    # Grab the API key from environment variables
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_email = os.getenv("SMTP_USER")
    smtp_pwd = os.getenv("SMTP_PASSWORD")
    
    # Build the payload for SendGrid using plain_text_content
    message = create_message_for_smtp(
        name,
        smtp_email,
        email,
        username,
        password,
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:

            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                smtp_email,
                smtp_pwd
            )

            smtp.send_message(message)

            # SendGrid returns a 202 status code when they successfully accept the email queue
            print(
                f"Successfully sent via SMTP.")
            return "Email sent"
    except smtplib.SMTPAuthenticationError as e:

        print(f"Authentication failed for {e}")
        # raise HTTPException(status_code=500,detail="Authentication failed")

    except smtplib.SMTPException as e:
        print(e)
        # raise HTTPException(status_code=500,detail=e)

    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        # raise HTTPException(status_code=500,detail=e)
