import tkinter as tk
import json
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

SYSTEM_APPS = [
"System Idle Process",
"System",
"Registry",
"svchost.exe",
"smss.exe",
"services.exe",
"lsass.exe",
"csrss.exe",
"wininit.exe",
"winlogon.exe",
"fontdrvhost.exe",
"dwm.exe",
"RuntimeBroker.exe",
"WmiPrvSE.exe",
"conhost.exe",
"taskhostw.exe",
"spoolsv.exe",
"SearchIndexer.exe",
"SearchHost.exe",
"SearchProtocolHost.exe",
"backgroundTaskHost.exe",
"audiodg.exe"
]
STATS_FILE = "stats.json"

PRODUCTIVE = ["code.exe", "pycharm.exe", "notepad.exe"]

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)


def calculate_focus(stats):

    productive = 0
    total = 0

    for app, sec in stats.items():
        total += sec
        if app in PRODUCTIVE:
            productive += sec

    if total == 0:
        return 0

    return int((productive / total) * 100)


def refresh():

    stats = load_stats()

    text.delete("1.0", tk.END)

    for app, seconds in stats.items():

        if app in SYSTEM_APPS:
            continue

        minutes = seconds // 60

        if minutes == 0:
            continue

        text.insert(tk.END, f"{app:<20} {minutes} min\n")
    update_chart(stats)


def update_chart(stats):

    # sort apps by usage
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    # keep top 5 apps only
    top_apps = sorted_stats[:5]

    apps = [app for app, sec in top_apps]
    minutes = [sec // 60 for app, sec in top_apps]

    ax.clear()

    ax.bar(apps, minutes)

    ax.set_title("Top Apps Usage")
    ax.set_ylabel("Minutes")

    plt.xticks(rotation=45)

    canvas.draw()

window = tk.Tk()
window.title("Focus Monitor")
window.geometry("700x600")
window.configure(bg="#1e1e1e")

title = tk.Label(window, text="Focus Monitor Dashboard",
                 font=("Segoe UI",18),
                 fg="white",
                 bg="#1e1e1e")
title.pack(pady=10)

focus_label = tk.Label(window,
                       text="Focus Score: 0%",
                       font=("Segoe UI",14),
                       fg="white",
                       bg="#1e1e1e")
focus_label.pack()

button = tk.Button(window,
                   text="Refresh Stats",
                   command=refresh)
button.pack(pady=10)

text = tk.Text(window, height=10)
text.pack(fill="x", padx=10)

fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(fill="both", expand=True)

window.mainloop()