import json
import os

STATS_FILE = "../stats.json"

SYSTEM_APPS = [
    "System",
    "Registry",
    "svchost.exe",
    "lsass.exe",
    "services.exe",
    "csrss.exe",
    "wininit.exe",
    "fontdrvhost.exe"
]


def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)


def show_dashboard():

    stats = load_stats()

    print("\n===== Focus Dashboard =====\n")

    for app, seconds in stats.items():

        if app in SYSTEM_APPS:
            continue

        minutes = seconds // 60

        print(f"{app:<20} {minutes} minutes")


if __name__ == "__main__":
    show_dashboard()