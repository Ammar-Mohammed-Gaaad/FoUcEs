import tkinter as tk
import psutil

def kill_process(process_name):
    """Searches the active memory and terminates the specific process."""
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            try:
                proc.kill()
                print(f"[ACTION] Terminated distracted process: {proc.info['name']}")
                killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Ignore processes that have already closed or require root access
                pass
    return killed

def show_warning():
    """Takes over the screen with a strict message."""
    window = tk.Tk()
    window.title("Focus Enforcer")
    
    # Force full screen and keep it on top of everything else
    window.attributes("-fullscreen", True)
    window.attributes("-topmost", True)
    window.configure(bg="black")
    
    # The warning message
    msg = tk.Label(
        window, 
        text="Stop playing! Let's continue our study courses.", 
        font=("Helvetica", 36, "bold"), 
        fg="red",
        bg="black"
    )
    msg.pack(expand=True)
    
    # The only way to close the window is to click this button
    btn = tk.Button(
        window, 
        text="I understand, I will study", 
        font=("Helvetica", 16),
        command=window.destroy,
        bg="white",
        fg="black"
    )
    btn.pack(pady=50)
    
    window.mainloop()