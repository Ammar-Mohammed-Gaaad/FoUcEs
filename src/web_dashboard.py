from flask import Flask, render_template
import json
import os

app = Flask(__name__)

STATS_FILE = "stats.json"

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)

@app.route("/")
def dashboard():

    data = load_stats()

    apps = list(data.keys())
    times = [round(v/60,2) for v in data.values()]  # convert to minutes

    return render_template("dashboard.html", apps=apps, times=times)

if __name__ == "__main__":
    app.run(debug=True)