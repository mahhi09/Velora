import subprocess
import sys
import os

folder = os.path.dirname(os.path.abspath(__file__))

try:
    subprocess.Popen([sys.executable, os.path.join(folder, "script1.pyw")])
except Exception as e:
    print(f"Script 1 start karne mein issue: {e}")

try:
    subprocess.Popen([sys.executable, os.path.join(folder, "script2.pyw")])
except Exception as e:
    print(f"Script 2 start karne mein issue: {e}")

try:
    subprocess.Popen([sys.executable, os.path.join(folder, "script3.pyw")])
except Exception as e:
    print(f"Script 3 start karne mein issue: {e}")

try:
    subprocess.Popen([sys.executable, os.path.join(folder, "script4.pyw")])
except Exception as e:
    print(f"Script 4 start karne mein issue: {e}")