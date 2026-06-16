#!/usr/bin/env python3
"""Convert Markdown report to PDF using Python."""
import sys
import os

def md_to_html(md_path):
    """Convert Markdown file to styled HTML."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first heading
    title = "Analysis Report"
    for line in md_content.split('\n'):
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## '):
            title = line[2:].strip()
            break
    
    # Simple Markdown to HTML conversion
    html_lines = []
    in_code_block = False
    in_list = False
    in_blockquote = False
    unordered_list_level = 0
    
    for line in md_content.split('\n'):
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        
        # Horizontal rules
        if stripped == '---':
            html_lines.append('<hr>')
            continue
        
        # Blockquote
        if stripped.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            html_lines.append(f'<p>{stripped[2:]}</p>')
            continue
        else:
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
        
        # Headings
        if stripped.startswith('#### '):
            html_lines.append(f'<h4>{stripped[5:]}</h4>')
            continue
        if stripped.startswith('### '):
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
            continue
        if stripped.startswith('## '):
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
            continue
        if stripped.startswith('# '):
            continue  # skip main title
        
        # Unordered lists
        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            # Handle bold within list items
            item = stripped[2:]
            item = item.replace('**', '<strong>', 1)
            if '<strong>' in item:
                item = item.replace('**', '</strong>', 1)
            html_lines.append(f'<li>{item}</li>')
            continue
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
        
        # Bold text
        import re
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
        
        # Italic text
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
        
        # Empty lines
        if not stripped:
            continue
        
        # Regular paragraph
        if not stripped.startswith('<'):
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append(stripped)
    
    if in_list:
        html_lines.append('</ul>')
    
    html_content = '\n'.join(html_lines)
    
    # Full HTML template
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @media print {{
    body {{ margin: 0; padding: 0; }}
    .page-break {{ page-break-before: always; }}
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #1a1a1a;
    max-width: 720px;
    margin: 0 auto;
    padding: 48px 40px;
    background: #fff;
  }}
  hr {{
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 32px 0;
  }}
  .report-meta {{
    text-align: center;
    margin-bottom: 48px;
  }}
  .report-meta h1 {{
    font-size: 20pt;
    font-weight: 400;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
    color: #111;
  }}
  .report-meta p {{
    font-size: 9pt;
    color: #999;
    letter-spacing: 0.06em;
  }}
  h2 {{
    font-size: 13pt;
    font-weight: 400;
    color: #111;
    margin-top: 40px;
    margin-bottom: 16px;
    letter-spacing: 0.04em;
    padding-top: 24px;
    border-top: 1px solid #eee;
  }}
  h2:first-of-type {{
    border-top: none;
    margin-top: 0;
    padding-top: 0;
  }}
  h3 {{
    font-size: 11pt;
    font-weight: 400;
    color: #333;
    margin-top: 24px;
    margin-bottom: 8px;
    letter-spacing: 0.03em;
  }}
  h4 {{
    font-size: 10pt;
    font-weight: 400;
    color: #555;
    margin-top: 16px;
    margin-bottom: 4px;
  }}
  p {{
    font-size: 10.5pt;
    color: #444;
    margin-bottom: 8px;
    text-align: justify;
  }}
  strong {{
    color: #111;
    font-weight: 500;
  }}
  em {{
    color: #666;
    font-style: italic;
  }}
  ul, ol {{
    margin: 8px 0 16px 24px;
    color: #555;
  }}
  li {{
    font-size: 10.5pt;
    margin-bottom: 6px;
    line-height: 1.7;
  }}
  li strong {{
    color: #333;
  }}
  blockquote {{
    border-left: 3px solid #ddd;
    margin: 16px 0;
    padding: 8px 16px;
    background: #fafafa;
  }}
  blockquote p {{
    font-size: 10pt;
    color: #666;
    font-style: italic;
    margin-bottom: 4px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 10pt;
  }}
  table td, table th {{
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
    text-align: left;
  }}
  table th {{
    color: #999;
    font-weight: 400;
    letter-spacing: 0.06em;
    font-size: 9pt;
    text-transform: uppercase;
  }}
  .page-break {{
    page-break-before: always;
  }}
  @media print {{
    body {{ padding: 36px 48px; }}
    h2 {{ page-break-after: avoid; }}
    h3 {{ page-break-after: avoid; }}
    p, li {{ orphans: 3; widows: 3; }}
  }}
</style>
</head>
<body>
<div class="report-meta">
  <h1>{title}</h1>
  <p>分析引擎：project_analyst v3 · 2026年6月16日</p>
</div>
{html_content}
</body>
</html>'''
    
    return full_html, title


if __name__ == '__main__':
    md_path = sys.argv[1] if len(sys.argv) > 1 else r'D:\Photography\project_analysis\无垠之闷尘肺都市.md'
    output_dir = os.path.dirname(md_path)
    base_name = os.path.splitext(os.path.basename(md_path))[0]
    
    html, title = md_to_html(md_path)
    
    # Save HTML
    html_path = os.path.join(output_dir, f'{base_name}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'HTML saved: {html_path}')
    
    # Try to generate PDF
    pdf_path = os.path.join(output_dir, f'{base_name}.pdf')
    
    # Method 1: Try pdfkit
    try:
        import pdfkit
        pdfkit.from_file(html_path, pdf_path)
        print(f'PDF generated (pdfkit): {pdf_path}')
    except ImportError:
        print('pdfkit not installed, trying weasyprint...')
        
        # Method 2: Try weasyprint
        try:
            from weasyprint import HTML
            HTML(filename=html_path).write_pdf(pdf_path)
            print(f'PDF generated (weasyprint): {pdf_path}')
        except ImportError:
            print('weasyprint not installed.')
            print(f'Please open the HTML file in browser and print to PDF:')
            print(f'  {html_path}')