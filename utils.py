import sys
import os
import shutil
from datetime import datetime
import json

#will find data file in: 
#C:\Users\<your-username>\AppData\Local\ProductivityTracker\data.json

def resource_path(filename="data.json", app_name="Productivity Tracker"):
    """
    Returns a writable, persistent path in AppData.
    Copies bundled default on first run.
    """

    # AppData location (hidden from normal view)
    appdata = os.getenv("LOCALAPPDATA")
    folder = os.path.join(appdata, app_name)

    os.makedirs(folder, exist_ok=True)

    writable_file = os.path.join(folder, filename)

    # Where bundled resources live
    if getattr(sys, "frozen", False):
        bundled_folder = sys._MEIPASS
    else:
        bundled_folder = os.path.dirname(os.path.abspath(__file__))

    bundled_file = os.path.join(bundled_folder, filename)

    # Copy default on first run
    if not os.path.exists(writable_file) and os.path.exists(bundled_file):
        shutil.copy(bundled_file, writable_file)

    return writable_file

def load_data():
    with open(resource_path('data.json'), 'r+') as f:
        data = json.load(f)

        if(data == {}):
            current_date = datetime.today().strftime('%A, %m-%d-%y')
            data = {
                "date": current_date,
                "score": 0,
                "historic_scores": [],
                "activity_list": [],
                "start_date": current_date
            }

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()