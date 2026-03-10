import psutil

BLOCKED_APPS = ["chrome.exe", "discord.exe"]


def enforce():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in BLOCKED_APPS:
                print(f"Killing {proc.info['name']}")
                proc.kill()
        except:
            pass


if __name__ == "__main__":
    enforce()