import streamlit as st
import fitz  # PyMuPDF
import difflib
import tempfile
import os


def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def get_differences(prev_text, curr_text):
    prev_lines = prev_text.splitlines()
    curr_lines = curr_text.splitlines()
    diff = difflib.unified_diff(prev_lines, curr_lines, lineterm='', fromfile='Previous PDF', tofile='Current PDF')
    return list(diff)


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

            # Option to download difference
            if st.button("Download Differences as .txt"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w') as f:
                    f.write(diff_output)
                    temp_path = f.name
                with open(temp_path, "rb") as f:
                    st.download_button("Download File", f, file_name="pdf_differences.txt")
                os.unlink(temp_path)
        else:
            st.success("No differences found between the PDFs.")


if __name__ == "__main__":
    main()
