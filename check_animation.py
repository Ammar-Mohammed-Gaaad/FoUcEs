import os

css_path = os.path.join('front', 'css', 'styles.css')

if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '@keyframes gradientAnimation' in content and 'background-size: 400%' in content:
            print("✅ SUCCESS: Animated gradient background is implemented in CSS.")
        else:
            print("❌ FAILED: Animation code or background-size is missing in CSS.")
else:
    print(f"❌ Error: CSS file not found at {css_path}")
