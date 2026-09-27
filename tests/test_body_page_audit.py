import json
import pytest
pytest.importorskip("docx")
from pathlib import Path
import sys


def test_body_audit_is_reproducible_and_not_certified():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from body_page_audit import run
    result=run();stored=json.loads((root/'results/body_page_audit.json').read_text())
    assert result==stored
    assert result['prose_paragraphs']>0
    assert result['total_pdf_pages']>result['estimated_body_text_pages_at_2500_chars']
    assert result['certified_50_body_pages'] is False
