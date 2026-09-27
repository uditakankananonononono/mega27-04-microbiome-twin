"""Conservative prose estimator frozen in results/PREREG_20260927_body_page_audit.md."""
import json
import re
from pathlib import Path
from docx import Document
ROOT=Path(__file__).resolve().parents[1]

def run():
    d=Document(ROOT/'paper/mega27-04-microbiome-twin-paper.docx')
    in_body=False; paragraphs=[]; omitted={'heading':0,'non_normal':0,'caption_or_equation':0}
    for p in d.paragraphs:
        txt=p.text.strip();style=p.style.name
        if style.startswith('Heading') and txt.startswith('1. Introduction'):in_body=True;continue
        if style.startswith('Heading') and (txt.startswith('Appendix A.') or txt=='References'):break
        if not in_body:continue
        if style.startswith('Heading'):omitted['heading']+=1;continue
        if style!='Normal':omitted['non_normal']+=1;continue
        if txt.startswith(('Table ','Figure ')) or (p.alignment is not None and re.search(r'\(\d+\)\s*$',txt)):
            omitted['caption_or_equation']+=1;continue
        if txt:paragraphs.append(txt)
    text='\n'.join(paragraphs)
    import subprocess
    info=subprocess.check_output(['pdfinfo',str(ROOT/'paper/mega27-04-microbiome-twin-paper.pdf')],text=True)
    pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
    return {'method':'normal-style prose from Introduction through before Appendix A; excludes headings/captions/equations/tables/figures/abstract/references',
            'prose_paragraphs':len(paragraphs),'prose_characters':len(text),'prose_words':len(text.split()),'omitted_paragraphs':omitted,
            'estimated_body_text_pages_at_2500_chars':round(len(text)/2500,2), 'estimated_body_text_pages_at_3000_chars':round(len(text)/3000,2),
            'total_pdf_pages':pages,'certified_50_body_pages':False,
            'caveat':'Character-density estimates are not visual page counts. No 50-page certification follows from total PDF pages.'}
if __name__=='__main__':
    result=run();(ROOT/'results/body_page_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
