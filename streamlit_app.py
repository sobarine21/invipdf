import streamlit as st
import fitz  # PyMuPDF
import difflib
import tempfile
import os

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_differences(prev_text, curr_text):
    """Generates a unified diff between two texts."""
    prev_lines = prev_text.splitlines()
    curr_lines = curr_text.splitlines()
    diff = difflib.unified_diff(prev_lines, curr_lines, lineterm='', fromfile='Previous PDF', tofile='Current PDF')
    return list(diff)

def highlight_differences(prev_pdf, curr_pdf, differences):
    """Highlights the differences in the current PDF."""
    with fitz.open(stream=curr_pdf.read(), filetype="pdf") as doc:
        for page_num, diff in enumerate(differences):
            if diff.startswith('+'):
                page = doc.load_page(page_num)
                rects = page.search_for(diff[2:])
                for rect in rects:
                    highlight = page.add_highlight_annot(rect)
                    highlight.set_colors(stroke=(1, 0, 0))  # Red color
                    highlight.update()
        output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc.save(output_pdf.name)
        return output_pdf.name

def main():
    st.set_page_config(page_title="PDF Difference Tracker", layout="wide")
    st.title("📄 PDF Difference Tracker Tool")

    st.markdown("Upload the **Previous PDF** and the **Current PDF** to see the differences.")

    col1, col2 = st.columns(2)
    with col1:
        prev_pdf = st.file_uploader("Upload Previous PDF", type=["pdf"], key="prev_pdf")
    with col2:
        curr_pdf = st.file_uploader("Upload Current PDF", type=["pdf"], key="curr_pdf")

    if prev_pdf and curr_pdf:
        st.subheader("🔍 Comparing PDFs...")
        prev_text = extract_text_from_pdf(prev_pdf)
        curr_text = extract_text_from_pdf(curr_pdf)

        differences = get_differences(prev_text, curr_text)

        if differences:
            st.markdown("### 🧾 Differences:")
            diff_output = "\n".join(differences)
            st.code(diff_output, language="diff")

            # Option to download the highlighted PDF
            if st.button("Download Highlighted PDF"):
                highlighted_pdf_path = highlight_differences(prev_pdf, curr_pdf, differences)
                with open(highlighted_pdf_path, "rb") as f:
                    st.download_button("Download Highlighted PDF", f, file_name="highlighted_differences.pdf")
                os.remove(highlighted_pdf_path)
        else:
            st.success("No differences found between the PDFs.")

if __name__ == "__main__":
    main()
