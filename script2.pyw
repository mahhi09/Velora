# Sent Logs To Google Drive

import os
import datetime
import time
from pathlib import Path


# -------------------------------------
# SETTINGS: apne hisaab se check/badlo
# -------------------------------------
LOG_DIR = Path(os.getenv("APPDATA")) / "Velora"
CREDS_FILE = LOG_DIR / "credentials.json"
TOKEN_FILE = LOG_DIR / "token.json"
ACTIVITY_LOG = LOG_DIR / "uploaded_log.txt"
DRIVE_FOLDER_ID = "1xoUGDauwC3HUoSOqSxxc8-B-QNL1jdy4" #<-- Paste Your DRIVE_FOLDER_ID
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
MIN_FILE_SIZE_BYTES = 1
# khaali file bhi bhejni hai to 1, varna jitna chaho
#______________________________________________________________________________________________________



# IMPORTANT: yeh dono 24-HOUR format mein hain (0 se 23)
# e.g. 4:50 PM chahiye to RUN_AFTER_HOUR = 16, RUN_AFTER_MINUTE = 50
RUN_AFTER_HOUR = 15      # 0-23 range, apna target hour daalo
RUN_AFTER_MINUTE = 50    # 0-59 range, apna target minute daalo

CHECK_EVERY_SECONDS = 30        # har 30 second mein time check karega
LOG_WAIT_EVERY_SECONDS = 300    # har 5 min mein "waiting" status uploaded_log.txt mein likhega

# Daily log file ka naam pattern: DD-MM-YYYY.log  (e.g. 28-06-2026.log)
DATE_FMT = "%d-%m-%Y"

RETENTION_DAYS = 2          # itne din purani daily .log file ho jaye to delete kar do
MARKER_RETENTION_DAYS = 7   # itne din purane *_DriveSent.log marker bhi delete ho jayein

UPLOAD_MAX_RETRIES = 3            # upload fail hone par kitni baar retry kare
UPLOAD_RETRY_DELAY_SECONDS = 15   # har retry ke beech kitna wait kare

MAX_ACTIVITY_LOG_LINES = 2000   # uploaded_log.txt mein max itni lines, varna purani trim ho jayengi

FORCE_RESEND = False   # True karo to aaj ka already-sent marker ignore karke dobara bhej dega
# -------------------------------------


def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_activity(message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
    trim_activity_log()


def trim_activity_log():
    try:
        if not ACTIVITY_LOG.exists():
            return
        lines = ACTIVITY_LOG.read_text(encoding="utf-8").splitlines()
        if len(lines) > MAX_ACTIVITY_LOG_LINES:
            trimmed = lines[-MAX_ACTIVITY_LOG_LINES:]
            ACTIVITY_LOG.write_text("\n".join(trimmed) + "\n", encoding="utf-8")
    except Exception:
        pass


# -------------------------------------
# TIME CHECK
# -------------------------------------
def is_after_target_time() -> bool:
    now = datetime.datetime.now()
    target = now.replace(hour=RUN_AFTER_HOUR, minute=RUN_AFTER_MINUTE, second=0, microsecond=0)
    return now >= target


# -------------------------------------
# FILE PATHS (daily log + sent marker)
# -------------------------------------
def todays_log_path() -> Path:
    today_str = datetime.date.today().strftime(DATE_FMT)
    return LOG_DIR / f"{today_str}.log"


def sent_marker_path() -> Path:
    today_str = datetime.date.today().strftime(DATE_FMT)
    return LOG_DIR / f"{today_str}_DriveSent.log"


def already_sent_today() -> bool:
    if FORCE_RESEND:
        return False
    return sent_marker_path().exists()


def mark_sent_today():
    marker = sent_marker_path()
    marker.write_text(
        f"Uploaded on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        encoding="utf-8",
    )


# -------------------------------------
# GOOGLE DRIVE AUTH
# -------------------------------------
def get_drive_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


# -------------------------------------
# FIND + UPLOAD LOG FILE
# -------------------------------------
def find_todays_log_file():
    filepath = todays_log_path()
    if filepath.exists() and filepath.stat().st_size >= MIN_FILE_SIZE_BYTES:
        return filepath
    return None


def upload_with_retry(service, filepath: Path):
    from googleapiclient.http import MediaFileUpload

    last_error = None
    for attempt in range(1, UPLOAD_MAX_RETRIES + 1):
        try:
            media = MediaFileUpload(str(filepath), mimetype="text/plain", resumable=True)
            metadata = {"name": filepath.name, "parents": [DRIVE_FOLDER_ID]}
            uploaded = service.files().create(body=metadata, media_body=media, fields="id").execute()
            return uploaded
        except Exception as e:
            last_error = e
            log_activity(f"Upload attempt {attempt}/{UPLOAD_MAX_RETRIES} fail: {e}")
            if attempt < UPLOAD_MAX_RETRIES:
                time.sleep(UPLOAD_RETRY_DELAY_SECONDS)

    raise last_error


def do_upload():
    if already_sent_today():
        log_activity(f"{sent_marker_path().name} already maujood hai, matlab aaj ki file pehle hi bhej di gayi thi. Skip.")
        return

    filepath = find_todays_log_file()
    if not filepath:
        log_activity(f"{todays_log_path().name} nahi mili, kuch nahi kiya.")
        return

    try:
        service = get_drive_service()
        uploaded = upload_with_retry(service, filepath)
        log_activity(f"Uploaded {filepath.name} -> Drive file id: {uploaded.get('id')}")
        mark_sent_today()
    except Exception as e:
        log_activity(f"Error (sab retries fail ho gaye): {e}")


# -------------------------------------
# CLEANUP OLD FILES
# -------------------------------------
def cleanup_old_logs():
    today = datetime.date.today()

    for file in LOG_DIR.glob("*.log"):
        is_marker = file.name.endswith("_DriveSent.log")

        if is_marker:
            date_part = file.name.replace("_DriveSent.log", "")
            limit_days = MARKER_RETENTION_DAYS
        else:
            date_part = file.stem
            limit_days = RETENTION_DAYS

        try:
            file_date = datetime.datetime.strptime(date_part, DATE_FMT).date()
        except ValueError:
            continue

        age_days = (today - file_date).days
        if age_days >= limit_days:
            try:
                file.unlink()
                kind = "marker" if is_marker else "daily log"
                log_activity(f"Purani {kind} file delete ki: {file.name} (age: {age_days} din)")
            except Exception as e:
                log_activity(f"Delete karte time error {file.name}: {e}")


# -------------------------------------
# MAIN LOOP
# -------------------------------------
def main():
    ensure_log_dir()
    target_time_str = f"{RUN_AFTER_HOUR:02d}:{RUN_AFTER_MINUTE:02d}"
    log_activity(f"Script shuru hui. Target time: {target_time_str} (24-hr) ka wait kar rahi hai...")

    last_wait_log = 0.0
    while True:
        try:
            if is_after_target_time():
                do_upload()
                cleanup_old_logs()
                break

            now_ts = time.time()
            if now_ts - last_wait_log >= LOG_WAIT_EVERY_SECONDS:
                current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
                log_activity(
                    f"Waiting... target time {target_time_str} hai, abhi current time {current_time_str} hai."
                )
                last_wait_log = now_ts

            time.sleep(CHECK_EVERY_SECONDS)

        except Exception as e:
            log_activity(f"Unexpected error in main loop: {e}")
            time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    main()