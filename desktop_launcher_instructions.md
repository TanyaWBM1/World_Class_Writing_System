# Desktop Launcher Instructions

Confirmed launch method:

- the dashboard is a local `tkinter` app in `app/dashboard.py`
- it launches correctly through Python directly
- the confirmed Python executable is:
  `C:\Users\Billionaire Mind DT\AppData\Local\Programs\Python\Python313\python.exe`
- the launcher uses `pythonw.exe` from the same install to suppress the extra console window while preserving the same app behavior

Which launcher to use:

- use `launch_dashboard.vbs` for normal desktop launching
- `launch_dashboard.bat` is the direct launcher and is useful for testing or troubleshooting

How to create a desktop shortcut:

1. In File Explorer, go to:
   `C:\Users\Billionaire Mind DT\World_Class_Writing_System`
2. Right-click `launch_dashboard.vbs`
3. Select `Show more options` if needed
4. Click `Send to` -> `Desktop (create shortcut)`

What each file does:

- `launch_dashboard.bat` sets the repo folder as the working directory and starts `app/dashboard.py`
- `launch_dashboard.vbs` runs the batch launcher hidden so you do not get unnecessary terminal noise

Recommended desktop shortcut target:

- `launch_dashboard.vbs`
