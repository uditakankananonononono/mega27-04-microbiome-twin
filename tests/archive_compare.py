"""Keep archive structure exact; tolerate only floating-point roundoff."""
import math

def assert_archive_equal(actual,expected):
    if isinstance(expected,dict):
        assert isinstance(actual,dict) and actual.keys()==expected.keys()
        for key in expected:assert_archive_equal(actual[key],expected[key])
    elif isinstance(expected,list):
        assert isinstance(actual,list) and len(actual)==len(expected)
        for a,e in zip(actual,expected):assert_archive_equal(a,e)
    elif isinstance(expected,float):
        assert isinstance(actual,float) and math.isfinite(actual) and math.isfinite(expected)
        assert math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12)
    else:
        assert type(actual) is type(expected) and actual==expected
