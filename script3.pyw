# Delete Logs File
import os
import datetime
from pathlib import Path

LOG_DIR = Path(os.getenv("APPDATA")) / "Velora"
ACTIVITY_LOG = LOG_DIR / "uploaded_log.txt"

# -------------------------------------
# TESTING MODE (abhi 5 minute purani files delete hongi)
# -------------------------------------
# DELETE_OLDER_THAN = datetime.timedelta(minutes=5)

# -------------------------------------
# FINAL/PRODUCTION MODE (2 din purani files delete hongi)
# Test ho jaaye to upar wali line ko # laga ke comment kar do,
# aur neeche wali line se # hata do:
# -------------------------------------
DELETE_OLDER_THAN = datetime.timedelta(days=2)
# -------------------------------------

# uploaded_log.txt ke liye alag rule - isme kitne din baad delete karna hai
ACTIVITY_LOG_MAX_DAYS = 5  # 5 din tak rakho, 6th din delete

# *_DriveSent.log marker files (jaise 28-06-2026_DriveSent.log) - inki retention
# Example: aaj 25 hai to 23 wali file (2 din purani) delete ho jayegi
DRIVE_SENT_RETENTION_DAYS = 2
# -------------------------------------


def log_cleanup(message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Agar file pehli baar ban rahi hai, to sabse pehle CREATED line likho
    file_is_new = not ACTIVITY_LOG.exists()

    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        if file_is_new:
            today_str = datetime.date.today().isoformat()
            f.write(f"# CREATED:{today_str}\n")
        f.write(f"[{ts}] [CLEANUP] {message}\n")


def file_logical_date(file: Path):
    try:
        return datetime.datetime.strptime(file.stem, "%d-%m-%Y").date()
    except ValueError:
        return None


def is_old_enough(file: Path) -> bool:
    logical_date = file_logical_date(file)

    if logical_date is not None:
        ref_time = datetime.datetime.combine(logical_date, datetime.time.min)
    else:
        ref_time = datetime.datetime.fromtimestamp(file.stat().st_mtime)

    age = datetime.datetime.now() - ref_time
    return age >= DELETE_OLDER_THAN


def marker_for(file: Path) -> Path:
    logical_date = file_logical_date(file)

    if logical_date is None:
        logical_date = datetime.date.fromtimestamp(file.stat().st_mtime)

    return LOG_DIR / f"sent_{logical_date.isoformat()}.marker"


# -------------------------------------
# *_DriveSent.log style markers (DD-MM-YYYY_DriveSent.log)
# -------------------------------------
def drive_sent_marker_date(file: Path):
    # "28-06-2026_DriveSent.log" -> "28-06-2026" -> date nikalo
    date_part = file.name.replace("_DriveSent.log", "")
    try:
        return datetime.datetime.strptime(date_part, "%d-%m-%Y").date()
    except ValueError:
        return None


def cleanup_drive_sent_logs():
    today = datetime.date.today()

    for marker_file in LOG_DIR.glob("*_DriveSent.log"):
        file_date = drive_sent_marker_date(marker_file)

        if file_date is None:
            print(f"Skip (naam pattern match nahi hua): {marker_file.name}")
            continue

        age_days = (today - file_date).days

        if age_days >= DRIVE_SENT_RETENTION_DAYS:
            try:
                marker_file.unlink()
                log_cleanup(f"Deleted DriveSent marker: {marker_file.name} (age: {age_days} din)")
                print(f"Deleted DriveSent marker: {marker_file.name} (age: {age_days} din)")
            except Exception as e:
                log_cleanup(f"Error deleting {marker_file.name}: {e}")
                print(f"Error deleting {marker_file.name}: {e}")
        else:
            print(f"Skip (abhi {age_days} din hua): {marker_file.name}")


def cleanup_log_files():
    for log_file in LOG_DIR.glob("*.log"):
        # _DriveSent.log files yahan se skip - unke liye alag function hai (upar wala)
        if log_file.name.endswith("_DriveSent.log"):
            continue

        if not is_old_enough(log_file):
            print(f"Skip (abhi purani nahi): {log_file.name}")
            continue

        marker = marker_for(log_file)

        if marker.exists():
            try:
                log_file.unlink()
                log_cleanup(f"Deleted (upload confirmed): {log_file.name}")
                print(f"Deleted (upload confirmed): {log_file.name}")

                marker.unlink()
                log_cleanup(f"Deleted marker: {marker.name}")
                print(f"Deleted marker: {marker.name}")
            except Exception as e:
                log_cleanup(f"Error deleting {log_file.name}: {e}")
                print(f"Error deleting {log_file.name}: {e}")
        else:
            print(f"Skip (upload confirm nahi mila, safe rakha): {log_file.name}")
            log_cleanup(f"Skip - upload marker nahi mila: {log_file.name}")


def cleanup_orphan_markers():
    for marker_file in LOG_DIR.glob("sent_*.marker"):
        if is_old_enough(marker_file):
            try:
                marker_file.unlink()
                log_cleanup(f"Deleted orphan marker: {marker_file.name}")
                print(f"Deleted orphan marker: {marker_file.name}")
            except Exception as e:
                print(f"Error deleting {marker_file.name}: {e}")


def cleanup_activity_log():
    # uploaded_log.txt mein bahut sari scripts likhti hain, isliye sirf
    # first line pe depend nahi kar sakte. Poori file scan karenge
    # CREATED line dhoondne ke liye.
    if not ACTIVITY_LOG.exists():
        print(f"Skip: {ACTIVITY_LOG.name} (exist nahi karta)")
        return

    try:
        created_date = None

        with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# CREATED:"):
                    created_date_str = line.replace("# CREATED:", "").strip()
                    try:
                        found_date = datetime.date.fromisoformat(created_date_str)
                        # Agar multiple CREATED lines mil jaye (kabhi kabhi ho sakta hai),
                        # to sabse PURANI (chhoti) date lenge - sabse safe option
                        if created_date is None or found_date < created_date:
                            created_date = found_date
                    except ValueError:
                        continue  # galat format wali line, ignore karo

        if created_date is None:
            # Koi CREATED line nahi mili poori file mein - purani format wali file hai
            print(f"CREATED line nahi mili poori file mein - skip kar rahe: {ACTIVITY_LOG.name}")
            return

        age_days = (datetime.date.today() - created_date).days
        print(f"uploaded_log.txt ki age: {age_days} din (created: {created_date})")

        if age_days >= ACTIVITY_LOG_MAX_DAYS:
            ACTIVITY_LOG.unlink()
            print(f"Deleted (age {age_days} din ho gayi): {ACTIVITY_LOG.name}")
        else:
            print(f"Skip (abhi {age_days} din hua, {ACTIVITY_LOG_MAX_DAYS} din chahiye): {ACTIVITY_LOG.name}")

    except Exception as e:
        print(f"Error checking {ACTIVITY_LOG.name}: {e}")


def main():
    cleanup_log_files()
    cleanup_orphan_markers()
    cleanup_drive_sent_logs()
    cleanup_activity_log()


if __name__ == "__main__":
    main()