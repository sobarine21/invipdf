import streamlit as st
import pdfplumber
import difflib
import pandas as pd

def extract_text(pdf_file):
    text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def get_diff_lines(prev, curr):
    diff = list(difflib.ndiff(prev.splitlines(), curr.splitlines()))
    table = []
    for line in diff:
        if line.startswith('  '):
            table.append(('','', line[2:]))
        elif line.startswith('- '):
            table.append(('➖','Removed', f"{line[2:]}"))
        elif line.startswith('+ '):
            table.append(('➕','Added', f"{line[2:]}"))
        elif line.startswith('? '):
            continue
    return table

def diff_to_dataframe(diff_table):
    return pd.DataFrame(diff_table, columns=["","Change Type","Text"])

st.set_page_config(page_title="PDF Difference Tracker", layout="centered")
st.title("📄 PDF Comparison / Difference Tracker")
st.write("Upload your previous and current PDF documents below to see the differences.")

prev_pdf = st.file_uploader("Upload Previous PDF", type=["pdf"], key="prev_pdf")
curr_pdf = st.file_uploader("Upload Current PDF", type=["pdf"], key="curr_pdf")

if prev_pdf and curr_pdf:
    with st.spinner("Extracting text and computing differences..."):
        prev_text = extract_text(prev_pdf)
        curr_text = extract_text(curr_pdf)
        diff_table = get_diff_lines(prev_text, curr_text)
        diff_df = diff_to_dataframe(diff_table)

    st.subheader("🪄 Differences between PDFs")
    if (diff_df["Change Type"] == "Added").sum() == 0 and (diff_df["Change Type"] == "Removed").sum() == 0:
        st.success("No differences found between the two PDFs! 🎉")
    else:
        def color_diff(row):
            if row["Change Type"] == "Added":
                return ['background-color: #d4fcdc', '', 'background-color: #d4fcdc']
            elif row["Change Type"] == "Removed":
                return ['background-color: #fde4e1', '', 'background-color: #fde4e1']
            else:
                return ['','', '']
        st.dataframe(
            diff_df.style.apply(color_diff, axis=1),
            use_container_width=True,
            hide_index=True
        )

    with st.expander("Show raw text from Previous PDF"):
        st.text(prev_text[:5000] + ("..." if len(prev_text) > 5000 else ""))
    with st.expander("Show raw text from Current PDF"):
        st.text(curr_text[:5000] + ("..." if len(curr_text) > 5000 else ""))
else:
    st.info("Please upload both PDFs above to compare.")

st.markdown(
"""
---
**How this works:**  
- Text is extracted from both PDFs, then compared line-by-line.
- Green: lines added. Red: lines removed.
- Unchanged lines are shown for context.
- This tool uses [pdfplumber](https://github.com/jsvine/pdfplumber) and [difflib](https://docs.python.org/3/library/difflib.html).
"""
)
