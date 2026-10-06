import os

INJECT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&display=swap" rel="stylesheet">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">'
    '<script src="/_astro/fix.js" defer></script>'
)

for fname in sorted(os.listdir('public')):
    if not fname.endswith('.html'):
        continue
    path = os.path.join('public', fname)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    html = html.replace('</head>', INJECT + '</head>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  injected: {fname}')
