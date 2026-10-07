from pathlib import Path
import json
import sys
from archive_compare import assert_archive_equal


def test_window_mapping_boundaries():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mdsine_window_diagnostic import _window
    assert _window(21.499)=='pre'
    assert _window(21.5)=='diet'
    assert _window(28.5)=='diet'
    assert _window(28.501)=='between_diet_vanco'
    assert _window(35.5)=='vancomycin'
    assert _window(42.5)=='vancomycin'
    assert _window(50.5)=='gentamicin'
    assert _window(57.5)=='gentamicin'
    assert _window(57.501)=='after_gent'


def test_window_result_uses_mouse_units_and_reproduces_archives():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mdsine_window_diagnostic import run
    for cohort,n in [('healthy',4),('uc',5)]:
        result=run(cohort)
        stored=json.loads((root/f'results/mdsine_window_{cohort}.json').read_text())
        assert_archive_equal(result,stored)
        assert result['subjects']==n
        assert len(result['windows'])==14
        assert all(r['n_mice']==n for r in result['windows'])
