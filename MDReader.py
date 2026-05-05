# MDReader.py — Streamlit 版 Markdown 閱讀器
# 本機執行: streamlit run MDReader.py

import re
import sys
import asyncio
from html import escape

import markdown as md_lib
import streamlit as st

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

st.set_page_config(
    page_title="Markdown Reader",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

THEMES = {
    "dark": {
        "bg": "#0f0e0c",
        "surface": "#1a1916",
        "surface2": "#242320",
        "border": "#2e2c28",
        "accent": "#c9a84c",
        "accent2": "#8b6914",
        "text": "#e8e2d6",
        "text_dim": "#b4ab9e",
        "text_dimmer": "#8b8173",
        "code_bg": "#161514",
        "upload_bg": "#1c1a15",
        "upload_hover_bg": "#1f1d16",
        "h1_color": "#f0e8d6",
        "h2_color": "#ddd4c0",
        "h3_color": "#ccc4b0",
        "p_color": "#cfc8bc",
        "li_color": "#c8c0b0",
        "code_color": "#b8a882",
        "pre_code_color": "#a09878",
        "blockquote_bg": "rgba(201,168,76,0.04)",
        "table_stripe": "rgba(255,255,255,0.02)",
        "panel_shadow": "0 18px 40px rgba(0, 0, 0, 0.18)",
    },
    "light": {
        "bg": "#f5f2ed",
        "surface": "#ffffff",
        "surface2": "#f0ece6",
        "border": "#ddd8d0",
        "accent": "#8b5e1a",
        "accent2": "#a07030",
        "text": "#2a2520",
        "text_dim": "#6a6058",
        "text_dimmer": "#aaa098",
        "code_bg": "#f8f5f0",
        "upload_bg": "#f8f4ef",
        "upload_hover_bg": "#f2ede8",
        "h1_color": "#1e1a14",
        "h2_color": "#2e2a22",
        "h3_color": "#3e3a30",
        "p_color": "#3d3830",
        "li_color": "#4a4438",
        "code_color": "#6b5930",
        "pre_code_color": "#7a6840",
        "blockquote_bg": "rgba(139,94,26,0.06)",
        "table_stripe": "rgba(0,0,0,0.03)",
        "panel_shadow": "0 18px 36px rgba(70, 54, 36, 0.08)",
    },
}


def inject_styles(theme: str, font_size: int = 100) -> None:
    theme_vars = "\n".join(
        f"    --{name.replace('_', '-')}: {value};"
        for name, value in THEMES[theme].items()
    )
    font_size_factor = font_size / 100
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;700&family=JetBrains+Mono:wght@400;500&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap');

:root {{
{theme_vars}
}}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stHeader"], .stAppDeployButton,
.stAppHeader, .stAppToolbar, .stDecoration,
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [class*="css"] {{
    font-family: 'Noto Serif TC', serif;
}}

.stApp,
[data-testid="stAppViewContainer"] {{
    background: var(--bg);
    color: var(--text);
}}

[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0 !important;
}}

.stAppHeader {{
    background: transparent !important;
    height: 0 !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    padding-top: 0 !important;
}}

.stMainBlockContainer {{
    padding-top: 0 !important;
}}

.block-container {{
    max-width: 100% !important;
    padding: 0.35rem 2rem 2rem !important;
}}

div.stButton > button {{
    width: 100%;
    min-height: 42px;
    border-radius: 4px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    transition: all 0.2s ease;
}}

div.stButton > button:hover {{
    border-color: var(--accent2);
    color: var(--accent);
    background: var(--surface);
}}

div.stButton > button:focus:not(:active) {{
    border-color: var(--accent);
    color: var(--accent);
}}

[data-testid="stFileUploader"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.75rem;
    box-shadow: var(--panel-shadow);
}}

[data-testid="stFileUploaderDropzone"] {{
    background: var(--upload-bg);
    border: 1.5px dashed var(--border);
    border-radius: 4px;
    padding: 1rem 0.75rem;
}}

[data-testid="stFileUploaderDropzone"]:hover {{
    background: var(--upload-hover-bg);
    border-color: var(--accent2);
}}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzone"] div {{
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

[data-testid="stFileUploaderFileName"] {{
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

[data-testid="stFileUploader"] button {{
    background: transparent !important;
    border: 1px solid var(--accent2) !important;
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.app-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.25rem 0 1.25rem;
    color: var(--text);
}}

.logo-wrap {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.logo-box {{
    width: 32px;
    height: 32px;
    border: 1.5px solid var(--accent);
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.logo-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}

.file-meta {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: flex-end;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
}}

.panel-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dimmer);
    margin: 0 0 0.6rem;
}}

.panel-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: var(--panel-shadow);
    color: var(--text);
}}

.current-file {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    word-break: break-all;
    line-height: 1.6;
}}

.empty-file {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dim);
    font-style: italic;
}}

.stat-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.6rem;
}}

.stat-box {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.75rem;
    text-align: center;
}}

.stat-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    color: var(--accent);
    font-weight: 500;
}}

.stat-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: var(--text-dimmer);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}}

.reader-shell {{
    width: 100%;
}}

.md-content, .welcome-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    box-shadow: var(--panel-shadow);
    animation: fadeUp 0.3s ease;
}}

.md-content {{
    max-width: min(1180px, 100%);
    margin: 0 auto;
    padding: 56px 84px;
    line-height: 1.95;
    color: var(--text);
}}

.welcome-card {{
    max-width: min(1180px, 100%);
    margin: 0 auto;
    padding: 90px 48px;
    text-align: center;
    color: var(--text);
}}

.welcome-icon {{
    font-size: 52px;
    opacity: 0.15;
    margin-bottom: 1.2rem;
}}

.welcome-title {{
    font-family: 'Crimson Pro', serif;
    font-size: 30px;
    font-weight: 300;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
}}

.welcome-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dimmer);
    letter-spacing: 0.08em;
}}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.md-content {{
    --font-size-factor: {font_size_factor};
}}

.md-content h1, .md-content h2, .md-content h3,
.md-content h4, .md-content h5, .md-content h6 {{
    font-family: 'Noto Serif TC', serif;
    font-weight: 500;
    margin: 1.8em 0 0.7em;
    line-height: 1.4;
    scroll-margin-top: 20px;
}}

.md-content h1 {{
    font-size: calc(2.15em * var(--font-size-factor));
    font-weight: 700;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4em;
    color: var(--h1-color);
    margin-top: 0;
}}

.md-content h2 {{
    font-size: calc(1.48em * var(--font-size-factor));
    color: var(--h2-color);
    position: relative;
    padding-left: 14px;
}}

.md-content h2::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 70%;
    background: var(--accent2);
}}

.md-content h3 {{
    font-size: calc(1.18em * var(--font-size-factor));
    color: var(--h3-color);
}}

.md-content p {{
    margin: 0.9em 0;
    font-family: 'Crimson Pro', serif;
    font-size: calc(1.24em * var(--font-size-factor));
    color: var(--p-color);
    font-weight: 300;
}}

.md-content a {{
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid var(--accent2);
}}

.md-content a:hover {{
    border-color: var(--accent);
}}

.md-content ul, .md-content ol {{
    padding-left: 1.8em;
    margin: 0.8em 0;
}}

.md-content li {{
    margin: 0.35em 0;
    font-family: 'Crimson Pro', serif;
    font-size: calc(1.08em * var(--font-size-factor));
    color: var(--li-color);
}}

.md-content ul li::marker {{
    color: var(--accent2);
}}

.md-content ol li::marker {{
    color: var(--accent2);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
}}

.md-content blockquote {{
    border-left: 2px solid var(--accent2);
    margin: 1.2em 0;
    padding: 12px 20px;
    background: var(--blockquote-bg);
    color: var(--text-dim);
    font-style: italic;
}}

.md-content code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    background: var(--code-bg);
    color: var(--code-color);
    padding: 2px 6px;
    border-radius: 2px;
    border: 1px solid var(--border);
}}

.md-content pre {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 20px 24px;
    overflow-x: auto;
    margin: 1.2em 0;
}}

.md-content pre code {{
    background: none;
    border: none;
    padding: 0;
    font-size: 0.88em;
    color: var(--pre-code-color);
    line-height: 1.7;
}}

.language-powershell::before {{
    content: "PowerShell";
    display: block;
    font-size: 0.75em;
    color: var(--text-dimmer);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.md-content hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 2em 0;
}}

.md-content table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.2em 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.83em;
}}

.md-content th {{
    background: var(--surface2);
    color: var(--accent);
    padding: 10px 14px;
    border: 1px solid var(--border);
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-size: 0.9em;
}}

.md-content td {{
    padding: 9px 14px;
    border: 1px solid var(--border);
    color: var(--text-dim);
}}

.md-content tr:nth-child(even) td {{
    background: var(--table-stripe);
}}

.md-content .toc {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 1.5em;
    display: inline-block;
    min-width: 220px;
}}

.md-content .toc ul {{
    margin: 0;
}}

.md-content .toc a {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    border-bottom: none;
}}

.md-content .toc a:hover {{
    color: var(--accent);
}}

@media (max-width: 900px) {{
    .block-container {{
        padding: 1rem !important;
    }}

    .app-header {{
        flex-direction: column;
        align-items: flex-start;
    }}

    .file-meta {{
        justify-content: flex-start;
    }}

    .md-content, .welcome-card {{
        padding: 32px 22px;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def process_markdown(raw: str, filename: str = "") -> dict:
    html = md_lib.markdown(
        raw,
        extensions=["tables", "fenced_code", "toc", "nl2br"],
        extension_configs={
            "fenced_code": {
                "lang_prefix": "language-"
            }
        }
    )
    return {
        "html": html,
        "filename": filename,
        "words": len(raw.split()),
        "lines": len(raw.splitlines()),
        "headings": len(re.findall(r"^#{1,6}\s", raw, re.MULTILINE)),
        "code_blocks": raw.count("```") // 2,
    }


def initialize_state() -> None:
    defaults = {
        "theme": "dark",
        "panel_expanded": True,
        "raw_markdown": "",
        "filename": "",
        "font_size": 100,
        "last_uploaded_filename": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_header(data: dict | None) -> None:
    meta_html = '<div class="file-meta"><span>尚未載入檔案</span></div>'
    if data:
        meta_html = (
            '<div class="file-meta">'
            f'<span>{escape(data["filename"])}</span>'
            f'<span>{data["words"]:,} 字</span>'
            f'<span>{data["lines"]:,} 行</span>'
            '</div>'
        )

    title_col, font_col, theme_col = st.columns([12, 1, 1], vertical_alignment="center")
    with title_col:
        st.markdown(
            f"""
            <div class="app-header">
              <div class="logo-wrap">
                <div class="logo-box">MD</div>
                <div class="logo-title">Markdown Reader</div>
              </div>
              {meta_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with font_col:
        size_col1, size_col2 = st.columns(2, gap="small")
        with size_col1:
            if st.button("−", key="font_decrease", help="縮小文字", use_container_width=True):
                st.session_state.font_size = max(70, st.session_state.font_size - 10)
                st.rerun()
        with size_col2:
            if st.button("＋", key="font_increase", help="放大文字", use_container_width=True):
                st.session_state.font_size = min(150, st.session_state.font_size + 10)
                st.rerun()
    with theme_col:
        theme_icon = "☀" if st.session_state.theme == "dark" else "☾"
        if st.button(theme_icon, key="theme_toggle", help="切換深淺主題", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()


def render_upload_panel() -> None:
    st.markdown('<div class="panel-title">上傳檔案</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "選取 Markdown 檔案",
        type=["md", "markdown", "txt"],
        label_visibility="collapsed",
        key="markdown_upload",
    )
    if uploaded is not None:
        # 只在上傳新檔案時更新並重新運行
        if uploaded.name != st.session_state.last_uploaded_filename:
            st.session_state.raw_markdown = uploaded.getvalue().decode("utf-8", errors="replace")
            st.session_state.filename = uploaded.name
            st.session_state.last_uploaded_filename = uploaded.name
            st.rerun()


def render_file_info(data: dict | None) -> None:
    current_file = '<div class="empty-file">尚未載入 Markdown 檔案</div>'
    if data:
        current_file = f'<div class="current-file">{escape(data["filename"])}</div>'

    st.markdown(
        f"""
        <div class="panel-card">
          <div class="panel-title">目前檔案</div>
          {current_file}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(data: dict | None) -> None:
    words = f"{data['words']:,}" if data else "0"
    lines = f"{data['lines']:,}" if data else "0"
    headings = str(data["headings"]) if data else "0"
    code_blocks = str(data["code_blocks"]) if data else "0"

    st.markdown(
        f"""
        <div class="panel-card">
          <div class="panel-title">統計</div>
          <div class="stat-grid">
            <div class="stat-box">
              <div class="stat-val">{words}</div>
              <div class="stat-label">字數</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">{lines}</div>
              <div class="stat-label">行數</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">{headings}</div>
              <div class="stat-label">標題</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">{code_blocks}</div>
              <div class="stat-label">程式碼</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_content(data: dict | None) -> None:
    if data:
        st.html(
            f'<div class="reader-shell"><div class="md-content">{data["html"]}</div></div>',
        )
        return

    st.html(
        """
        <div class="reader-shell">
          <div class="welcome-card">
            <div class="welcome-icon">📄</div>
            <div class="welcome-title">選取一個 Markdown 檔案</div>
            <div class="welcome-sub">展開左側 PANEL，上傳 .md 檔案後開始閱讀</div>
          </div>
        </div>
        """,
    )


initialize_state()
inject_styles(st.session_state.theme, st.session_state.font_size)

data = None
if st.session_state.raw_markdown:
    data = process_markdown(st.session_state.raw_markdown, st.session_state.filename)

render_header(data)

if st.session_state.panel_expanded:
    sidebar_col, toggle_col, content_col = st.columns([1.15, 0.22, 4.4], vertical_alignment="top")
    with sidebar_col:
        render_upload_panel()
        render_file_info(data)
        render_stats(data)
    with toggle_col:
        if st.button("◀", key="panel_toggle_open", help="縮合左側 panel", use_container_width=True):
            st.session_state.panel_expanded = False
            st.rerun()
    with content_col:
        render_content(data)
else:
    toggle_col, content_col = st.columns([0.22, 5.4], vertical_alignment="top")
    with toggle_col:
        if st.button("▶", key="panel_toggle_closed", help="展開左側 panel", use_container_width=True):
            st.session_state.panel_expanded = True
            st.rerun()
    with content_col:
        render_content(data)
