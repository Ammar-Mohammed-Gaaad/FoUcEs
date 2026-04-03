import os

def verify_premium_setup():
    checks = {
        "Voice Logic": os.path.exists("front/js/ai_assistant.js"),
        "Documentation": os.path.exists("front/docs/ai_copilot_guide.md"),
        "API Key Config": "gsk_" in open("src/ai_agent.py", encoding="utf-8").read()
    }
    for label, status in checks.items():
        # replaced emoji with ascii
        icon = "[PASS]" if status else "[FAIL]"
        print(f"{icon} {label}")

if __name__ == "__main__":
    verify_premium_setup()
