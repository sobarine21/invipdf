import streamlit as st
import pdfplumber
import difflib
import tempfile
import os

def extract_text_from_pdf(pdf_file):
    text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def get_differences(text1, text2):
    diff = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        lineterm='',
        fromfile='Previous PDF',
        tofile='Current PDF'
    )
    return "\n".join(diff)

def highlight_differences(diff_text):
    highlighted = []
    for line in diff_text.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            highlighted.append(f"<span style='background-color: #c6f6d5;'>{line}</span>")
        elif line.startswith('-') and not line.startswith('---'):
            highlighted.append(f"<span style='background-color: #fed7d7;'>{line}</span>")
        elif line.startswith('@@'):
            highlighted.append(f"<span style='color: #805ad5;'>{line}</span>")
        else:
            highlighted.append(line)
    return "<br>".join(highlighted)

st.set_page_config(page_title="PDF Difference Tracker", layout="wide")

st.title("PDF Comparison / Difference Tracker Tool")

st.write("""
Upload your previous and current PDF documents below. The tool will extract text from both and highlight the differences.
""")

col1, col2 = st.columns(2)

with col1:
    prev_pdf = st.file_uploader("Upload Previous PDF", type=["pdf"], key="prev_pdf")
with col2:
    curr_pdf = st.file_uploader("Upload Current PDF", type=["pdf"], key="curr_pdf")

if prev_pdf and curr_pdf:
    with st.spinner('Extracting text from PDFs...'):
        prev_text = extract_text_from_pdf(prev_pdf)
        curr_text = extract_text_from_pdf(curr_pdf)

    diff_text = get_differences(prev_text, curr_text)
    st.subheader("Differences")
    if diff_text.strip() == "":
        st.success("No differences found between the two PDFs!")
    else:
        st.markdown(highlight_differences(diff_text), unsafe_allow_html=True)

    with st.expander("Show Previous PDF Text"):
        st.text(prev_text[:3000] + ("..." if len(prev_text) > 3000 else ""))
    with st.expander("Show Current PDF Text"):
        st.text(curr_text[:3000] + ("..." if len(curr_text) > 3000 else ""))
else:
    st.info("Please upload both the previous and current PDF files above to compare.")

st.markdown("""
---
**How it works:**  
- This tool uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract text from PDFs.
- It then uses Python's [difflib](https://docs.python.org/3/library/difflib.html) to compute and display the differences.
- Added lines are highlighted in green, removed lines in red.
""")
