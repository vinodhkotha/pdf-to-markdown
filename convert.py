
from pathlib import Path
from markitdown import MarkItDown

# Define input and output folders
input_folder = Path("input")
output_folder = Path("output")

# Create output folder if missing
output_folder.mkdir(exist_ok=True)

# Initialize Microsoft's converter
converter = MarkItDown()

# Find all PDF files
pdf_files = list(input_folder.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found in input folder.")

for pdf_file in pdf_files:
    output_file = output_folder / f"{pdf_file.stem}.md"

    try:
        print(f"Converting: {pdf_file.name}")

        result = converter.convert(str(pdf_file))

        output_file.write_text(
            result.markdown,
            encoding="utf-8"
        )

        print(f"Success: {output_file.name}")

    except Exception as error:
        print(f"Error converting {pdf_file.name}: {error}")

print("Conversion completed!")
