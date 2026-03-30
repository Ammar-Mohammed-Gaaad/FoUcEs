import os
import re

html_files = [
    r'a:\FoUcs\FoUcEs\front\html\home.html',
    r'a:\FoUcs\FoUcEs\front\html\profile.html',
    r'a:\FoUcs\FoUcEs\front\html\notifications.html',
    r'a:\FoUcs\FoUcEs\front\html\learning-interview.html'
]

css_dir = r'a:\FoUcs\FoUcEs\front\css'
os.makedirs(css_dir, exist_ok=True)

style_pattern = re.compile(r'<style>(.*?)</style>', re.DOTALL | re.IGNORECASE)

for html_path in html_files:
    if not os.path.exists(html_path):
        print(f"Skipping {html_path}, file not found.")
        continue
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    match = style_pattern.search(content)
    if match:
        css_content = match.group(1).strip()
        
        # Determine css filename based on html filename
        basename = os.path.basename(html_path)
        name, _ = os.path.splitext(basename)
        css_filename = f"{name}.css"
        css_path = os.path.join(css_dir, css_filename)
        
        # Write CSS file
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content + '\n')
            
        print(f"Created {css_filename} from {basename}")
        
        # Replace the <style>...</style> block with <link ...>
        # Find if styles.css is already linked nearby to place it after
        link_tag = f'<link rel="stylesheet" href="../css/{css_filename}">'
        new_content = style_pattern.sub(link_tag, content)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {basename} with link to {css_filename}")
    else:
        print(f"No <style> block found in {html_path}")
