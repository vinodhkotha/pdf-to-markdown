import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def build_pdf(lines: list[str], padding_bytes: int = 0) -> bytes:
    """Build a minimal single-page PDF with Helvetica text; output is byte-for-byte deterministic."""
    text_ops = "".join(
        f"BT /F1 14 Tf 72 {720 - i * 24} Td ({line}) Tj ET\n" for i, line in enumerate(lines)
    ).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(text_ops) + text_ops + b"endstream",
    ]
    if padding_bytes:
        # Unreferenced stream used only to inflate file size.
        objects.append(b"<< /Length %d >>\nstream\n" % padding_bytes + b" " * padding_bytes + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for num, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % num + body + b"\nendobj\n"

    xref_pos = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref_pos)
    return bytes(out)


@pytest.fixture(scope="session", autouse=True)
def _app_is_running(base_url):
    try:
        urllib.request.urlopen(f"{base_url}/_stcore/health", timeout=5)
    except OSError as exc:
        pytest.exit(
            f"Streamlit app not reachable at {base_url}. Start it with: "
            f"streamlit run app.py --server.headless true  ({exc})",
            returncode=1,
        )


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("pdfs")
    (d / "alpha.pdf").write_bytes(build_pdf(["Alpha Test Document", "Line two of alpha"]))
    (d / "beta.pdf").write_bytes(build_pdf(["Beta Test Document"]))
    (d / "corrupt.pdf").write_bytes(b"%PDF-1.4\nthis is not a valid pdf body\n")
    (d / "notes.txt").write_text("plain text, not a pdf\n", encoding="utf-8")
    (d / "large.pdf").write_bytes(build_pdf(["Large"], padding_bytes=MAX_UPLOAD_BYTES + 1024))
    return d


@pytest.fixture
def app(page: Page, base_url) -> Page:
    page.goto(base_url)
    expect(page.get_by_role("heading", name="PDF to Markdown Converter")).to_be_visible(timeout=30_000)
    return page


@pytest.fixture
def upload(app: Page):
    def _upload(path: Path) -> None:
        app.locator('[data-testid="stFileUploader"] input[type="file"]').set_input_files(str(path))

    return _upload
