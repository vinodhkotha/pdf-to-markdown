
import streamlit as st
from markitdown import MarkItDown
from pathlib import Path
import io
import tempfile
from pdfminer.pdfdocument import PDFDocument, PDFPasswordIncorrect
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def validate_pdf(data: bytes) -> None:
    """Raise ValueError unless data parses as a PDF with at least one page (text not required)."""
    invalid = ValueError("The file is not a valid PDF. It may be corrupted or malformed.")
    # PDF spec allows the header anywhere in the first 1024 bytes.
    if b"%PDF-" not in data[:1024]:
        raise invalid
    try:
        document = PDFDocument(PDFParser(io.BytesIO(data)))
        has_page = next(PDFPage.create_pages(document), None) is not None
    except PDFPasswordIncorrect:
        raise ValueError("The PDF is password-protected and cannot be converted.") from None
    except Exception:
        raise invalid from None
    if not has_page:
        raise invalid

# Application configuration
st.set_page_config(
    page_title="PDF to Markdown",
    page_icon="📄",
    layout="centered"
)

# Page heading
st.title("📄 PDF to Markdown Converter")
st.write("Convert your PDF documents into clean Markdown using Microsoft's MarkItDown.")

st.divider()

# Changing this key gives Streamlit a fresh, empty file uploader widget.
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def reset_for_next_pdf() -> None:
    st.session_state.uploader_key += 1
    st.session_state.file_identity = None
    st.session_state.markdown_result = None


# Upload one PDF
uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"],
    accept_multiple_files=False,
    key=f"pdf_uploader_{st.session_state.uploader_key}"
)

# Reset previous result when the uploaded file changes
if uploaded_file is not None:
    MAX_FILE_SIZE = 25 * 1024 * 1024

    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("PDF exceeds the 25 MB limit.")
        st.stop()



    file_identity = (
        uploaded_file.name,
        uploaded_file.size,
        uploaded_file.getvalue()
    )

    if st.session_state.get("file_identity") != file_identity:
        st.session_state.file_identity = file_identity
        st.session_state.markdown_result = None

    st.info(f"Selected file: {uploaded_file.name}")

    if st.button(
        "Convert to Markdown",
        type="primary",
        use_container_width=True
    ):
        try:
            with st.spinner("Converting PDF..."):
                validate_pdf(uploaded_file.getvalue())

                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_path = Path(temp_dir) / "document.pdf"
                    pdf_path.write_bytes(uploaded_file.getvalue())

                    converter = MarkItDown()
                    result = converter.convert(str(pdf_path))

                    st.session_state.markdown_result = (
                        result.markdown
                    )

            st.success("PDF converted successfully!")

        except Exception as error:
            st.session_state.markdown_result = None
            st.error(f"Conversion failed: {error}")

    # Show result only after conversion
    markdown_text = st.session_state.get("markdown_result")
    if markdown_text is not None:

        st.subheader("Markdown Preview")
        st.text_area(
            "Converted Markdown",
            value=markdown_text,
            height=300
        )

        output_filename = (
            Path(uploaded_file.name).stem + ".md"
        )

        st.download_button(
            label="Download Markdown (.md)",
            data=markdown_text,
            file_name=output_filename,
            mime="text/markdown",
            use_container_width=True
        )

        if st.button(
            "Convert Another PDF",
            use_container_width=True
        ):
            reset_for_next_pdf()
            st.rerun()

else:
    st.session_state.file_identity = None
    st.session_state.markdown_result = None

st.divider()
st.caption("Powered by Microsoft MarkItDown")
