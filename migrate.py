import re

def migrate():
    with open('front/html/profile.html', 'r', encoding='utf-8') as f:
        prof_html = f.read()

    # Extract the main body of the profile page (from the container to just before the scripts)
    body_match = re.search(r'<div class="container">(.*?)(<!-- ===== INITIALIZE =====|</div>\s*<script>)', prof_html, re.DOTALL)
    if not body_match:
        print("Could not find body in profile.html")
        return

    profile_content = body_match.group(1).strip()
    
    # We also need the JS scripts from profile.html to make it fully functional inside home.html
    scripts_match = re.search(r'(<script>.*?document\.addEventListener\(\'DOMContentLoaded\'.*?</script>)', prof_html, re.DOTALL)
    scripts_content = scripts_match.group(1).replace("document.addEventListener('DOMContentLoaded', async () => {", "async function loadProfileView() {") if scripts_match else ""

    new_section = f"""
    <section id="profileView" class="page-section" style="display: none; padding-top: 50px;">
        <div class="container">
            {profile_content}
        </div>
    </section>
    """

    with open('front/html/home.html', 'r', encoding='utf-8') as f:
        home_html = f.read()

    # Insert the new section before </main>
    if '<section id="profileView"' not in home_html:
        home_html = home_html.replace('</main>', new_section + '\n    </main>')

    # Update sidebar HTML based on the provided snippet
    home_html = re.sub(
        r'<a class="nav-item" href="profile\.html" tabindex="0">.*?</a>',
        '''<div class="nav-item" onclick="showSection('profileView')" id="navProfile">
            <span class="material-icons-outlined">account_circle</span>
            <span>الملف الشخصي</span>
        </div>''',
        home_html, flags=re.DOTALL
    )

    # Add the showSection function and the profile scripts into home.html
    new_js = f"""
    {scripts_content}
    <script>
    function showSection(sectionId) {{
        document.querySelectorAll('.page-section, .section-view').forEach(s => s.style.display = 'none');
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        
        const target = document.getElementById(sectionId);
        if (target) {{
            target.style.display = 'block';
            if (sectionId === 'profileView') {{
                if (typeof loadProfileView === 'function') loadProfileView();
                else if (typeof fetchUserData === 'function') fetchUserData();
            }}
        }}

        // Set active class
        document.querySelectorAll('.nav-item').forEach(item => {{
            const onclickAttr = item.getAttribute('onclick') || '';
            const hrefAttr = item.getAttribute('href') || '';
            
            // if this nav item targets our section
            if (onclickAttr.includes(sectionId) || hrefAttr.includes(sectionId)) {{
                item.classList.add('active');
            }}
        }});
    }}
    </script>
    """
    
    if 'function showSection' not in home_html:
        home_html = home_html.replace('</body>', new_js + '\n</body>')

    with open('front/html/home.html', 'w', encoding='utf-8') as f:
        f.write(home_html)
    
    print("Migration successful")

if __name__ == '__main__':
    migrate()
