"""
PDF Generator Script
Converts markdown files to professionally styled PDFs.

Two pipelines:

  default   markdown -> HTML -> PDF (xhtml2pdf). General-purpose document
            styling: docs, guides, notes, cheatsheets.

  --cv      markdown -> .docx (markdown-to-word skill) -> PDF (LibreOffice).
            Use for CVs. This is the pipeline that produced the reference
            CVs (YL-CV-2026-CityFM.pdf / YL-CV-2026-general.pdf, whose
            metadata reads Author=python-docx, Producer=LibreOffice).
            The default HTML pipeline does NOT reproduce that look — it has
            no notion of CV sections, justifies body text, and renders at
            document rather than CV scale.
"""

import subprocess
import sys
import markdown
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Sibling skill that owns the CV-aware markdown -> .docx styling.
CV_CONVERTER = (Path(__file__).resolve().parent.parent.parent
                / 'markdown-to-word' / 'scripts' / 'convert_cv.py')

SOFFICE_CANDIDATES = [
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    '/usr/bin/soffice',
    '/usr/bin/libreoffice',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
]


def find_soffice():
    """Locate the LibreOffice binary, or return None."""
    from shutil import which
    for name in ('soffice', 'libreoffice'):
        found = which(name)
        if found:
            return found
    for path in SOFFICE_CANDIDATES:
        if Path(path).exists():
            return path
    return None


def convert_cv_to_pdf(md_file):
    """CV pipeline: markdown -> .docx -> .pdf, output beside the source file."""
    md_path = Path(md_file).resolve()
    if not md_path.exists():
        print(f"Error: File not found: {md_file}")
        sys.exit(1)

    if not CV_CONVERTER.exists():
        print(f"Error: CV converter not found at {CV_CONVERTER}")
        print("The --cv pipeline requires the sibling 'markdown-to-word' skill.")
        sys.exit(1)

    soffice = find_soffice()
    if not soffice:
        print("Error: LibreOffice not found — required to convert .docx to PDF.")
        print("Install LibreOffice, or generate the .docx only via the "
              "markdown-to-word skill and export to PDF from Word.")
        sys.exit(1)

    # Step 1: markdown -> .docx (CV-aware styling)
    print(f"[1/2] Building .docx via markdown-to-word ...")
    result = subprocess.run([sys.executable, str(CV_CONVERTER), str(md_path)],
                            capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print("Error: .docx conversion failed")
        print(result.stdout, result.stderr)
        sys.exit(1)
    print(result.stdout.strip())

    docx_path = md_path.with_suffix('.docx')
    if not docx_path.exists():
        print(f"Error: expected .docx not produced at {docx_path}")
        sys.exit(1)

    # Step 2: .docx -> .pdf (LibreOffice), written beside the source
    print(f"[2/2] Converting to PDF via LibreOffice ...")
    result = subprocess.run(
        [soffice, '--headless', '--convert-to', 'pdf',
         '--outdir', str(md_path.parent), str(docx_path)],
        capture_output=True, text=True, encoding='utf-8', errors='replace')

    pdf_path = md_path.with_suffix('.pdf')
    if result.returncode != 0 or not pdf_path.exists():
        print("Error: LibreOffice PDF conversion failed")
        print(result.stdout, result.stderr)
        sys.exit(1)

    print(f"DOCX generated: {docx_path} ({docx_path.stat().st_size / 1024:.1f} KB)")
    print(f"PDF generated:  {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
    return str(pdf_path)

def convert_md_to_pdf(md_file):
    """Convert a markdown file to a styled PDF"""

    # Check if file exists
    if not Path(md_file).exists():
        print(f"Error: File not found: {md_file}")
        sys.exit(1)

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
    )

    # Add professional styling (xhtml2pdf compatible CSS)
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 1in;
            }}

            body {{
                font-family: Georgia, serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }}

            h1 {{
                font-family: Helvetica, sans-serif;
                color: #2c3e50;
                font-size: 28pt;
                margin-top: 0;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }}

            h2 {{
                font-family: Helvetica, sans-serif;
                color: #34495e;
                font-size: 20pt;
                margin-top: 30px;
                margin-bottom: 15px;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
            }}

            h3 {{
                font-family: Helvetica, sans-serif;
                color: #34495e;
                font-size: 16pt;
                margin-top: 20px;
                margin-bottom: 10px;
            }}

            h4, h5, h6 {{
                font-family: Helvetica, sans-serif;
                color: #34495e;
            }}

            p {{
                margin: 10px 0;
                text-align: justify;
            }}

            code {{
                background: #f4f4f4;
                padding: 2px 6px;
                font-family: "Courier New", monospace;
                font-size: 10pt;
                color: #e74c3c;
            }}

            pre {{
                background: #f8f8f8;
                padding: 15px;
                border-left: 4px solid #3498db;
                line-height: 1.4;
            }}

            pre code {{
                background: transparent;
                padding: 0;
                color: #333;
                font-size: 9pt;
            }}

            blockquote {{
                border-left: 4px solid #95a5a6;
                padding-left: 20px;
                margin-left: 0;
                font-style: italic;
                color: #555;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}

            th {{
                background: #3498db;
                color: white;
                padding: 10px;
                text-align: left;
                font-family: Helvetica, sans-serif;
            }}

            td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
            }}

            ul, ol {{
                margin: 10px 0;
                padding-left: 30px;
            }}

            li {{
                margin: 5px 0;
            }}

            hr {{
                border: none;
                border-top: 1px solid #bdc3c7;
                margin: 30px 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Create output directory
    output_dir = Path('output/pdfs')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    pdf_filename = Path(md_file).stem + '.pdf'
    pdf_path = output_dir / pdf_filename

    try:
        from xhtml2pdf import pisa

        with open(pdf_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)

        if pisa_status.err:
            print(f"Error generating PDF: xhtml2pdf reported errors")
            sys.exit(1)

        print(f"PDF generated: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
        return str(pdf_path)

    except ImportError:
        print("Error: xhtml2pdf not installed. Install with: pip install xhtml2pdf")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        sys.exit(1)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}

    if len(args) != 1:
        print("Usage: python convert.py [--cv] <markdown-file>")
        print("Example: python convert.py docs/guide.md")
        print("Example: python convert.py --cv assets/YL-CV-2026-AI.md")
        sys.exit(1)

    if '--cv' in flags:
        convert_cv_to_pdf(args[0])
    else:
        convert_md_to_pdf(args[0])

if __name__ == "__main__":
    main()
