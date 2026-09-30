from pypdf import PdfReader

pdf_path = "data/support-policy.pdf"

reader = PdfReader(pdf_path)

print(f"Number of pages: {len(reader.pages)}")
print("=" * 80)

for page_number, page in enumerate(reader.pages, start=1):
    print(f"\n\n===== PAGE {page_number} =====\n")
    text = page.extract_text()
    print(text)