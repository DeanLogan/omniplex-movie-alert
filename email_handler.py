import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from browser_handler import get_movie_info

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
EMAIL_FORMAT = 'html'
EMAIL_SUBJECT_PREFIX = '🎬 Movie Updates: '
EMAIL_SUBJECT_SUFFIX = ' 🎬'
DATE_FORMAT = '%d %b %Y'
ENV_EMAIL = 'EMAIL_GMAIL'
ENV_PASSWORD = 'APP_PASSWORD_GMAIL'

location_cache = {}

def send_email(recipients, subject, body):
    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    sender = os.environ.get(ENV_EMAIL)
    password = os.environ.get(ENV_PASSWORD)
    smtp.login(sender, password)
    for recipient in recipients:
        message = MIMEText(body, EMAIL_FORMAT)
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipient
        smtp.sendmail(sender, recipient, message.as_string())
    smtp.quit()

def format_email_body(driver, location, movies):
    body = "<div>\n"
    body += "<h2>New movies at " + location + "</h2>\n"
    for movie in movies:
        movie_info = get_movie_info(driver, location, movie)
        if movie_info is not None:
            body += "<div>\n"
            body += "<h3><a href=" + movie_info["link"] + ">" + movie_info["title"] + "</a></h3>\n"
            body += "<table style='width: 100%; margin-bottom: 20px;'>\n"
            body += "<tr>\n"
            body += "<td style='vertical-align: top; width:160px;'>\n"
            body += '<img src="' + movie_info["img"] + '" alt="' + movie_info["title"] + '" style="width: 150px; height: 225px;">\n'
            body += "</td>\n"
            body += "<td style='vertical-align: top; padding-left: 0;'>\n"
            body += '<ul style="margin: 0; padding: 0; list-style-type: none;">\n'
            for date in movie_info["dates"]:
                body += "<li>" + date + "</li>\n"
            body += "</ul>\n"
            body += "</td>\n"
            body += "</tr>\n"
            body += "</table>\n"
            body += "</div>\n"
        else:
            body += "<div>\n"
            body += "<h3>Unable to access info for " + movie + "</h3>\n"
            body += "</div>\n"
    body += "</div>\n"
    return body

def build_email_body_for_user(user_locations):
    body = ""
    for location in user_locations:
        if location in location_cache and location_cache[location] != "":
            body += location_cache[location]
    return body

def send_user_email(user_email, user_locations):
    body = build_email_body_for_user(user_locations)
    if body:
        print("sending email to: ", user_email)
        subject = EMAIL_SUBJECT_PREFIX + datetime.now().strftime(DATE_FORMAT) + EMAIL_SUBJECT_SUFFIX
        send_email([user_email], subject, body)
    else:
        print("no email to send to: " + user_email)

def send_all_user_emails(email_list):
    for item in email_list:
        send_user_email(item['email'], item['locations'])
