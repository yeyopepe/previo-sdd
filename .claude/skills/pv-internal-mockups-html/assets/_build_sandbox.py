import re

master = open("mockup-annotations.html", encoding="utf-8").read()
style_m = re.search(r'(<style id="mnoteqz7k-styles">.*?</style>)', master, re.S)
runtime_m = re.search(r'(^<script id="mnoteqz7k-runtime">.*?^</script>)', master, re.S | re.M)
style_block = style_m.group(1)
runtime_block = runtime_m.group(1)

demo_body = """
<h1>mnoteqz7k-framework v1 — sandbox</h1>
<p>Click any element below to select it, then use the floating bar's <strong>+</strong> to
attach a note or add a general one. This body exists only to manually exercise the framework
against a variety of widgets — <code>pv-internal-mockups-html</code> never copies this file or
this body, only the <code>#mnoteqz7k-styles</code>/<code>#mnoteqz7k-runtime</code> blocks above
(injected verbatim from <code>mockup-annotations.html</code>).</p>
<div style="display:flex; gap:1rem; margin-top:1rem; align-items:flex-start;">
  <button style="padding:.5rem .9rem;">Save</button>
  <button style="padding:.5rem .9rem;">Cancel</button>
  <button id="demo-help" style="padding:.5rem .9rem;">Help</button>
</div>

<h2 style="margin-top:2rem;">Interactive widgets</h2>
<p>These exist to check the runtime doesn't break the mockup's own interactivity in normal mode
(eye on), and doesn't get in the way of note-taking clicks in note mode (eye off).</p>

<div style="display:flex; gap:2rem; align-items:flex-start; margin-top:1rem;">
  <div>
    <button id="demo-dropdown-btn" style="padding:.5rem .9rem;">Options ▾</button>
    <div id="demo-dropdown-menu" style="display:none; margin-top:.3rem; border:1px solid #ccc; border-radius:4px; width:160px;">
      <div style="padding:.4rem .6rem; cursor:pointer;" class="demo-dropdown-item">Rename</div>
      <div style="padding:.4rem .6rem; cursor:pointer;" class="demo-dropdown-item">Duplicate</div>
      <div style="padding:.4rem .6rem; cursor:pointer;" class="demo-dropdown-item">Delete</div>
    </div>
  </div>

  <div>
    <button id="demo-toggle-btn" style="padding:.5rem .9rem;">Toggle panel</button>
    <div id="demo-toggle-panel" style="display:none; margin-top:.3rem; border:1px solid #ccc; border-radius:4px; padding:.6rem; width:200px;">
      This panel appears/disappears on click — should keep working with annotations on or off.
    </div>
  </div>

  <div>
    <button id="demo-counter-btn" style="padding:.5rem .9rem;">Clicked: <span id="demo-counter-value">0</span></button>
  </div>
</div>

<script>
(function () {
  var ddBtn = document.getElementById("demo-dropdown-btn");
  var ddMenu = document.getElementById("demo-dropdown-menu");
  ddBtn.addEventListener("click", function (ev) {
    ev.stopPropagation();
    ddMenu.style.display = ddMenu.style.display === "none" ? "block" : "none";
  });
  document.querySelectorAll(".demo-dropdown-item").forEach(function (item) {
    item.addEventListener("click", function () { ddMenu.style.display = "none"; });
  });

  var tgBtn = document.getElementById("demo-toggle-btn");
  var tgPanel = document.getElementById("demo-toggle-panel");
  tgBtn.addEventListener("click", function () {
    tgPanel.style.display = tgPanel.style.display === "none" ? "block" : "none";
  });

  var ctBtn = document.getElementById("demo-counter-btn");
  var ctVal = document.getElementById("demo-counter-value");
  var count = 0;
  ctBtn.addEventListener("click", function () {
    count++;
    ctVal.textContent = String(count);
  });
})();
</script>

<h2 style="margin-top:2rem;">More widget types</h2>
<div style="display:flex; gap:2rem; align-items:flex-start; margin-top:1rem; flex-wrap:wrap;">
  <div>
    <label for="demo-text-input" style="display:block; font-size:.85rem; margin-bottom:.25rem;">Text input</label>
    <input id="demo-text-input" type="text" placeholder="Type here…" style="padding:.4rem .5rem;">
  </div>

  <div>
    <label style="display:block; font-size:.85rem; margin-bottom:.25rem;">
      <input id="demo-checkbox" type="checkbox"> Enable notifications
    </label>
    <label style="display:block; font-size:.85rem;">
      <input type="radio" name="demo-radio" value="a" checked> Option A
    </label>
    <label style="display:block; font-size:.85rem;">
      <input type="radio" name="demo-radio" value="b"> Option B
    </label>
  </div>

  <div>
    <label for="demo-select" style="display:block; font-size:.85rem; margin-bottom:.25rem;">Select</label>
    <select id="demo-select" style="padding:.4rem .5rem;">
      <option>First</option>
      <option>Second</option>
      <option>Third</option>
    </select>
  </div>

  <div>
    <div style="display:flex; gap:.25rem; border-bottom:1px solid #ccc;">
      <button class="demo-tab" data-tab="1" style="padding:.4rem .8rem; border:0; background:#e9edf0; cursor:pointer;">Tab 1</button>
      <button class="demo-tab" data-tab="2" style="padding:.4rem .8rem; border:0; background:transparent; cursor:pointer;">Tab 2</button>
    </div>
    <div id="demo-tab-panel-1" style="padding:.6rem; border:1px solid #ccc; border-top:0; width:180px;">Content of tab 1.</div>
    <div id="demo-tab-panel-2" style="display:none; padding:.6rem; border:1px solid #ccc; border-top:0; width:180px;">Content of tab 2.</div>
  </div>

  <div>
    <button id="demo-modal-open" style="padding:.5rem .9rem;">Open modal</button>
  </div>
</div>

<div id="demo-modal-overlay" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,.4); z-index:1000; align-items:center; justify-content:center;">
  <div id="demo-modal" style="background:#fff; border-radius:8px; padding:1.2rem; width:280px;">
    <h3 style="margin:0 0 .6rem;">Demo modal</h3>
    <p style="margin:0 0 1rem; font-size:.85rem;">A modal dialog, to check the framework doesn't fight with an overlay's own stacking/clicks.</p>
    <button id="demo-modal-close" style="padding:.4rem .8rem;">Close</button>
  </div>
</div>

<script>
(function () {
  document.querySelectorAll(".demo-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      document.querySelectorAll(".demo-tab").forEach(function (t) { t.style.background = "transparent"; });
      tab.style.background = "#e9edf0";
      document.getElementById("demo-tab-panel-1").style.display = tab.dataset.tab === "1" ? "block" : "none";
      document.getElementById("demo-tab-panel-2").style.display = tab.dataset.tab === "2" ? "block" : "none";
    });
  });

  var modalOverlay = document.getElementById("demo-modal-overlay");
  document.getElementById("demo-modal-open").addEventListener("click", function () {
    modalOverlay.style.display = "flex";
  });
  document.getElementById("demo-modal-close").addEventListener("click", function () {
    modalOverlay.style.display = "none";
  });
  modalOverlay.addEventListener("click", function (ev) {
    if (ev.target === modalOverlay) modalOverlay.style.display = "none";
  });
})();
</script>

<h2 style="margin-top:2rem;">Complex nested structures</h2>
<p>Deep nesting, inherited typography/color, images, overflow/scroll containers, and elements
that set their own <code>position</code> — to stress the robust-selector path and badge/card
positioning against real-world layout complexity, not just flat buttons.</p>

<style>
  .demo-card-list { display:flex; gap:1.5rem; flex-wrap:wrap; margin-top:1rem; }
  .demo-card { width:260px; border:1px solid #d0d0d0; border-radius:10px; overflow:hidden;
    background:#fff; box-shadow:0 1px 3px rgba(0,0,0,.12); font-family:Georgia, serif; color:#333; }
  .demo-card__banner { height:70px; background:linear-gradient(135deg,#6a89cc,#4a69bd); position:relative; }
  .demo-card__avatar { position:absolute; left:16px; bottom:-24px; width:48px; height:48px;
    border-radius:50%; border:3px solid #fff; background:#fff; overflow:hidden; }
  .demo-card__body { padding:32px 16px 14px; }
  .demo-card__body h3 { margin:0 0 4px; font-size:1.05rem; color:inherit; }
  .demo-card__body .demo-role { font-size:.8rem; color:#888; font-style:italic; }
  .demo-card__meta { display:flex; gap:.6rem; margin-top:.6rem; font-size:.75rem; color:#666; }
  .demo-card__meta span { background:#f0f0f0; padding:.15rem .5rem; border-radius:999px; }
  .demo-card__footer { border-top:1px solid #eee; padding:.5rem .75rem; display:flex; justify-content:flex-end; gap:.4rem; }
  .demo-card__footer button { border:1px solid #ccc; background:#fafafa; border-radius:4px;
    padding:.3rem .6rem; font-size:.78rem; cursor:pointer; font-family:inherit; }

  .demo-tree { font-family:"Courier New", monospace; font-size:.82rem; color:#2b2b2b;
    background:#f7f7f7; border:1px solid #ddd; border-radius:6px; padding:.8rem 1rem; width:320px; }
  .demo-tree ul { list-style:none; margin:.2rem 0 .2rem 1rem; padding-left:.8rem;
    border-left:1px dashed #bbb; }
  .demo-tree li { margin:.15rem 0; }
  .demo-tree .demo-leaf { color:#1b6f3c; cursor:pointer; }
  .demo-tree .demo-leaf:hover { text-decoration:underline; }

  .demo-scrollbox { width:280px; height:140px; overflow-y:auto; border:1px solid #ccc;
    border-radius:6px; padding:.5rem .7rem; background:#fff; }
  .demo-scrollbox p { margin:.4rem 0; font-size:.85rem; line-height:1.4; }
  .demo-scrollbox .demo-scroll-item { padding:.3rem .4rem; border-bottom:1px solid #eee; font-size:.82rem; }

  .demo-inherit-wrap { font-family:"Trebuchet MS", sans-serif; font-size:1rem; color:#7a1fa2;
    border:2px dashed #d9b3ff; padding:1rem; width:300px; }
  .demo-inherit-wrap .demo-inherit-mid { font-size:1.15em; border-left:3px solid currentColor; padding-left:.8rem; }
  .demo-inherit-wrap .demo-inherit-inner { font-weight:bold; }
  .demo-inherit-wrap .demo-inherit-inner small { font-weight:normal; opacity:.7; }

  .demo-floaty { position:relative; width:260px; height:120px; background:#fffbe6;
    border:1px solid #f0d97a; border-radius:8px; overflow:hidden; }
  .demo-floaty__badge { position:absolute; top:8px; right:8px; background:#f5a623; color:#fff;
    font-size:.7rem; padding:.15rem .5rem; border-radius:999px; }
  .demo-floaty__pill { position:absolute; bottom:10px; left:10px; background:#2c7dd8; color:#fff;
    font-size:.75rem; padding:.3rem .7rem; border-radius:999px; }
</style>

<div class="demo-card-list">
  <div class="demo-card" id="demo-profile-card">
    <div class="demo-card__banner">
      <div class="demo-card__avatar">
        <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
          <circle cx="24" cy="24" r="24" fill="#4a69bd"/>
          <circle cx="24" cy="19" r="9" fill="#dfe6fd"/>
          <path d="M6 44c2-10 12-16 18-16s16 6 18 16" fill="#dfe6fd"/>
        </svg>
      </div>
    </div>
    <div class="demo-card__body">
      <h3>Alex Rivera</h3>
      <div class="demo-role">Senior mockup enthusiast</div>
      <div class="demo-card__meta"><span>Admin</span><span>Active</span><span>2 teams</span></div>
    </div>
    <div class="demo-card__footer">
      <button class="demo-card-msg">Message</button>
      <button class="demo-card-view">View profile</button>
    </div>
  </div>

  <div class="demo-tree">
    <div><strong>Project /</strong></div>
    <ul>
      <li>📁 src
        <ul>
          <li>📁 components
            <ul>
              <li class="demo-leaf" id="demo-tree-leaf-1">📄 Button.tsx</li>
              <li class="demo-leaf" id="demo-tree-leaf-2">📄 Modal.tsx</li>
            </ul>
          </li>
          <li class="demo-leaf" id="demo-tree-leaf-3">📄 index.ts</li>
        </ul>
      </li>
      <li class="demo-leaf" id="demo-tree-leaf-4">📄 package.json</li>
    </ul>
  </div>

  <div class="demo-scrollbox" id="demo-scrollbox">
    <p>Scrollable log — selecting an item near the bottom should still position the bar/card
    sensibly relative to the viewport, not the scrolled-away content.</p>
    <div class="demo-scroll-item">01. Build started</div>
    <div class="demo-scroll-item">02. Linting passed</div>
    <div class="demo-scroll-item">03. Tests: 42 passed</div>
    <div class="demo-scroll-item" id="demo-scroll-item-warn">04. Warning: unused import</div>
    <div class="demo-scroll-item">05. Bundling assets</div>
    <div class="demo-scroll-item">06. Optimizing images</div>
    <div class="demo-scroll-item">07. Build finished</div>
    <div class="demo-scroll-item" id="demo-scroll-item-last">08. Deployed to staging</div>
  </div>
</div>

<h3 style="margin-top:2rem;">Inherited typography/color (nested, no own styling on inner spans)</h3>
<div class="demo-inherit-wrap" id="demo-inherit-outer">
  Outer text sets font/color for everyone below.
  <div class="demo-inherit-mid" id="demo-inherit-mid">
    Mid level bumps size and adds a colored rule, still inherits the purple.
    <div class="demo-inherit-inner" id="demo-inherit-inner">
      Inner level goes bold, <small id="demo-inherit-small">and this small tag dims it</small> —
      note this element has no id-based selector shortcut once you strip the id, forcing the
      framework's nth-of-type fallback path.
    </div>
  </div>
</div>

<h3 style="margin-top:2rem;">Absolutely-positioned overlays inside a clipped box</h3>
<div class="demo-floaty" id="demo-floaty">
  Base content sits here, partly covered by its own badge/pill.
  <span class="demo-floaty__badge" id="demo-floaty-badge">NEW</span>
  <span class="demo-floaty__pill" id="demo-floaty-pill">v2.3</span>
</div>

<h3 style="margin-top:2rem;">Draggable, animated, visually complex widget</h3>
<p>Drag it anywhere on the page by its header, while it keeps a looping gradient/pulse
animation — checks that a note's robust selector, badge position, and open card survive the
element moving to arbitrary coordinates, and that dragging itself doesn't get hijacked by the
framework's own click/selection handling.</p>

<style>
  @keyframes demo-drag-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(124,58,237,.45), 0 10px 24px rgba(0,0,0,.18); }
    50% { box-shadow: 0 0 0 10px rgba(124,58,237,0), 0 10px 24px rgba(0,0,0,.18); }
  }
  @keyframes demo-drag-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  #demo-draggable { position: absolute; top: 480px; left: 40px; width: 260px;
    border-radius: 12px; overflow: hidden; background: #fff; z-index: 50;
    animation: demo-drag-pulse 2.4s ease-in-out infinite;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  #demo-draggable.demo-dragging { animation-play-state: paused; cursor: grabbing !important; }
  #demo-draggable .demo-drag-header { cursor: grab; padding: .6rem .8rem; color: #fff;
    font-size: .82rem; font-weight: 700; display: flex; align-items: center; gap: .4rem;
    background: linear-gradient(120deg, #7c3aed, #db2777, #2563eb, #7c3aed);
    background-size: 300% 300%; animation: demo-drag-gradient 6s ease infinite; }
  #demo-draggable .demo-drag-header .demo-drag-dot { width: 8px; height: 8px; border-radius: 50%;
    background: rgba(255,255,255,.85); }
  #demo-draggable .demo-drag-body { padding: .8rem; font-size: .8rem; color: #333; }
  #demo-draggable .demo-drag-row { display: flex; align-items: center; gap: .6rem; margin-bottom: .6rem; }
  #demo-draggable .demo-drag-avatar { width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0; }
  #demo-draggable .demo-drag-bar { height: 6px; border-radius: 999px; background: #eee; overflow: hidden; }
  #demo-draggable .demo-drag-bar__fill { height: 100%; width: 68%; border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #db2777); }
  #demo-draggable .demo-drag-tags { display: flex; gap: .35rem; margin-top: .6rem; flex-wrap: wrap; }
  #demo-draggable .demo-drag-tags span { font-size: .68rem; background: #f2eaff; color: #6b21a8;
    padding: .15rem .5rem; border-radius: 999px; }
</style>

<div id="demo-draggable">
  <div class="demo-drag-header" id="demo-drag-header">
    <span class="demo-drag-dot"></span> Drag me around
  </div>
  <div class="demo-drag-body">
    <div class="demo-drag-row">
      <svg class="demo-drag-avatar" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
        <circle cx="18" cy="18" r="18" fill="#7c3aed"/>
        <circle cx="18" cy="14" r="7" fill="#f2eaff"/>
        <path d="M4 33c1.5-7.5 9-12 14-12s12.5 4.5 14 12" fill="#f2eaff"/>
      </svg>
      <div>
        <div style="font-weight:700;">Live deploy</div>
        <div style="color:#888; font-size:.72rem;">Building — 68% complete</div>
      </div>
    </div>
    <div class="demo-drag-bar"><div class="demo-drag-bar__fill"></div></div>
    <div class="demo-drag-tags">
      <span>staging</span><span>auto-retry</span><span id="demo-drag-tag-note">no-cache</span>
    </div>
  </div>
</div>

<script>
(function () {
  var el = document.getElementById("demo-draggable");
  var header = document.getElementById("demo-drag-header");
  var dragging = false, offsetX = 0, offsetY = 0;

  header.addEventListener("mousedown", function (ev) {
    dragging = true;
    el.classList.add("demo-dragging");
    var r = el.getBoundingClientRect();
    offsetX = ev.clientX - r.left;
    offsetY = ev.clientY - r.top;
    ev.preventDefault();
  });

  document.addEventListener("mousemove", function (ev) {
    if (!dragging) return;
    el.style.left = (ev.clientX - offsetX + window.scrollX) + "px";
    el.style.top = (ev.clientY - offsetY + window.scrollY) + "px";
  });

  document.addEventListener("mouseup", function () {
    if (!dragging) return;
    dragging = false;
    el.classList.remove("demo-dragging");
  });
})();
</script>
"""

sandbox = """<!--
  SANDBOX FILE — not part of the skill's contract, never read by pv-internal-mockups-html.
  The <style id="mnoteqz7k-styles"> and <script id="mnoteqz7k-runtime"> blocks below are injected
  verbatim from mockup-annotations.html (the real asset) — never hand-edited here. If you
  change the framework, edit mockup-annotations.html and re-run this builder script (or restore
  from mockup-annotations.sandbox.golden.html, the clean untouched copy, and re-run it there).
  This body exists only to manually exercise the framework against a wide variety of
  interactive widgets and DOM complexity, in both eye-on and eye-off modes.
-->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mnoteqz7k-framework sandbox</title>
<!-- mnoteqz7k-framework v1 -->
""" + style_block + """
</head>
<body>

<script type="application/json" id="mnoteqz7k-data">[]</script>

""" + runtime_block + """
""" + demo_body + """
</body>
</html>
"""

open("mockup-annotations.sandbox.html", "w", encoding="utf-8").write(sandbox)
open("mockup-annotations.sandbox.golden.html", "w", encoding="utf-8").write(sandbox)
print("built sandbox + golden, length:", len(sandbox))
