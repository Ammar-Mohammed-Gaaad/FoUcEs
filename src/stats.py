import json
import os

STATS_FILE = "stats.json"

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


def update_stat(app, seconds):
    stats = load_stats()

    if app not in stats:
        stats[app] = 0

    stats[app] += seconds

    save_stats(stats)