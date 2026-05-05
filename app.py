from flask import Flask, render_template_string, request, jsonify
import markdown
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="zh-TW" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Markdown Reader</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;700&family=JetBrains+Mono:wght@400;500&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap');

  /* Dark theme (default) */
  :root, [data-theme="dark"] {
    --bg: #0f0e0c;
    --surface: #1a1916;
    --surface2: #242320;
    --border: #2e2c28;
    --accent: #c9a84c;
    --accent2: #8b6914;
    --text: #e8e2d6;
    --text-dim: #8a8070;
    --text-dimmer: #4a4540;
    --code-bg: #161514;
    --upload-bg: #1c1a15;
    --upload-hover-bg: #1f1d16;
    --h1-color: #f0e8d6;
    --h2-color: #ddd4c0;
    --h3-color: #ccc4b0;
    --p-color: #cfc8bc;
    --li-color: #c8c0b0;
    --code-color: #b8a882;
    --pre-code-color: #a09878;
    --blockquote-bg: rgba(201,168,76,0.04);
    --table-stripe: rgba(255,255,255,0.02);
    --toggle-icon: "☀";
  }

  /* Light theme */
  [data-theme="light"] {
    --bg: #f5f2ed;
    --surface: #ffffff;
    --surface2: #f0ece6;
    --border: #ddd8d0;
    --accent: #8b5e1a;
    --accent2: #a07030;
    --text: #2a2520;
    --text-dim: #6a6058;
    --text-dimmer: #aaa098;
    --code-bg: #f8f5f0;
    --upload-bg: #f8f4ef;
    --upload-hover-bg: #f2ede8;
    --h1-color: #1e1a14;
    --h2-color: #2e2a22;
    --h3-color: #3e3a30;
    --p-color: #3d3830;
    --li-color: #4a4438;
    --code-color: #6b5930;
    --pre-code-color: #7a6840;
    --blockquote-bg: rgba(139,94,26,0.06);
    --table-stripe: rgba(0,0,0,0.03);
    --toggle-icon: "☾";
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Noto Serif TC', serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    transition: background 0.25s, color 0.25s;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky; top: 0; z-index: 100;
    transition: background 0.25s, border-color 0.25s;
  }

  .logo {
    display: flex; align-items: center; gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px; color: var(--accent);
    letter-spacing: 0.1em; text-transform: uppercase;
  }

  .logo-box {
    width: 28px; height: 28px;
    border: 1.5px solid var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px;
  }

  .file-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: var(--text-dim);
    display: flex; gap: 20px; align-items: center;
  }

  .theme-toggle {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-dim);
    font-size: 14px;
    width: 30px; height: 30px;
    border-radius: 3px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .theme-toggle:hover {
    border-color: var(--accent2);
    color: var(--accent);
  }

  .sidebar-toggle {
    flex-shrink: 0;
    align-self: flex-start;
    position: sticky;
    top: 88px;
    width: 16px;
    height: 64px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 0 4px 4px 0;
    color: var(--text-dimmer);
    cursor: pointer;
    font-size: 10px;
    display: flex; align-items: center; justify-content: center;
    transition: color 0.2s, background 0.2s, border-color 0.2s;
    margin-right: 24px;
    padding: 0;
  }

  .sidebar-toggle:hover {
    background: var(--surface);
    border-color: var(--accent2);
    color: var(--accent);
  }

  main {
    flex: 1;
    display: flex;
    max-width: 1500px;
    width: 100%;
    margin: 0 auto;
    padding: 32px 40px;
    gap: 0;
  }

  /* Sidebar */
  aside {
    width: 260px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
    transition: width 0.3s cubic-bezier(0.4,0,0.2,1),
                opacity 0.2s ease;
  }

  aside.collapsed {
    width: 0;
    opacity: 0;
    pointer-events: none;
  }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
    transition: background 0.25s, border-color 0.25s;
  }

  .panel-title {
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dimmer);
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
  }

  .panel-body { padding: 14px; }

  /* Upload area */
  .upload-area {
    border: 1.5px dashed var(--border);
    border-radius: 3px;
    padding: 24px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    background: var(--upload-bg);
    position: relative;
  }

  .upload-area:hover { border-color: var(--accent2); background: var(--upload-hover-bg); }
  .upload-area.drag-over { border-color: var(--accent); border-style: solid; }

  .upload-icon { font-size: 28px; opacity: 0.4; margin-bottom: 10px; }
  .upload-hint {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: var(--text-dimmer);
    line-height: 1.6;
  }

  #file-input { display: none; }

  .btn {
    width: 100%;
    padding: 8px;
    margin-top: 10px;
    background: transparent;
    border: 1px solid var(--accent2);
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn:hover { background: rgba(201,168,76,0.08); border-color: var(--accent); }

  /* File path input */
  .path-group { display: flex; flex-direction: column; gap: 8px; }

  .path-input {
    width: 100%;
    padding: 8px 10px;
    background: var(--code-bg);
    border: 1px solid var(--border);
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    border-radius: 2px;
    outline: none;
    transition: border-color 0.2s, background 0.25s;
  }

  .path-input:focus { border-color: var(--accent2); }
  .path-input::placeholder { color: var(--text-dimmer); }

  /* Stats */
  .stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .stat {
    background: var(--code-bg);
    border: 1px solid var(--border);
    padding: 10px;
    text-align: center;
  }

  .stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    color: var(--accent);
    font-weight: 500;
  }

  .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: var(--text-dimmer);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 3px;
  }

  .current-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    word-break: break-all;
    line-height: 1.5;
  }

  .no-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dimmer);
    font-style: italic;
  }

  /* Document */
  .doc-area {
    flex: 1;
    min-width: 0;
  }

  #welcome {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 80px 40px;
    text-align: center;
  }

  .welcome-icon { font-size: 48px; opacity: 0.2; margin-bottom: 20px; }

  .welcome-title {
    font-family: 'Crimson Pro', serif;
    font-size: 26px;
    font-weight: 300;
    color: var(--text-dim);
    margin-bottom: 8px;
  }

  .welcome-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dimmer);
    letter-spacing: 0.08em;
  }

  #doc-header {
    display: none;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }

  .doc-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent);
  }

  #content-box {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 52px 72px;
    line-height: 1.9;
    animation: fadeUp 0.3s ease;
    transition: background 0.25s, border-color 0.25s;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Markdown styles */
  #content-box h1, #content-box h2, #content-box h3,
  #content-box h4, #content-box h5, #content-box h6 {
    font-family: 'Noto Serif TC', serif;
    font-weight: 500;
    margin: 1.8em 0 0.7em;
    line-height: 1.4;
    scroll-margin-top: 80px;
  }

  #content-box h1 {
    font-size: 2em; font-weight: 700;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4em;
    color: var(--h1-color); margin-top: 0;
  }

  #content-box h2 {
    font-size: 1.4em; color: var(--h2-color);
    position: relative; padding-left: 14px;
  }

  #content-box h2::before {
    content: '';
    position: absolute; left: 0; top: 50%;
    transform: translateY(-50%);
    width: 3px; height: 70%;
    background: var(--accent2);
  }

  #content-box h3 { font-size: 1.15em; color: var(--h3-color); }

  #content-box p {
    margin: 0.9em 0;
    font-family: 'Crimson Pro', serif;
    font-size: 1.18em; color: var(--p-color); font-weight: 300;
  }

  #content-box a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent2); }
  #content-box a:hover { border-color: var(--accent); }

  #content-box ul, #content-box ol { padding-left: 1.8em; margin: 0.8em 0; }
  #content-box li { margin: 0.35em 0; font-family: 'Crimson Pro', serif; font-size: 1.05em; color: var(--li-color); }
  #content-box ul li::marker { color: var(--accent2); }
  #content-box ol li::marker { color: var(--accent2); font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }

  #content-box blockquote {
    border-left: 2px solid var(--accent2);
    margin: 1.2em 0; padding: 12px 20px;
    background: var(--blockquote-bg);
    color: var(--text-dim); font-style: italic;
  }

  #content-box code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    background: var(--code-bg);
    color: var(--code-color); padding: 2px 6px;
    border-radius: 2px; border: 1px solid var(--border);
  }

  #content-box pre {
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 4px; padding: 20px 24px;
    overflow-x: auto; margin: 1.2em 0;
  }

  #content-box pre code {
    background: none; border: none; padding: 0;
    font-size: 0.85em; color: var(--pre-code-color); line-height: 1.7;
  }

  #content-box hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }

  #content-box table { width: 100%; border-collapse: collapse; margin: 1.2em 0; font-family: 'JetBrains Mono', monospace; font-size: 0.83em; }
  #content-box th { background: var(--surface2); color: var(--accent); padding: 10px 14px; border: 1px solid var(--border); font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.9em; }
  #content-box td { padding: 9px 14px; border: 1px solid var(--border); color: var(--text-dim); }
  #content-box tr:nth-child(even) td { background: var(--table-stripe); }

  .error-msg {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: #c06060;
    padding: 10px;
    background: rgba(192,96,96,0.08);
    border: 1px solid rgba(192,96,96,0.2);
    border-radius: 3px;
    margin-top: 8px;
    display: none;
  }

  footer {
    text-align: center; padding: 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: var(--text-dimmer);
    letter-spacing: 0.08em;
    border-top: 1px solid var(--border);
  }

  @media (max-width: 700px) {
    main { flex-direction: column; }
    aside { width: 100%; }
    #content-box { padding: 28px 20px; }
  }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-box">MD</div>
    Markdown Reader
  </div>
  <div class="file-meta">
    <div id="header-meta" style="display:none; gap:20px; display:none; align-items:center">
      <span id="meta-name">—</span>
      <span id="meta-words">0 字</span>
      <span id="meta-lines">0 行</span>
    </div>
    <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="切換深色／淡色">
      <span id="theme-icon">☀</span>
    </button>
  </div>
</header>

<main>
  <!-- Sidebar -->
  <aside id="sidebar">

    <!-- Upload Panel -->
    <div class="panel">
      <div class="panel-title">上傳檔案</div>
      <div class="panel-body">
        <div class="upload-area" id="drop-area" onclick="document.getElementById('file-input').click()">
          <div class="upload-icon">⌘</div>
          <div class="upload-hint">拖曳 .md 檔案<br>或點擊選取</div>
          <input type="file" id="file-input" accept=".md,.markdown,.txt">
        </div>
        <button class="btn" onclick="document.getElementById('file-input').click()">選取檔案</button>
      </div>
    </div>

    <!-- Server Path Panel -->
    <div class="panel">
      <div class="panel-title">伺服器路徑</div>
      <div class="panel-body">
        <div class="path-group">
          <input type="text" class="path-input" id="path-input" placeholder="輸入檔案路徑 e.g. /home/user/README.md">
          <button class="btn" onclick="loadFromPath()">載入路徑</button>
          <div class="error-msg" id="path-error"></div>
        </div>
      </div>
    </div>

    <!-- Current File Panel -->
    <div class="panel">
      <div class="panel-title">目前檔案</div>
      <div class="panel-body">
        <div class="no-file" id="no-file-msg">尚未載入檔案</div>
        <div class="current-file" id="current-file" style="display:none"></div>
      </div>
    </div>

    <!-- Stats Panel -->
    <div class="panel" id="stats-panel" style="display:none">
      <div class="panel-title">統計</div>
      <div class="panel-body">
        <div class="stat-grid">
          <div class="stat">
            <div class="stat-val" id="stat-words">0</div>
            <div class="stat-label">字數</div>
          </div>
          <div class="stat">
            <div class="stat-val" id="stat-lines">0</div>
            <div class="stat-label">行數</div>
          </div>
          <div class="stat">
            <div class="stat-val" id="stat-h">0</div>
            <div class="stat-label">標題</div>
          </div>
          <div class="stat">
            <div class="stat-val" id="stat-code">0</div>
            <div class="stat-label">程式碼</div>
          </div>
        </div>
      </div>
    </div>

  </aside>
  <button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" title="收合／展開側欄">
    <span id="sidebar-toggle-icon">◀</span>
  </button>

  <!-- Document Area -->
  <div class="doc-area">
    <div id="welcome">
      <div class="welcome-icon">📄</div>
      <div class="welcome-title">選取一個 Markdown 檔案</div>
      <div class="welcome-sub">支援拖曳上傳 · 點選選取 · 輸入伺服器路徑</div>
    </div>

    <div id="doc-header">
      <span class="doc-name" id="doc-name-label"></span>
    </div>

    <div id="content-box"></div>
  </div>
</main>

<footer>MARKDOWN READER &nbsp;·&nbsp; PYTHON FLASK + MARKDOWN</footer>

<script>
  // Theme
  (function() {
    const saved = localStorage.getItem('md-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    document.getElementById('theme-icon').textContent = saved === 'dark' ? '☀' : '☾';
  })();

  // Sidebar collapse
  (function() {
    if (localStorage.getItem('md-sidebar') === 'collapsed') {
      document.getElementById('sidebar').classList.add('collapsed');
      document.getElementById('sidebar-toggle-icon').textContent = '▶';
    }
  })();

  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('sidebar-toggle-icon');
    const collapsed = sidebar.classList.toggle('collapsed');
    icon.textContent = collapsed ? '▶' : '◀';
    localStorage.setItem('md-sidebar', collapsed ? 'collapsed' : 'open');
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    document.getElementById('theme-icon').textContent = next === 'dark' ? '☀' : '☾';
    localStorage.setItem('md-theme', next);
  }

  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('file-input');

  // Drag & drop
  dropArea.addEventListener('dragover', e => { e.preventDefault(); dropArea.classList.add('drag-over'); });
  dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over'));
  dropArea.addEventListener('drop', e => {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) uploadFile(fileInput.files[0]);
  });

  async function uploadFile(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch('/upload', { method: 'POST', body: form });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    renderDoc(data);
  }

  async function loadFromPath() {
    const path = document.getElementById('path-input').value.trim();
    const errEl = document.getElementById('path-error');
    errEl.style.display = 'none';
    if (!path) return;

    const res = await fetch('/load-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path })
    });
    const data = await res.json();
    if (data.error) {
      errEl.textContent = data.error;
      errEl.style.display = 'block';
      return;
    }
    renderDoc(data);
  }

  function renderDoc(data) {
    // Content
    document.getElementById('welcome').style.display = 'none';
    document.getElementById('doc-header').style.display = 'flex';
    const box = document.getElementById('content-box');
    box.style.display = 'block';
    box.innerHTML = data.html;

    // Labels
    document.getElementById('doc-name-label').textContent = data.filename;
    document.getElementById('current-file').textContent = data.filename;
    document.getElementById('current-file').style.display = 'block';
    document.getElementById('no-file-msg').style.display = 'none';

    // Header meta
    document.getElementById('header-meta').style.display = 'flex';
    document.getElementById('meta-name').textContent = data.filename;
    document.getElementById('meta-words').textContent = data.words.toLocaleString() + ' 字';
    document.getElementById('meta-lines').textContent = data.lines.toLocaleString() + ' 行';

    // Stats
    document.getElementById('stats-panel').style.display = 'block';
    document.getElementById('stat-words').textContent = data.words.toLocaleString();
    document.getElementById('stat-lines').textContent = data.lines.toLocaleString();
    document.getElementById('stat-h').textContent = data.headings;
    document.getElementById('stat-code').textContent = data.code_blocks;

    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Re-animate
    box.style.animation = 'none';
    box.offsetHeight;
    box.style.animation = 'fadeUp 0.3s ease';
  }

  // Smooth scroll for anchor links (TOC, headings), accounting for sticky header
  document.getElementById('content-box').addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = decodeURIComponent(a.getAttribute('href').slice(1));
    const target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': '未收到檔案'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未選取檔案'}), 400

    raw = file.read().decode('utf-8', errors='replace')
    return jsonify(process_markdown(raw, file.filename))

@app.route('/load-path', methods=['POST'])
def load_path():
    data = request.get_json()
    path = data.get('path', '').strip()

    if not path:
        return jsonify({'error': '請輸入檔案路徑'}), 400
    if not os.path.exists(path):
        return jsonify({'error': f'找不到檔案：{path}'}), 404
    if not os.path.isfile(path):
        return jsonify({'error': '路徑不是檔案'}), 400

    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            raw = f.read()
    except PermissionError:
        return jsonify({'error': '沒有權限讀取此檔案'}), 403

    filename = os.path.basename(path)
    return jsonify(process_markdown(raw, filename))

def process_markdown(raw, filename):
    import re
    # 取得 markdown 檔案所在目錄
    md_dir = ''
    if filename and os.path.sep in filename:
      md_dir = os.path.dirname(filename)
    # 將 ![xxx](./img.png) 這類路徑自動補上 static 目錄
    def img_repl(match):
      alt, path = match.group(1), match.group(2)
      # 僅處理相對路徑（不以 http/https 開頭，且不是 / 開頭）
      if not path.lower().startswith(('http://', 'https://', '/')):
        # 若 markdown 檔案有子目錄，補上該目錄
        if md_dir:
          static_path = f"/static/{md_dir}/{path}".replace('\\', '/')
        else:
          static_path = f"/static/{path}".replace('\\', '/')
        return f'![{alt}]({static_path})'
      return match.group(0)
    patched_raw = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', img_repl, raw)
    html = markdown.markdown(
      patched_raw,
      extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']
    )
    words = len(raw.split())
    lines = len(raw.splitlines())
    headings = raw.count('\n#')
    code_blocks = raw.count('```')  // 2

    return {
      'html': html,
      'filename': filename,
      'words': words,
      'lines': lines,
      'headings': headings,
      'code_blocks': code_blocks
    }

if __name__ == '__main__':
    print("🚀 Markdown Reader 啟動於 http://localhost:5010")
    app.run(debug=True, port=5010)
