import os

def verify_sidebar_fix():
    home_file = "front/html/home.html"
    if not os.path.exists(home_file):
        print(f"File not found: {home_file}")
        return False
    with open(home_file, "r", encoding="utf-8") as f:
        content = f.read()
        is_integrated = "profileSection" in content
        has_nav = "side-nav" in content
        return is_integrated and has_nav

if __name__ == "__main__":
    if verify_sidebar_fix():
        print("SUCCESS: UI Integration: Sidebar fixed and Profile section unified.")
    else:
        print("ERROR: UI Failure: Profile is still a separate file or Sidebar missing.")
