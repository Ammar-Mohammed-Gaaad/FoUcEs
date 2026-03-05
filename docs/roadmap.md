# Focus Daemon: Project Roadmap

## Phase 1: System Design & Setup
- [ ] Map out the system architecture using UML sequence and use-case diagrams.
- [ ] Set up the Python virtual environment and `requirements.txt`.
- [ ] Research OS-level hooks for active window detection.

## Phase 2: The "Invisible Overseer" (Core Engine)
- [ ] Write `monitor.py` to use `psutil` to fetch running processes.
- [ ] Implement "Smart Polling" (checking the OS every 5 seconds to keep CPU usage < 1%).
- [ ] Create a target list of executable names to block.

## Phase 3: The "Fully Responsible" Enforcement
- [ ] Write `enforcer.py` with `os.kill()` to terminate forbidden processes instantly.
- [ ] Build an un-closable, full-screen `tkinter` overlay that blocks the monitor when triggered.
- [ ] Link the monitor to the enforcer.

## Phase 4: "On the Shelf" Silent Deployment
- [ ] Write the deployment configuration to strip away terminal windows.
- [ ] Register the script as a background daemon so it starts automatically on boot.
- [ ] Test system stability and resource consumption.