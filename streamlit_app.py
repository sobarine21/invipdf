import streamlit as st
import pdfplumber
import difflib
import html

def extract_text(pdf_file):
    text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def escape(s):
    # Escape text for HTML display
    return html.escape(s, quote=False)

def get_diff_html(prev, curr):
    diff = list(difflib.ndiff(prev.splitlines(), curr.splitlines()))
    html_lines = []
    for line in diff:
        content = escape(line[2:])
        if line.startswith('  '):
            html_lines.append(f"<div style='background-color: #fff;'>{content}</div>")
        elif line.startswith('- '):
            html_lines.append(f"<div style='background-color: #ffecec; color:#c00;'><b>−</b> {content}</div>")
        elif line.startswith('+ '):
            html_lines.append(f"<div style='background-color: #eaffea; color:#008800;'><b>＋</b> {content}</div>")
        # skip '? ' lines (markers)
    return "<div style='font-family:monospace;font-size:1rem;line-height:1.6;'>{}</div>".format("".join(html_lines))

st.set_page_config(page_title="PDF Difference Tracker", layout="wide")
st.title("📄 PDF Comparison / Difference Tracker")

st.write(
    "Upload your previous and current PDF documents below. "
    "The tool will extract text and highlight the differences directly in-place."
)

col1, col2 = st.columns(2)
with col1:
    prev_pdf = st.file_uploader("Upload Previous PDF", type=["pdf"], key="prev_pdf")
with col2:
    curr_pdf = st.file_uploader("Upload Current PDF", type=["pdf"], key="curr_pdf")

if prev_pdf and curr_pdf:
    with st.spinner('Extracting text and computing difference...'):
        prev_text = extract_text(prev_pdf)
        curr_text = extract_text(curr_pdf)
        diff_html = get_diff_html(prev_text, curr_text)

    st.subheader("🔍 Highlighted Differences")
    if not any(x in diff_html for x in ("−", "＋")):
        st.success("No differences found between the two PDFs! 🎉")
    else:
        st.markdown(diff_html, unsafe_allow_html=True)

    with st.expander("Show raw text from Previous PDF"):
        st.text(prev_text[:5000] + ("..." if len(prev_text) > 5000 else ""))
    with st.expander("Show raw text from Current PDF"):
        st.text(curr_text[:5000] + ("..." if len(curr_text) > 5000 else ""))
else:
    st.info("Please upload both PDFs above to compare.")

st.markdown(
"""
---
- <span style='background-color: #ffecec; color: #c00;'>Red highlight</span>: removed lines<br>
- <span style='background-color: #eaffea; color: #008800;'>Green highlight</span>: added lines<br>
- Unchanged lines show on a plain background.<br>
- Powered by [pdfplumber](https://github.com/jsvine/pdfplumber) and Python's [difflib](https://docs.python.org/3/library/difflib.html).
""", unsafe_allow_html=True)
