import re

from playwright.sync_api import Page, expect

CONVERT_TIMEOUT = 60_000


def convert(page: Page) -> None:
    page.get_by_role("button", name="Convert to Markdown").click()
    expect(page.get_by_text("PDF converted successfully!")).to_be_visible(timeout=CONVERT_TIMEOUT)


def preview(page: Page):
    return page.get_by_label("Converted Markdown")


def test_tc01_page_loads(app: Page):
    expect(app).to_have_title("PDF to Markdown")
    expect(app.get_by_text("Convert your PDF documents into clean Markdown")).to_be_visible()
    expect(app.locator('[data-testid="stFileUploader"]')).to_be_visible()
    expect(app.get_by_text("Powered by Microsoft MarkItDown")).to_be_visible()
    expect(app.get_by_role("button", name="Convert to Markdown")).to_have_count(0)


def test_tc02_upload_valid_pdf(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "alpha.pdf")
    expect(app.get_by_text("Selected file: alpha.pdf")).to_be_visible()
    expect(app.get_by_role("button", name="Convert to Markdown")).to_be_enabled()
    expect(preview(app)).to_have_count(0)


def test_tc03_convert_shows_preview(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "alpha.pdf")
    convert(app)
    expect(app.get_by_text("Markdown Preview")).to_be_visible()
    expect(preview(app)).to_have_value(re.compile(r"Alpha Test Document[\s\S]*Line two of alpha"))


def test_tc04_download_markdown(app: Page, upload, fixtures_dir, tmp_path):
    upload(fixtures_dir / "alpha.pdf")
    convert(app)
    with app.expect_download() as dl_info:
        app.get_by_role("button", name="Download Markdown (.md)").click()
    download = dl_info.value
    assert download.suggested_filename == "alpha.md"
    target = tmp_path / download.suggested_filename
    download.save_as(target)
    assert "Alpha Test Document" in target.read_text(encoding="utf-8")


def test_tc05_non_pdf_rejected(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "notes.txt")
    expect(app.get_by_text(re.compile("not allowed", re.IGNORECASE))).to_be_visible()
    expect(app.get_by_text("Selected file:")).to_have_count(0)
    expect(app.get_by_role("button", name="Convert to Markdown")).to_have_count(0)


def test_tc06_oversized_pdf_rejected(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "large.pdf")
    expect(app.get_by_text("PDF exceeds the 25 MB limit.")).to_be_visible(timeout=CONVERT_TIMEOUT)
    expect(app.get_by_role("button", name="Convert to Markdown")).to_have_count(0)


def test_tc07_corrupt_pdf_shows_error(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "corrupt.pdf")
    app.get_by_role("button", name="Convert to Markdown").click()
    expect(app.get_by_text(re.compile("^Conversion failed: The file is not a valid PDF"))).to_be_visible(
        timeout=CONVERT_TIMEOUT
    )
    expect(app.get_by_text("PDF converted successfully!")).to_have_count(0)
    expect(preview(app)).to_have_count(0)
    expect(app.get_by_role("button", name="Download Markdown (.md)")).to_have_count(0)


def test_tc08_new_or_removed_file_clears_result(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "alpha.pdf")
    convert(app)
    expect(preview(app)).to_be_visible()

    upload(fixtures_dir / "beta.pdf")
    expect(app.get_by_text("Selected file: beta.pdf")).to_be_visible()
    expect(preview(app)).to_have_count(0)

    convert(app)
    expect(preview(app)).to_have_value(re.compile("Beta Test Document"))

    app.get_by_role("button", name="Remove beta.pdf").click()
    expect(app.get_by_text("Selected file:")).to_have_count(0)
    expect(preview(app)).to_have_count(0)
