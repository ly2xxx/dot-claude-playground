import re
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE

def add_hyperlink(paragraph, text, url):
    """
    Adds a hyperlink to a paragraph with proper formatting.
    """
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    # Theme color blue for link
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0056B3')
    rPr.append(c)
    
    # Underline
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    
    # Font properties
    f = OxmlElement('w:rFonts')
    f.set(qn('w:ascii'), 'Calibri')
    f.set(qn('w:hAnsi'), 'Calibri')
    rPr.append(f)
    
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '19') # ~9.5 pt
    rPr.append(sz)
    
    new_run.append(rPr)
    new_run_text = OxmlElement('w:t')
    new_run_text.text = text
    new_run.append(new_run_text)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink

def add_paragraph_bottom_border(paragraph, color_hex="1A365D", size="8"):
    """
    Injects XML to add a clean bottom border to a paragraph.
    """
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = pPr.find(qn('w:pBdr'))
    if pBdr is None:
        pBdr = OxmlElement('w:pBdr')
        pPr.append(pBdr)
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), size) # 8 = 1pt width
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), color_hex)
    pBdr.append(bottom)

def add_formatted_text(paragraph, text, font_size=9.5, font_name="Calibri", color=None, default_bold=False):
    """
    Parses basic markdown inline formatting (**bold** and [text](url)) and appends to paragraph.
    """
    # Regex to tokenise bold and links
    pattern = re.compile(r'(\*\*.*?\*\*|\[.*?\]\(.*?\))')
    parts = pattern.split(text)
    
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            bold_text = part[2:-2]
            run = paragraph.add_run(bold_text)
            run.bold = True
            run.font.name = font_name
            run.font.size = Pt(font_size)
            if color:
                run.font.color.rgb = color
        elif part.startswith('[') and ']' in part and '(' in part and part.endswith(')'):
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                add_hyperlink(paragraph, link_text, link_url)
        else:
            run = paragraph.add_run(part)
            run.bold = default_bold
            run.font.name = font_name
            run.font.size = Pt(font_size)
            if color:
                run.font.color.rgb = color

def apply_paragraph_format(p, space_before=0, space_after=3, line_spacing=1.15):
    """
    Applies margins and line spacing to a paragraph.
    """
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def main():
    import sys
    
    if len(sys.argv) > 1:
        md_path = os.path.abspath(sys.argv[1])
    else:
        print("Usage: python convert_cv.py <path_to_markdown_file>")
        return
        
    if not os.path.exists(md_path):
        print(f"Error: File '{md_path}' not found.")
        return
        
    docx_path = os.path.splitext(md_path)[0] + ".docx"
    
    print(f"Reading: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    doc = Document()
    
    # Page setup - Margins (Top/Bottom: 0.6 in, Left/Right: 0.7 in)
    for section in doc.sections:
        section.top_margin = Inches(0.60)
        section.bottom_margin = Inches(0.60)
        section.left_margin = Inches(0.70)
        section.right_margin = Inches(0.70)
        
    current_section = "HEADER"
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Section transition (H2)
        if line.startswith('## '):
            sec_title = line[3:].strip()
            current_section = sec_title.upper()
            
            p = doc.add_paragraph()
            apply_paragraph_format(p, space_before=11, space_after=4, line_spacing=1.0)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(sec_title.upper())
            run.bold = True
            run.font.name = 'Calibri'
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(26, 54, 93) # Slate Blue (#1A365D)
            add_paragraph_bottom_border(p, color_hex="1A365D", size="8")
            
            i += 1
            continue
            
        # Ignore horizontal rules
        if line == '---':
            i += 1
            continue
            
        # Parse based on section state
        if current_section == "HEADER":
            if line.startswith('# '):
                # Name Header
                name = line[2:].strip()
                p = doc.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                apply_paragraph_format(p, space_before=0, space_after=2, line_spacing=1.0)
                
                run = p.add_run(name)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(26, 54, 93) # Slate Blue (#1A365D)
            elif line.startswith('**') and line.endswith('**'):
                # Subtitle Tagline
                tagline = line[2:-2].strip()
                p = doc.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                apply_paragraph_format(p, space_before=0, space_after=4, line_spacing=1.0)
                
                run = p.add_run(tagline)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(44, 95, 138) # Accent Blue (#2C5F8A)
            else:
                # Contact info / Links
                p = doc.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                apply_paragraph_format(p, space_before=0, space_after=8, line_spacing=1.0)
                add_formatted_text(p, line, font_size=9.5, color=RGBColor(51, 51, 51))
                
        elif "PROFILE" in current_section:
            p = doc.add_paragraph()
            apply_paragraph_format(p, space_before=2, space_after=4, line_spacing=1.15)
            if line.startswith('**Specialised in:**'):
                add_formatted_text(p, line, font_size=9.5, color=RGBColor(26, 54, 93))
            else:
                add_formatted_text(p, line, font_size=9.5, color=RGBColor(51, 51, 51))
                
        elif "SKILLS" in current_section:
            if line.startswith('**') and line.endswith('**'):
                # Skill group subheader
                cat_name = line[2:-2].strip()
                p = doc.add_paragraph()
                apply_paragraph_format(p, space_before=6, space_after=2, line_spacing=1.0)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(cat_name)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(17, 17, 17)
            elif line.startswith('- '):
                # Skill bullet point
                p = doc.add_paragraph(style='List Bullet')
                apply_paragraph_format(p, space_before=0, space_after=2, line_spacing=1.15)
                bullet_content = line[2:].strip()
                add_formatted_text(p, bullet_content, font_size=9.5, color=RGBColor(51, 51, 51))
                
        elif "EXPERIENCE" in current_section:
            if line.startswith('### '):
                # Organisation H3
                emp = line[4:].strip()
                p = doc.add_paragraph()
                apply_paragraph_format(p, space_before=8, space_after=2, line_spacing=1.0)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(emp)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(17, 17, 17)
            elif line.startswith('**') and line.endswith('**'):
                # Role / Dates Subtitle
                role_info = line[2:-2].strip()
                p = doc.add_paragraph()
                apply_paragraph_format(p, space_before=2, space_after=3, line_spacing=1.0)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(role_info)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(85, 85, 85) # Muted gray
            elif line.startswith('- '):
                # Experience bullet point
                p = doc.add_paragraph(style='List Bullet')
                apply_paragraph_format(p, space_before=0, space_after=2.5, line_spacing=1.15)
                bullet_content = line[2:].strip()
                add_formatted_text(p, bullet_content, font_size=9.5, color=RGBColor(51, 51, 51))
                
        elif "EDUCATION" in current_section:
            if line.startswith('**') and line.endswith('**'):
                # University/College Subheader
                uni = line[2:-2].strip()
                p = doc.add_paragraph()
                apply_paragraph_format(p, space_before=8, space_after=2, line_spacing=1.0)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(uni)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(17, 17, 17)
            elif line.startswith('- '):
                # Education/Thesis bullet point
                p = doc.add_paragraph(style='List Bullet')
                apply_paragraph_format(p, space_before=0, space_after=2, line_spacing=1.15)
                bullet_content = line[2:].strip()
                add_formatted_text(p, bullet_content, font_size=9.5, color=RGBColor(51, 51, 51))
            else:
                # Degree / Timeframe
                p = doc.add_paragraph()
                apply_paragraph_format(p, space_before=1, space_after=2, line_spacing=1.0)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(line)
                run.italic = True
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(85, 85, 85) # Muted gray
                
        elif "ACHIEVEMENTS" in current_section:
            if line.startswith('- '):
                # Achievement bullet point
                p = doc.add_paragraph(style='List Bullet')
                apply_paragraph_format(p, space_before=0, space_after=2.5, line_spacing=1.15)
                bullet_content = line[2:].strip()
                add_formatted_text(p, bullet_content, font_size=9.5, color=RGBColor(51, 51, 51))
                
        i += 1
        
    doc.save(docx_path)
    print(f"Successfully generated: {docx_path}")

if __name__ == '__main__':
    main()
