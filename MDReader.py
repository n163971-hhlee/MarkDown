# MDReader.py — Streamlit 版 Markdown 閱讀器
# 本機執行: streamlit run MDReader.py
# 發布到 streamlit.app 需附 requirements.txt (見下方)
#
# requirements.txt 內容:
#   streamlit
#   markdown
#   pygments

import re
import markdown as md_lib
import streamlit as st

st.set_page_config(
    page_title="Markdown Reader",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;700&family=JetBrains+Mono:wght@400;500&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap');

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.stAppDeployButton { display: none !important; }

[data-testid="stSidebar"] {
    background: #1a1916 !important;
    border-right: 1px solid #2e2c28 !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

.panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a4540;
    padding: 8px 0 6px 0;
    border-bottom: 1px solid #2e2c28;
    margin-bottom: 10px;
}

.current-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #c9a84c;
    word-break: break-all;
    line-height: 1.5;
    padding: 6px 0;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 4px;
}
.stat-box {
    background: #161514;
    border: 1px solid #2e2c28;
    padding: 10px;
    text-align: center;
    border-radius: 2px;
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    color: #c9a84c;
    font-weight: 500;
}
.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #4a4540;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 3px;
}

.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

.md-content {
    background: #1a1916;
    border: 1px solid #2e2c28;
    border-radius: 4px;
    padding: 52px 72px;
    line-height: 1.9;
    max-width: 860px;
    margin: 0 auto;
    animation: fadeUp 0.3s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.md-content h1, .md-content h2, .md-content h3,
.md-content h4, .md-content h5, .md-content h6 {
    font-family: 'Noto Serif TC', serif;
    font-weight: 500;
    margin: 1.8em 0 0.7em;
    line-height: 1.4;
    scroll-margin-top: 20px;
}
.md-content h1 {
    font-size: 2em; font-weight: 700;
    border-bottom: 1px solid #2e2c28;
    padding-bottom: 0.4em;
    color: #f0e8d6; margin-top: 0;
}
.md-content h2 {
    font-size: 1.4em; color: #ddd4c0;
    position: relative; padding-left: 14px;
}
.md-content h2::before {
    content: '';
    position: absolute; left: 0; top: 50%;
    transform: translateY(-50%);
    width: 3px; height: 70%;
    background: #8b6914;
}
.md-content h3 { font-size: 1.15em; color: #ccc4b0; }
.md-content p {
    margin: 0.9em 0;
    font-family: 'Crimson Pro', serif;
    font-size: 1.18em; color: #cfc8bc; font-weight: 300;
}
.md-content a { color: #c9a84c; text-decoration: none; border-bottom: 1px solid #8b6914; }
.md-content a:hover { border-color: #c9a84c; }
.md-content ul, .md-content ol { padding-left: 1.8em; margin: 0.8em 0; }
.md-content li { margin: 0.35em 0; font-family: 'Crimson Pro', serif; font-size: 1.05em; color: #c8c0b0; }
.md-content ul li::marker { color: #8b6914; }
.md-content ol li::marker { color: #8b6914; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }
.md-content blockquote {
    border-left: 2px solid #8b6914;
    margin: 1.2em 0; padding: 12px 20px;
    background: rgba(201,168,76,0.04);
    color: #8a8070; font-style: italic;
}
.md-content code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    background: #161514;
    color: #b8a882; padding: 2px 6px;
    border-radius: 2px; border: 1px solid #2e2c28;
}
.md-content pre {
    background: #161514;
    border: 1px solid #2e2c28;
    border-radius: 4px; padding: 20px 24px;
    overflow-x: auto; margin: 1.2em 0;
}
.md-content pre code {
    background: none; border: none; padding: 0;
    font-size: 0.85em; color: #a09878; line-height: 1.7;
}
.md-content hr { border: none; border-top: 1px solid #2e2c28; margin: 2em 0; }
.md-content table {
    width: 100%; border-collapse: collapse;
    margin: 1.2em 0;
    font-family: 'JetBrains Mono', monospace; font-size: 0.83em;
}
.md-content th {
    background: #242320; color: #c9a84c;
    padding: 10px 14px; border: 1px solid #2e2c28;
    font-weight: 500; letter-spacing: 0.05em;
    text-transform: uppercase; font-size: 0.9em;
}
.md-content td { padding: 9px 14px; border: 1px solid #2e2c28; color: #8a8070; }
.md-content tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

.md-content .toc {
    background: #161514;
    border: 1px solid #2e2c28;
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 1.5em;
    display: inline-block;
    min-width: 200px;
}
.md-content .toc ul { margin: 0; }
.md-content .toc a {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em; border-bottom: none;
}
.md-content .toc a:hover { color: #c9a84c; }
</style>
""", unsafe_allow_html=True)


def process_markdown(raw: str, filename: str = "") -> dict:
    html = md_lib.markdown(
        raw,
        extensions=["tables", "fenced_code", "codehilite", "toc", "nl2br"],
    )
    return {
        "html": html,
        "filename": filename,
        "words": len(raw.split()),
        "lines": len(raw.splitlines()),
        "headings": len(re.findall(r"^#{1,6}\s", raw, re.MULTILINE)),
        "code_blocks": raw.count("```") // 2,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="panel-title">上傳檔案</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "選取 Markdown 檔案",
        type=["md", "markdown", "txt"],
        label_visibility="collapsed",
    )

# ── Main ──────────────────────────────────────────────────────────────────────
if uploaded is not None:
    raw = uploaded.read().decode("utf-8", errors="replace")
    data = process_markdown(raw, uploaded.name)

    with st.sidebar:
        st.markdown(
            '<div class="panel-title" style="margin-top:16px">目前檔案</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="current-file">{data["filename"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel-title" style="margin-top:16px">統計</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"""
        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-val">{data['words']:,}</div>
            <div class="stat-label">字數</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{data['lines']:,}</div>
            <div class="stat-label">行數</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{data['headings']}</div>
            <div class="stat-label">標題</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{data['code_blocks']}</div>
            <div class="stat-label">程式碼</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="md-content">{data["html"]}</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown("""
    <div style="text-align:center; padding:80px 40px;">
      <div style="font-size:48px; opacity:0.15; margin-bottom:20px">📄</div>
      <div style="font-family:'Crimson Pro',serif; font-size:26px; font-weight:300;
                  color:#6a6058; margin-bottom:8px">
        選取一個 Markdown 檔案
      </div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
                  color:#4a4540; letter-spacing:0.08em">
        從左側上傳 .md 檔案開始閱讀
      </div>
    </div>
    """, unsafe_allow_html=True)
