import os

def check_isolation():
    css_file = "front/css/auth.css"
    if not os.path.exists(css_file):
        return "❌ CSS File not found"

    with open(css_file, "r", encoding="utf-8") as f:
        content = f.read()
        
        # التأكد من استخدام المحدد :not(.dark-mode) للألوان الجديدة
        light_mode_logic = content.count(":not(.dark-mode)")
        
        # التأكد من أن الألوان الداكنة لم تتغير
        dark_mode_vars = ["--auth-bg: #0f172a", "--auth-text: #f8fafc"]
        dark_mode_ok = all(v in content for v in dark_mode_vars)

        if light_mode_logic >= 3 and dark_mode_ok:
            return "PASS: Light mode edits are isolated using :not(.dark-mode)."
        else:
            return f"FAIL: Potential contamination. Logic checks: {light_mode_logic}, Dark mode vars: {dark_mode_ok}"

if __name__ == "__main__":
    print(check_isolation())
