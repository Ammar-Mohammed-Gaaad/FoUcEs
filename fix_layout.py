import re

with open('front/html/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract profileView section
m = re.search(r'<section id="profileView".*?</section>', content, re.DOTALL)
if not m:
    print('profileView section not found')
    exit(1)

profile_html = m.group(0)
print(f'Found profileView ({len(profile_html)} chars)')

# Convert it to a section-view div (same system as dashboard)
profile_new = profile_html.replace(
    '<section id="profileView" class="page-section" style="display: none; padding-top: 50px;">',
    '<div id="profileView" class="section-view">'
).replace('</section>', '</div>')

# Remove old profileView (with surrounding whitespace)
content_clean = re.sub(
    r'\n\s*<section id="profileView".*?</section>\s*\n',
    '\n',
    content,
    flags=re.DOTALL
)

# Find content-body closing tag (it's right before </main>)
# structure: </div>  <- closes content-body
#            </main>
insert_marker = '        </div>\n    </main>'
if insert_marker not in content_clean:
    # Try alternate
    insert_marker = '        </div>\n\n    </main>'

if insert_marker not in content_clean:
    print('Could not find insert marker, trying another approach...')
    # Find </main> and work backwards
    main_end = content_clean.rfind('</main>')
    if main_end == -1:
        print('No </main> found!')
        exit(1)
    # Insert profileView before </main>
    content_new = (
        content_clean[:main_end] +
        '\n        ' + profile_new + '\n        </div>\n    </main>' +
        content_clean[main_end + len('</main>'):]
    )
    # But this would break the structure. Let me just inject it differently
    # Insert profile_new before the last </div></main>
    idx = content_clean.rfind('</div>', 0, main_end)
    content_new = (
        content_clean[:idx+6] +
        '\n\n            ' + profile_new +
        content_clean[idx+6:]
    )
else:
    content_new = content_clean.replace(
        insert_marker,
        '            ' + profile_new + '\n        </div>\n    </main>',
        1
    )

# Update showSection to use section-view approach (CSS class toggle, not style.display)
old_show = '''        function showSection(sectionId) {
            // 1. إخفاء الداشبورد (section-view) وكل الـ page-sections
            document.querySelectorAll('.section-view').forEach(sec => {
                sec.classList.remove('active');
                sec.style.display = 'none';
            });
            document.querySelectorAll('.page-section').forEach(sec => sec.style.display = 'none');

            // 2. إظهار القسم المطلوب
            const target = document.getElementById(sectionId);
            if (target) {
                target.style.display = 'block';
                if (target.classList.contains('section-view')) target.classList.add('active');
            }

            // 3. تحديث السايد بار
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

            if (sectionId === 'dashboard') {
                const btn = document.getElementById('btnDash');
                if (btn) btn.classList.add('active');
            }
            if (sectionId === 'profileView') {
                const btn = document.getElementById('btnProf');
                if (btn) btn.classList.add('active');
                fetchUserData();
            }
        }'''

new_show = '''        function showSection(sectionId) {
            // Hide all section-views (using the same CSS class mechanism as switchTab)
            document.querySelectorAll('.section-view').forEach(sec => sec.classList.remove('active'));

            // Show target section
            const target = document.getElementById(sectionId);
            if (target) target.classList.add('active');

            // Update sidebar active state
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            const btnDash = document.getElementById('btnDash');
            const btnProf = document.getElementById('btnProf');
            if (sectionId === 'dashboard' && btnDash) btnDash.classList.add('active');
            if (sectionId === 'profileView' && btnProf) {
                btnProf.classList.add('active');
                fetchUserData();
            }
        }'''

if old_show in content_new:
    content_new = content_new.replace(old_show, new_show)
    print('showSection updated')
else:
    print('WARNING: showSection not found for replacement - it may have changed')

with open('front/html/home.html', 'w', encoding='utf-8') as f:
    f.write(content_new)

print('Done! profileView moved inside content-body as section-view')
