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
    # Streamlit enforces maxUploadSize = 25 in the browser, so app.py never receives the file.
    upload(fixtures_dir / "large.pdf")
    uploader = app.locator('[data-testid="stFileUploader"]')
    expect(
        uploader.get_by_role("alert").filter(has_text="File must be 25.0MB or smaller")
    ).to_be_visible(timeout=CONVERT_TIMEOUT)
    expect(app.get_by_text("Selected file:")).to_have_count(0)
    expect(app.get_by_role("button", name="Convert to Markdown")).to_have_count(0)
    expect(preview(app)).to_have_count(0)
    expect(app.get_by_role("button", name="Download Markdown (.md)")).to_have_count(0)


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


def convert_another_button(page: Page):
    return page.get_by_role("button", name="Convert Another PDF")


def test_tc09_convert_another_button_visibility(app: Page, upload, fixtures_dir):
    expect(convert_another_button(app)).to_have_count(0)

    upload(fixtures_dir / "alpha.pdf")
    expect(app.get_by_text("Selected file: alpha.pdf")).to_be_visible()
    expect(convert_another_button(app)).to_have_count(0)

    convert(app)
    expect(convert_another_button(app)).to_be_visible()


def test_tc10_convert_another_hidden_after_failed_conversion(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "corrupt.pdf")
    app.get_by_role("button", name="Convert to Markdown").click()
    expect(app.get_by_text(re.compile("^Conversion failed:"))).to_be_visible(timeout=CONVERT_TIMEOUT)
    expect(convert_another_button(app)).to_have_count(0)


def test_tc11_convert_another_resets_and_converts_second_pdf(app: Page, upload, fixtures_dir):
    upload(fixtures_dir / "alpha.pdf")
    convert(app)
    expect(preview(app)).to_have_value(re.compile("Alpha Test Document"))

    convert_another_button(app).click()

    # Previous upload, status, preview, download and reset button are all cleared.
    expect(app.get_by_text("Selected file:")).to_have_count(0)
    expect(app.get_by_role("button", name="Remove alpha.pdf")).to_have_count(0)
    expect(app.get_by_text("alpha.pdf")).to_have_count(0)
    expect(app.get_by_text("PDF converted successfully!")).to_have_count(0)
    expect(app.get_by_text("Markdown Preview")).to_have_count(0)
    expect(preview(app)).to_have_count(0)
    expect(app.get_by_role("button", name="Download Markdown (.md)")).to_have_count(0)
    expect(app.get_by_role("button", name="Convert to Markdown")).to_have_count(0)
    expect(convert_another_button(app)).to_have_count(0)

    # Uploader is ready for a new PDF.
    expect(app.locator('[data-testid="stFileUploader"]')).to_be_visible()
    expect(app.locator('[data-testid="stFileUploader"] input[type="file"]')).to_have_count(1)

    upload(fixtures_dir / "beta.pdf")
    expect(app.get_by_text("Selected file: beta.pdf")).to_be_visible()
    expect(preview(app)).to_have_count(0)

    convert(app)
    expect(preview(app)).to_have_value(re.compile("Beta Test Document"))
    expect(preview(app)).not_to_have_value(re.compile("Alpha Test Document"))
    expect(convert_another_button(app)).to_be_visible()


def test_tc12_convert_another_same_pdf_starts_clean(app: Page, upload, fixtures_dir, tmp_path):
    upload(fixtures_dir / "alpha.pdf")
    convert(app)
    convert_another_button(app).click()
    expect(preview(app)).to_have_count(0)

    # Re-uploading the identical file must not resurrect the previous result.
    upload(fixtures_dir / "alpha.pdf")
    expect(app.get_by_text("Selected file: alpha.pdf")).to_be_visible()
    expect(preview(app)).to_have_count(0)
    expect(convert_another_button(app)).to_have_count(0)

    convert(app)
    with app.expect_download() as dl_info:
        app.get_by_role("button", name="Download Markdown (.md)").click()
    download = dl_info.value
    assert download.suggested_filename == "alpha.md"
    target = tmp_path / download.suggested_filename
    download.save_as(target)
    assert "Alpha Test Document" in target.read_text(encoding="utf-8")
