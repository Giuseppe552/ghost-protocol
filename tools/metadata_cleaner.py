import os
import argparse
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import docx


def clean_image(input_file, output_file):
    """Remove EXIF metadata from images."""
    img = Image.open(input_file)
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)
    img_no_exif.save(output_file)
    print(f"[+] Cleaned image saved: {output_file}")


def clean_pdf(input_file, output_file):
    """Remove metadata from PDFs."""
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata({})  # clear metadata
    with open(output_file, "wb") as f:
        writer.write(f)

    print(f"[+] Cleaned PDF saved: {output_file}")


def clean_docx(input_file, output_file):
    """Remove metadata from Word documents."""
    doc = docx.Document(input_file)
    props = doc.core_properties
    props.author = ""
    props.title = ""
    props.subject = ""
    props.comments = ""
    doc.save(output_file)
    print(f"[+] Cleaned DOCX saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Metadata Cleaner Tool")
    parser.add_argument("input", help="Input file (jpg, png, pdf, or docx)")
    parser.add_argument("-o", "--output", help="Output file name", required=True)
    args = parser.parse_args()

    infile = args.input
    outfile = args.output

    if not os.path.exists(infile):
        print(f"[!] File not found: {infile}")
        return

    ext = infile.lower().split(".")[-1]

    if ext in ["jpg", "jpeg", "png"]:
        clean_image(infile, outfile)
    elif ext == "pdf":
        clean_pdf(infile, outfile)
    elif ext == "docx":
        clean_docx(infile, outfile)
    else:
        print("[!] Unsupported file type. Use jpg, jpeg, png, pdf, or docx.")


if __name__ == "__main__":
    main()
