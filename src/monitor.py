import time
import psutil
from enforcer import kill_process, show_warning

# Add the exact executable names of the games or apps you want to block
FORBIDDEN_APPS = [
    "solitaire", 
    "minesweeper", 
    "steam", 
    "hl2" 
]

def is_forbidden_running():
    """Scans all running processes to see if a forbidden app is active."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name']:
            for app in FORBIDDEN_APPS:
                if app.lower() in proc.info['name'].lower():
                    return app
    return None

def run_daemon(poll_interval=5):
    """The main loop that runs silently in the background."""
    print("Focus Daemon started. Monitoring from the shelf...")
    
    while True:
        bad_app = is_forbidden_running()
        
        if bad_app:
            print(f"[ALERT] Distraction detected: {bad_app}")
            
            # Step 1: Kill the distracting app instantly
            kill_process(bad_app)
            
            # Step 2: Hijack the screen with the warning
            show_warning()
        
        # Go back to sleep for 5 seconds (keeps CPU usage < 1%)
        time.sleep(poll_interval)

if __name__ == "__main__":
    run_daemon()