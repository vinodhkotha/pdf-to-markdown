# PDF to Markdown

A small Streamlit web app that converts a PDF into Markdown using [Microsoft MarkItDown](https://github.com/microsoft/markitdown). Upload a PDF, preview the result, and download it as a `.md` file.

## Features

- Single PDF upload (max 25 MB)
- Structural PDF validation: corrupted or malformed files are rejected with a clear error
- Markdown preview and `.md` download
- Batch CLI script (`convert.py`) for converting every PDF in `input/`
- Headless Playwright end-to-end tests with HTML reporting

## Prerequisites

- Python 3.10+ (developed on 3.13)
- Windows, macOS, or Linux

## Local setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501.

### Batch conversion (optional)

Put PDFs in `input/` and run:

```bash
python convert.py
```

Markdown files are written to `output/`. Both folders are git-ignored apart from a placeholder.

## End-to-end tests

Tests use pytest and Playwright (headless Chromium) against the running app at `http://localhost:8501`. Test PDFs are generated at runtime, so no documents are stored in the repository.

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium

# Terminal 1
streamlit run app.py --server.headless true

# Terminal 2
python -m pytest
```

| ID | Scenario |
|----|----------|
| TC-01 | Page loads with title, description, uploader, footer |
| TC-02 | Valid PDF upload shows file name and Convert button |
| TC-03 | Conversion shows success message and Markdown preview |
| TC-04 | Download returns a `.md` file with expected content |
| TC-05 | Non-PDF files are rejected |
| TC-06 | PDFs over 25 MB are rejected |
| TC-07 | Corrupted PDFs show a conversion error |
| TC-08 | Replacing or removing the file clears the previous result |

Outputs:

- HTML report: `reports/report.html`
- Failure screenshots and traces: `test-results/` (open with `python -m playwright show-trace <path>/trace.zip`)

## Project structure

```
app.py                 Streamlit application
convert.py             Batch conversion script
requirements.txt       Runtime dependencies
requirements-dev.txt   Test dependencies
pytest.ini             pytest / Playwright configuration
tests/                 Playwright end-to-end tests
input/  output/        Local working folders (contents git-ignored)
```
