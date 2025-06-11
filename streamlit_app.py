import streamlit as st
import fitz  # PyMuPDF
import difflib
import tempfile
import os
import io


def extract_text_from_pdf(file_bytes):
    """Extracts text from PDF bytes."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def get_differences(prev_text, curr_text):
    """Generates a unified diff between two texts."""
    prev_lines = prev_text.splitlines()
    curr_lines = curr_text.splitlines()
    diff = difflib.unified_diff(prev_lines, curr_lines, lineterm='', fromfile='Previous PDF', tofile='Current PDF')
    return list(diff)


def highlight_differences(curr_pdf_bytes, differences):
    """Highlights additions in the current PDF."""
    doc = fitz.open(stream=curr_pdf_bytes, filetype="pdf")
    added_lines = [line[2:] for line in differences if line.startswith('+') and not line.startswith('+++')]

    for page in doc:
        page_text = page.get_text()
        for line in added_lines:
            if line.strip() == "":
                continue
            rects = page.search_for(line.strip())
            for rect in rects:
                highlight = page.add_highlight_annot(rect)
                highlight.set_colors(stroke=(1, 0, 0))  # Red highlight
                highlight.update()

    output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc.save(output_pdf.name)
    doc.close()
    return output_pdf.name


def main():
    st.set_page_config(page_title="PDF Difference Tracker", layout="wide")
    st.title("📄 PDF Difference Tracker Tool")

    st.markdown("Upload the **Previous PDF** and the **Current PDF** to see the differences highlighted directly in the PDF.")

    col1, col2 = st.columns(2)
    with col1:
        prev_pdf = st.file_uploader("Upload Previous PDF", type=["pdf"], key="prev_pdf")
    with col2:
        curr_pdf = st.file_uploader("Upload Current PDF", type=["pdf"], key="curr_pdf")

    if prev_pdf and curr_pdf:
        # Read the uploaded files once and store in memory
        prev_bytes = prev_pdf.read()
        curr_bytes = curr_pdf.read()

        st.subheader("🔍 Comparing PDFs...")

        prev_text = extract_text_from_pdf(prev_bytes)
        curr_text = extract_text_from_pdf(curr_bytes)

        differences = get_differences(prev_text, curr_text)

        if differences:
            st.markdown("### 🧾 Differences Found:")
            st.code("\n".join(differences), language="diff")

            if st.button("Generate Highlighted PDF"):
                highlighted_pdf_path = highlight_differences(curr_bytes, differences)
                with open(highlighted_pdf_path, "rb") as f:
                    st.download_button("📥 Download Highlighted PDF", f, file_name="highlighted_differences.pdf")
                os.remove(highlighted_pdf_path)
        else:
            st.success("No differences found between the PDFs.")


if __name__ == "__main__":
    main()
