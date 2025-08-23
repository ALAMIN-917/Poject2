python STA_GUI.pyStudent Academic Tracker - GUI

This repository contains a Tkinter-based GUI wrapper for the CLI project in `STA_DB.py`.

Files added/updated:
- `STA_GUI.py` - polished GUI using `ttk.Notebook` for Admin / Teacher / Student panels, background image support, and DB-bound actions.
- `requirements.txt` - includes `Pillow` for background image handling.

Quick start (Windows PowerShell):

1. Create a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Place a background image you want to use somewhere accessible. In the GUI use File → Set Background Image and pick it.

4. Run the GUI:

```powershell
python STA_GUI.py
```

Notes:
- If you don't install Pillow the GUI still works, but image background is disabled and the app will prompt to install Pillow when attempting to set a background image.
- The GUI reuses the SQLite database `college_db.sqlite3` in the project root. Ensure your `STA_DB.py` created the expected tables before using the GUI.

If you want, I can continue wiring more features or improve layout and styling further.
