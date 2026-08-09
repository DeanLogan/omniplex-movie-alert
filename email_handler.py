import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
EMAIL_FORMAT = 'html'
EMAIL_SUBJECT_PREFIX = '🎬 Movie Updates: '
EMAIL_SUBJECT_SUFFIX = ' 🎬'
DATE_FORMAT = '%d %b %Y'
ENV_EMAIL = 'SENDER_EMAIL'
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

def _chunk_list(items, size):
    """Split a list into sublists of at most `size` items each."""
    return [items[i:i + size] for i in range(0, len(items), size)]

def _format_showtime_cell(showtime):
    return (
        f'<td style="padding: 4px;">'
        f'<a href="{showtime["link"]}" '
        f'style="display: block; text-decoration: none; '
        f'background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 6px; '
        f'padding: 6px 10px; text-align: center; color: #1a1a1a;">'
        f'<span style="font-weight: bold; font-size: 14px;">{showtime["start_time"]} - {showtime["end_time"]}</span>'
        f'<br><span style="font-size: 11px; color: #666;">{showtime["screen"]}</span>'
        f'</a></td>\n'
    )

def _format_date_block(date, showtimes, columns=3):
    block = f'<p style="font-weight: bold; margin: 12px 0 6px 0;">{date}</p>\n'
    block += '<table style="border-collapse: collapse; width: 100%;">\n'
    for row in _chunk_list(showtimes, columns):
        block += '<tr>\n'
        for showtime in row:
            block += _format_showtime_cell(showtime)
        # pad the row with empty cells so short last rows don't stretch to fill the width
        for _ in range(columns - len(row)):
            block += '<td></td>\n'
        block += '</tr>\n'
    block += '</table>\n'
    return block

def _email_head_with_mobile_styles():
    return """
        <head>
        <style>
        @media only screen and (max-width: 480px) {
            .showtime-cell {
            width: 50% !important;
            }
            .poster-cell, .content-cell {
            display: block !important;
            width: 100% !important;
            padding: 0 !important;
            }
            .movie-poster {
            width: 100px !important;
            height: 150px !important;
            margin: 0 auto 12px auto !important;
            }
        }
        </style>
        </head>
    """

def format_email_body(location, movies, movies_info):
    body = (
        "<div style='font-family: Arial, Helvetica, sans-serif; max-width: 1800px; margin: 0;'>\n"
        f"<h2 style='color: #1a1a1a; border-bottom: 2px solid #f4c430; padding-bottom: 8px;'>"
        f"New movies at {location.title()}</h2>\n"
    )
    for movie in movies:
        if movie in movies_info:
            movie_info = movies_info[movie]
            body += "<table style='width: 100%; margin-bottom: 24px; border-collapse: collapse;'>\n"
            body += "<tr>\n"
            body += "<td class='poster-cell' style='vertical-align: top; width: 160px; padding-right: 16px;'>\n"
            body += (
                f'<img class="movie-poster" src="{movie_info["img"]}" alt="{movie_info["title"]}" '
                f'style="width: 150px; height: 225px; border-radius: 6px; '
                f'box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: block;">\n'
            )
            body += "</td>\n"
            body += "<td class='content-cell' style='vertical-align: top; padding-left: 0;'>\n"
            body += (
                f'<h3 style="margin: 0 0 8px 0;">'
                f'<a href="{movie_info["link"]}" style="color: #b8860b; text-decoration: none;">'
                f'{movie_info["title"]}</a></h3>\n'
            )
            for date, showtimes in sorted(movie_info["dates"].items()):
                body += _format_date_block(date, showtimes)
            body += "</td>\n"
            body += "</tr>\n"
            body += "</table>\n"
        else:
            body += (
                f"<div style='padding: 12px; background: #fff3cd; border-radius: 6px; margin-bottom: 16px;'>"
                f"<h3 style='margin: 0; color: #856404;'>Unable to access info for {movie}</h3></div>\n"
            )
    body += "</div>\n"
    return body

def _wrap_email_html(body):
    return f"""<html>
        {_email_head_with_mobile_styles()}
        <body>
        {body}
        </body>
    </html>"""

def build_email_body_for_user(user_locations):
    body = ""
    for location in user_locations:
        if location in location_cache and location_cache[location] != "":
            body += location_cache[location]
    return body

def send_user_email(user_email, user_locations):
    body = build_email_body_for_user(user_locations)
    if body:
        full_html = _wrap_email_html(body)
        print("sending email to: ", user_email)
        subject = EMAIL_SUBJECT_PREFIX + datetime.now().strftime(DATE_FORMAT) + EMAIL_SUBJECT_SUFFIX
        send_email([user_email], subject, full_html)
    else:
        print("no email to send to: " + user_email)

def send_all_user_emails(email_list):
    for item in email_list:
        send_user_email(item['email'], item['locations'])
