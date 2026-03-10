import time
import psutil
import json
import os

STATS_FILE = "stats.json"
INTERVAL = 5


def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


def monitor():
    print("Focus Monitor Started...")

    while True:

        stats = load_stats()

        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']

                if name:
                    if name not in stats:
                        stats[name] = 0

                    stats[name] += INTERVAL

            except:
                pass

        save_stats(stats)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    monitor()