#!/usr/bin/env python3
"""
IMAGE INVENTORY BUILDER (v3 — custom categories)

Run AFTER extract_site.py finishes. It scans
chuckeke-extract/assets/images/ and builds an interactive HTML catalog
where you can:

  1. Click images to select them (shift+click for range, cmd/ctrl+click to toggle)
  2. Type ANY category name (e.g. "headshot", "book-cover", "bill-clinton")
  3. Click "Assign to category" — selected images go into that group
  4. Repeat for other groups; the sidebar tracks all categories
  5. Click categories in the sidebar to view/copy their contents
  6. Click "Export all" to copy a structured JSON of every category

Categories save to your browser between sessions.

Usage:
  cd chuckeke-extract
  python3 image_inventory.py
  open image_inventory.html  (or just double-click it)
"""

import sys
import json
from pathlib import Path

HERE = Path.cwd()
IMG_DIR = HERE / "assets" / "images"

if not IMG_DIR.exists():
    print(f"ERROR: Can't find {IMG_DIR}")
    print("Run this from inside the chuckeke-extract folder.")
    sys.exit(1)

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
images = []
for fp in sorted(IMG_DIR.rglob("*")):
    if fp.is_file() and fp.suffix.lower() in EXTS:
        rel = fp.relative_to(HERE)
        size_kb = round(fp.stat().st_size / 1024, 1)
        images.append({
            "path": str(rel).replace("\\", "/"),
            "name": fp.name,
            "stem": fp.stem,
            "size_kb": size_kb,
        })

if not images:
    print(f"No images found in {IMG_DIR}")
    sys.exit(1)

print(f"Found {len(images)} images.")

DATA_JSON = json.dumps(images)

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>chuckeke.com — image inventory</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, system-ui, sans-serif;
         background: #0f0f10; color: #eee; }
  .layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
  .sidebar { background: #16161a; border-right: 1px solid #2a2a30;
             padding: 20px; position: sticky; top: 0; height: 100vh;
             overflow-y: auto; }
  .sidebar h2 { margin: 0 0 12px; font-size: 14px;
                text-transform: uppercase; letter-spacing: 0.05em;
                color: #888; }
  .cat-list { list-style: none; padding: 0; margin: 0; }
  .cat-list li { padding: 8px 10px; border-radius: 6px; cursor: pointer;
                 margin-bottom: 4px; font-size: 13px;
                 display: flex; justify-content: space-between; align-items: center; }
  .cat-list li:hover { background: #22222a; }
  .cat-list li.active { background: #2d4ed8; color: #fff; }
  .cat-list .count { background: #2a2a30; color: #aaa; border-radius: 10px;
                     padding: 1px 8px; font-size: 11px; }
  .cat-list li.active .count { background: rgba(255,255,255,0.2); color: #fff; }
  .main { padding: 20px 24px; }
  .toolbar { position: sticky; top: 0; background: #0f0f10; padding: 12px 0;
             border-bottom: 1px solid #2a2a30; z-index: 10;
             display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  input[type=text] { background: #1a1a1f; border: 1px solid #2a2a30;
                     color: #eee; padding: 8px 10px; border-radius: 6px;
                     font-size: 13px; min-width: 200px; }
  button { background: #2d4ed8; color: #fff; border: 0; padding: 8px 14px;
           border-radius: 6px; font-size: 13px; cursor: pointer;
           font-weight: 500; }
  button:hover { background: #3b5ee8; }
  button.ghost { background: #22222a; color: #ddd; }
  button.ghost:hover { background: #2a2a32; }
  button.danger { background: #b91c1c; }
  .stats { color: #888; font-size: 12px; margin-left: auto; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 12px; padding: 20px 0; }
  .card { background: #16161a; border: 2px solid transparent; border-radius: 8px;
          overflow: hidden; cursor: pointer; transition: border-color 0.1s; }
  .card.selected { border-color: #2d4ed8; }
  .card img { width: 100%; height: 140px; object-fit: cover; display: block;
              background: #000; }
  .card .meta { padding: 8px 10px; font-size: 11px; color: #aaa;
                word-break: break-all; line-height: 1.4; }
  .card .meta strong { color: #eee; font-size: 12px; }
  .toast { position: fixed; bottom: 20px; right: 20px; background: #22c55e;
           color: #fff; padding: 10px 16px; border-radius: 6px; font-size: 13px;
           opacity: 0; transition: opacity 0.2s; pointer-events: none; }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <h2>Categories</h2>
    <ul id="catList" class="cat-list"></ul>
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #2a2a30;">
      <button class="ghost" style="width:100%; margin-bottom: 8px;" onclick="exportAll()">Export all as JSON</button>
      <button class="ghost" style="width:100%;" onclick="clearAllCategories()">Clear all categories</button>
    </div>
  </aside>

  <main class="main">
    <div class="toolbar">
      <input type="text" id="search" placeholder="Filter by filename..." oninput="render()">
      <input type="text" id="catName" placeholder="Category name (e.g. headshot)">
      <button onclick="assignCategory()">Assign to category</button>
      <button class="ghost" onclick="selectAll()">Select all</button>
      <button class="ghost" onclick="deselectAll()">Deselect</button>
      <button class="ghost" onclick="copySelectedFilenames()">Copy filenames</button>
      <span class="stats" id="stats"></span>
    </div>
    <div class="grid" id="grid"></div>
  </main>
</div>

<div class="toast" id="toast"></div>

<script>
const ALL = """ + DATA_JSON + """;
const STORAGE_KEY = 'chuckeke-categories-v3';
let categories = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
let selected = new Set();
let lastClicked = null;
let activeCategory = null;

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(categories));
}
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}
function visibleImages() {
  const q = document.getElementById('search').value.toLowerCase();
  let list = ALL.filter(i => !q || i.name.toLowerCase().includes(q));
  if (activeCategory && categories[activeCategory]) {
    const set = new Set(categories[activeCategory]);
    list = list.filter(i => set.has(i.path));
  }
  return list;
}
function render() {
  const grid = document.getElementById('grid');
  const list = visibleImages();
  grid.innerHTML = list.map(img => {
    const sel = selected.has(img.path) ? 'selected' : '';
    return `<div class="card ${sel}" data-path="${img.path}">
      <img src="${img.path}" loading="lazy" ondblclick="window.open('${img.path}')">
      <div class="meta"><strong>${img.stem}</strong><br>${img.size_kb} KB</div>
    </div>`;
  }).join('');
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', e => handleClick(e, card.dataset.path));
  });
  document.getElementById('stats').textContent =
    `${list.length} shown · ${selected.size} selected · ${Object.keys(categories).length} categories`;
  renderSidebar();
}
function renderSidebar() {
  const ul = document.getElementById('catList');
  const names = Object.keys(categories).sort();
  if (!names.length) {
    ul.innerHTML = '<li style="color:#666; cursor:default;">No categories yet</li>';
    return;
  }
  ul.innerHTML =
    `<li class="${activeCategory === null ? 'active' : ''}" onclick="setCategory(null)">
       <span>All images</span><span class="count">${ALL.length}</span></li>` +
    names.map(n => `<li class="${activeCategory === n ? 'active' : ''}" onclick="setCategory('${n}')">
      <span>${n}</span><span class="count">${categories[n].length}</span></li>`).join('');
}
function setCategory(name) {
  activeCategory = name;
  selected.clear();
  render();
}
function handleClick(e, path) {
  if (e.shiftKey && lastClicked) {
    const list = visibleImages().map(i => i.path);
    const a = list.indexOf(lastClicked), b = list.indexOf(path);
    if (a >= 0 && b >= 0) {
      const [s, e2] = a < b ? [a, b] : [b, a];
      for (let i = s; i <= e2; i++) selected.add(list[i]);
    }
  } else if (e.metaKey || e.ctrlKey) {
    if (selected.has(path)) selected.delete(path); else selected.add(path);
  } else {
    if (selected.has(path) && selected.size === 1) selected.delete(path);
    else { selected.clear(); selected.add(path); }
  }
  lastClicked = path;
  render();
}
function selectAll() {
  visibleImages().forEach(i => selected.add(i.path));
  render();
}
function deselectAll() { selected.clear(); render(); }
function assignCategory() {
  const name = document.getElementById('catName').value.trim();
  if (!name) { toast('Type a category name first'); return; }
  if (!selected.size) { toast('Select some images first'); return; }
  if (!categories[name]) categories[name] = [];
  selected.forEach(p => {
    if (!categories[name].includes(p)) categories[name].push(p);
  });
  save();
  toast(`${selected.size} images → "${name}"`);
  selected.clear();
  document.getElementById('catName').value = '';
  render();
}
function copySelectedFilenames() {
  if (!selected.size) { toast('Nothing selected'); return; }
  const names = [...selected].map(p => {
    const stem = p.split('/').pop().replace(/\\.[^.]+$/, '');
    return stem;
  });
  navigator.clipboard.writeText(names.join('\\n'));
  toast(`Copied ${names.length} filenames`);
}
function exportAll() {
  // export filenames (stems) grouped by category
  const out = {};
  for (const [name, paths] of Object.entries(categories)) {
    out[name] = paths.map(p => p.split('/').pop().replace(/\\.[^.]+$/, ''));
  }
  const json = JSON.stringify(out, null, 2);
  navigator.clipboard.writeText(json);
  toast('Exported JSON to clipboard');
  console.log(json);
}
function clearAllCategories() {
  if (!confirm('Delete ALL categories? This cannot be undone.')) return;
  categories = {};
  activeCategory = null;
  save();
  render();
}
render();
</script>
</body>
</html>
"""

out_path = HERE / "image_inventory.html"
out_path.write_text(HTML, encoding="utf-8")
print(f"\nWrote {out_path}")
print("Open it in your browser to start tagging.")
