import pytest
from archive_compare import assert_archive_equal

def test_roundoff_only():
 assert_archive_equal({'n':3,'x':[.123456789]}, {'n':3,'x':[.1234567890000001]})

@pytest.mark.parametrize('actual,expected',[(3.,3),(True,1),({'n':4},{'n':3}),([1],[1,2]),(.124,.123),('new','old'),({'x':1,'y':2},{'x':1})])
def test_real_change_rejected(actual,expected):
 with pytest.raises(AssertionError):assert_archive_equal(actual,expected)
