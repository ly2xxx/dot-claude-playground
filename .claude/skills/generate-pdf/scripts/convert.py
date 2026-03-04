"""
PDF Generator Script
Converts markdown files to professionally styled PDFs
"""

import sys
import markdown
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
    if len(sys.argv) != 2:
        print("Usage: python convert.py <markdown-file>")
        print("Example: python convert.py docs/guide.md")
        sys.exit(1)

    md_file = sys.argv[1]
    convert_md_to_pdf(md_file)

if __name__ == "__main__":
    main()
