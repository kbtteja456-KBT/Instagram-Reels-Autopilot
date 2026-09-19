import os
import sys
from pathlib import Path

STARTUP_DIR = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
INST_DIR = Path(r"c:\Users\DELL\OneDrive\Desktop\inst")
TARGET_VBS = INST_DIR / "run_autopilot_silent.vbs"

startup_vbs = STARTUP_DIR / "Instagram_Autopilot_24x7.vbs"

content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{str(INST_DIR)}"
WshShell.Run """{sys.executable}"" ""{str(INST_DIR / 'scripts' / 'autopilot_daemon.py')}""", 0, False
'''

with open(startup_vbs, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Created startup autostart script at: {startup_vbs}")
