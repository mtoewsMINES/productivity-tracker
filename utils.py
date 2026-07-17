import sys
import os
import shutil
from datetime import datetime, timedelta
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

def newDay(data):
    with open(resource_path('data.json'), 'r+') as f:

        for i in range(len(data["activity_list"])):
            data["activity_list"][i]["total"] += data["activity_list"][i]["current_quantity"]
            data["activity_list"][i]["historic_daily_scores"].append(data["activity_list"][i]["current_quantity"])
            data["activity_list"][i]["days_tracked"] += 1
            data["activity_list"][i]["current_quantity"] = 0
            data["activity_list"][i]["historic_average_scores"].append(data["activity_list"][i]["total"] / data["activity_list"][i]["days_tracked"])
            if (data["activity_list"][i]["timeline"] == "By Date" 
            and datetime.strptime(data["activity_list"][i]["due_date"], "%A, %m-%d-%Y") <= datetime.strptime(data["date"], "%A, %m-%d-%Y")): 
                data["activity_list"][i]["active"] = False


        data["historic_scores"].append(data["score"]) 
        days_tracked = (datetime.strptime(data["date"], "%A, %m-%d-%Y") - datetime.strptime(data["start_date"], "%A, %m-%d-%Y")).days
        data["historic_averages"].append(sum(data["historic_scores"]) / (days_tracked or 1))
        data["date"] = (datetime.strptime(data["date"], "%A, %m-%d-%Y") + timedelta(days=1)).strftime("%A, %m-%d-%Y")

        return data["date"]

def load_data(reset=False):
    with open(resource_path('data.json'), 'r+') as f:
        current_date = datetime.today().strftime('%A, %m-%d-%Y')
        data = json.load(f)

        if reset or data == {}:
            data = {
                "date": current_date,
                "score": 0,
                "historic_scores": [],
                "historic_averages": [],
                "activity_list": [],
                "start_date": current_date
            }
        else:
            tracked_date = data["date"]
            while current_date != tracked_date and datetime.strptime(tracked_date, "%A, %m-%d-%Y") < datetime.strptime(current_date, "%A, %m-%d-%Y"):
                tracked_date = newDay(data)

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
