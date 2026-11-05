# 📄 PDF to Markdown Converter

## 🌐 Live Application

**Try the application online:**

https://kotha-pdf-to-markdown.streamlit.app

Upload a PDF, convert it to Markdown, preview the result, and download the `.md` file.

**Maximum upload size:** 25 MB.

A lightweight, browser-based application that converts PDF documents into clean Markdown using **Microsoft MarkItDown**.

Built with **Python and Streamlit**, the application runs locally and provides a simple drag-and-drop interface for uploading, converting, previewing, and downloading Markdown files.

## ✨ Features

- **Simple PDF Upload** — Drag and drop or browse to upload one PDF at a time.
- **One-Click Conversion** — Convert PDF documents to Markdown using Microsoft MarkItDown.
- **Markdown Preview** — Review the converted content before downloading.
- **Markdown Download** — Download the result as a `.md` file.
- **Convert Another PDF** — Reset the page after a conversion and convert the next PDF without refreshing the browser.
- **PDF Validation** — Detect malformed, corrupted, and unsupported PDF files.
- **File Size Limit** — Maximum 25 MB per PDF, with no fixed page-count limit.
- **Local Processing** — Run the application on your own computer without a cloud service.
- **Automated Testing** — End-to-end browser tests using Playwright and pytest.

## 🛠 Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.13.1 (tested) |
| Web Framework | Streamlit 1.66.1 |
| PDF Conversion | Microsoft MarkItDown 0.1.9 |
| PDF Validation | pdfminer.six |
| Automated Testing | Playwright + pytest |
| Version Control | Git / GitHub |

## 🏗 Architecture

```text
User (Web Browser)
        |
        v
Streamlit Web Interface
        |
        v
PDF Upload (Maximum 25 MB)
        |
        v
PDF Structure Validation
        |
        v
Microsoft MarkItDown
        |
        v
Markdown Preview
        |
        v
Download .md File
```

The application uses temporary files during conversion. It does not require a database or permanent storage of uploaded PDFs.

## 📁 Project Structure

```text
pdf-to-markdown/
├── app.py                  # Streamlit web application
├── convert.py              # Command-line batch converter
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Testing dependencies
├── pytest.ini              # Test configuration
├── .gitignore
├── README.md
├── input/                  # Local PDF input folder
├── output/                 # Local Markdown output folder
└── tests/
    ├── conftest.py         # Test fixtures
    └── test_app_e2e.py     # Playwright E2E tests
```

## 🚀 Getting Started

### Prerequisites

- Python (tested with 3.13.1)
- Git (optional for local execution)
- A modern web browser

### 1. Clone the repository

Once published on GitHub:

```bash
git clone <YOUR-REPOSITORY-URL>
cd pdf-to-markdown
```

Alternatively, open the project folder directly in VS Code.

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open your browser at:

**http://localhost:8501**

### 5. Convert a PDF

1. Upload a PDF using drag-and-drop or the file browser.
2. Click **Convert to Markdown**.
3. Review the Markdown preview.
4. Click **Download Markdown (.md)**.
5. Click **Convert Another PDF** to clear the current file and result, then upload the next PDF.

Only one PDF can be uploaded at a time.

## 💻 Command-Line Conversion

The project also includes a batch converter for local use.

Place PDF files inside the `input/` directory and run:

```powershell
.\.venv\Scripts\python.exe convert.py
```

Converted Markdown files will appear in the `output/` directory.

## 🧪 Automated Testing

The project uses Python Playwright and pytest for browser-based end-to-end testing.

### Install testing dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

### Run the tests

Start the Streamlit application first, then execute in a separate terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

### Test coverage

| Test ID | Scenario |
|---|---|
| TC-01 | Application loads successfully |
| TC-02 | Valid PDF upload |
| TC-03 | PDF-to-Markdown conversion |
| TC-04 | Markdown file download |
| TC-05 | Unsupported file rejection |
| TC-06 | PDF exceeding 25 MB rejected by Streamlit's upload limit |
| TC-07 | Corrupted PDF validation |
| TC-08 | Upload replacement and result reset |
| TC-09 | "Convert Another PDF" appears only after successful conversion |
| TC-10 | "Convert Another PDF" hidden after failed conversion |
| TC-11 | "Convert Another PDF" resets the page and a second PDF converts |
| TC-12 | Re-uploading the same PDF after reset starts clean |

**Latest reported local execution:** 12 passed, 0 failed, 0 skipped.

Oversized PDFs are rejected in the browser by Streamlit (`maxUploadSize = 25` in `.streamlit/config.toml`). The app's own 25 MB check in `app.py` remains as a second layer of protection.

Test reports and failure artifacts are generated locally and excluded from version control.

## ⚠️ Known Limitations

- Scanned or image-only PDFs may produce incomplete or empty Markdown without OCR.
- Complex layouts, diagrams, and tables may not be preserved accurately.
- Password-protected PDFs requiring a password are not supported.
- Some structurally unusual PDFs may fail validation.
- The application currently runs locally; public hosting is planned.

## 🗺 Roadmap

- [x] PDF-to-Markdown conversion engine
- [x] Streamlit web interface
- [x] Single-PDF upload and download
- [x] PDF validation and file-size restriction
- [x] Playwright automated testing
- [ ] GitHub repository publication
- [ ] GitHub Actions CI pipeline
- [ ] Cloud deployment
- [ ] Improved support for scanned PDFs and OCR
- [ ] Conversion-quality and token-usage analysis

## 🔒 Privacy

When running locally, uploaded PDFs are processed on the local machine. The application does not require an external AI API or cloud-based conversion service.

Avoid uploading confidential documents to any future public deployment without reviewing the hosting environment and appropriate security controls.

## 🙏 Acknowledgments

PDF conversion is powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown), an open-source document conversion utility.

Web interface built with [Streamlit](https://streamlit.io/).

Automated browser testing powered by [Playwright](https://playwright.dev/python/).

---

**Project status:** Version 1.0 — Local application tested and ready for GitHub preparation.