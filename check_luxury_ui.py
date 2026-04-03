import os

css_path = "front/css/auth.css"

def verify_luxury():
    if not os.path.exists(css_path): 
        print(f"Path not found: {css_path}")
        return False
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()
        checks = [
            "blur(100px)" in content,
            "60s" in content,
            "backdrop-filter" in content,
            "auth-tabs" in content
        ]
        return all(checks)

if __name__ == "__main__":
    if verify_luxury():
        print("SUCCESS: Luxury UI Verified: Frosted glass and slow flow active.")
    else:
        print("ERROR: UI Quality Alert: Missing blur or slow animation.")
