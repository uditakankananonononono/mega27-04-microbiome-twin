import importlib.util
from subprocess import CompletedProcess


def load():
    s=importlib.util.spec_from_file_location('verified_push','scripts/verified_push.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def test_suite_failure_never_calls_git():
    calls=[]
    def runner(args,**kwargs):
        calls.append(args);return CompletedProcess(args,1,'failed','')
    assert load().verified_push(runner=runner)['status']=='blocked_tests'
    assert len(calls)==1 and calls[0][1:]==['-m','pytest','-q']


def test_dirty_tree_never_pushes():
    calls=[]
    def runner(args,**kwargs):
        calls.append(args);return CompletedProcess(args,0,' M changed' if args[:2]==['git','status'] else '','')
    assert load().verified_push(runner=runner)['status']=='blocked_dirty_or_unreadable_tree'
    assert not any('push' in c for c in calls)


def test_verified_push_and_mismatched_readback():
    for remote,expected in [('abc','verified'),('different','blocked_readback_mismatch')]:
        calls=[]
        def runner(args,**kwargs):
            calls.append(args)
            text='abc\n' if args[:2]==['git','rev-parse'] else remote+' refs/heads/main\n' if args[:2]==['git','ls-remote'] else ''
            return CompletedProcess(args,0,text,'')
        assert load().verified_push(runner=runner)['status']==expected
        assert sum(c[:2]==['git','push'] for c in calls)==1
