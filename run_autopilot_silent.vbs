Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\DELL\OneDrive\Desktop\inst"
WshShell.Run """C:\Users\DELL\AppData\Local\Programs\Python\Python314\python.exe"" ""c:\Users\DELL\OneDrive\Desktop\inst\scripts\autopilot_daemon.py""", 0, False
