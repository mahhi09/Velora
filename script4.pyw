"""
Daily Log File Mailer (No GUI version)
----------------------------------------
- LOG_FOLDER is auto-detected (same folder where this script lives)
- Status is written to "uploaded_log.txt" instead of print()
- Instead of a single "last_sent.txt", we now use a date-named marker
  file like "28-06-2026_SentMail.log" to track if today's mail was sent
- If today's marker file exists -> mail already sent, skip
- If it doesn't exist -> send mail, then create the marker
- Old marker files (older than 2 days, based on filename date) are
  automatically deleted to save storage
- "Waiting for time" is logged only once per hour, with target + current time
"""

import smtplib
import time
import os
import re
import datetime
from email.message import EmailMessage

# ======================================================================
# FILL IN YOUR DETAILS HERE
# ======================================================================
SENDER_EMAIL = "your@gmail.com"        # your Gmail
SENDER_APP_PASSWORD = "ddoraucfevkhpkle"          # your App Password

CLIENT_EMAIL = "your@gmail.com"       # client's email

SEND_TIME = "15:40"                               # send after this time (24-hr HH:MM)
# ======================================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Use the folder where this script is located as LOG_FOLDER (auto-detected)
LOG_FOLDER = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(LOG_FOLDER, "uploaded_log.txt")

# Marker file suffix, e.g. "28-06-2026_SentMail.log"
SENT_MARKER_SUFFIX = "_SentMail.log"

# How often to log "Waiting for time" (in seconds)
WAITING_LOG_INTERVAL = 60 * 60  # 1 hour

# How old a marker file can get before it's deleted (in days)
MARKER_MAX_AGE_DAYS = 2


def write_status(text):
    with open(STATUS_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")


def todays_log_filename():
    return datetime.datetime.now().strftime("%d-%m-%Y") + ".log"


def sent_marker_path(date_str: str) -> str:
    """Returns the full path of today's (or any date's) sent-mail marker file."""
    return os.path.join(LOG_FOLDER, f"{date_str}{SENT_MARKER_SUFFIX}")


def is_mail_already_sent(date_str: str) -> bool:
    """Checks whether the marker file for the given date exists."""
    return os.path.exists(sent_marker_path(date_str))


def create_sent_marker(date_str: str):
    """Creates an empty marker file to record that mail was sent for this date."""
    with open(sent_marker_path(date_str), "w", encoding="utf-8") as f:
        f.write(f"Mail sent on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def cleanup_old_markers():
    """Deletes marker files older than MARKER_MAX_AGE_DAYS, based on the
    date encoded in their filename (not on file modified time)."""
    today = datetime.date.today()
    pattern = re.compile(r"^(\d{2}-\d{2}-\d{4})" + re.escape(SENT_MARKER_SUFFIX) + r"$")

    for filename in os.listdir(LOG_FOLDER):
        match = pattern.match(filename)
        if not match:
            continue

        date_str = match.group(1)
        try:
            file_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            continue  # filename doesn't match expected date format, skip it

        age_days = (today - file_date).days
        if age_days > MARKER_MAX_AGE_DAYS:
            try:
                os.remove(os.path.join(LOG_FOLDER, filename))
                write_status(f"Deleted old marker (age {age_days} days): {filename}")
            except Exception as e:
                write_status(f"Error deleting marker {filename}: {e}")


def send_log_email():
    filename = todays_log_filename()
    file_path = os.path.join(LOG_FOLDER, filename)

    if not os.path.exists(file_path):
        write_status(f"FILE NOT FOUND: {file_path}")
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Log File - {filename}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = CLIENT_EMAIL
    msg.set_content(f"Hello,\n\nToday's log file ({filename}) is attached.")

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=filename)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            smtp.send_message(msg)
        write_status(f"Mail sent to {CLIENT_EMAIL} -- '{filename}' was sent")
        return True
    except Exception as e:
        write_status(f"ERROR -- {e}")
        return False


if __name__ == "__main__":
    last_waiting_log_time = 0  # last time "Waiting for time" was logged
    last_cleanup_check = 0     # last time we ran the old-marker cleanup

    write_status(f"Script started. Log folder: {LOG_FOLDER} | Send time set to: {SEND_TIME}")

    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%d-%m-%Y")

        if current_time >= SEND_TIME and not is_mail_already_sent(today):
            sent = send_log_email()
            if sent:
                create_sent_marker(today)
        else:
            now_epoch = time.time()
            if now_epoch - last_waiting_log_time >= WAITING_LOG_INTERVAL:
                write_status(f"Waiting for time -- target send time: {SEND_TIME} (now: {current_time})")
                last_waiting_log_time = now_epoch

        # Run marker cleanup once an hour (no need to check every 30 sec)
        now_epoch = time.time()
        if now_epoch - last_cleanup_check >= WAITING_LOG_INTERVAL:
            cleanup_old_markers()
            last_cleanup_check = now_epoch

        time.sleep(30)