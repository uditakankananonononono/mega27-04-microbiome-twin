"""A nonzero fresh suite exit blocks push; successful push requires exact readback."""
import subprocess
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


def verified_push(*, runner=subprocess.run, python=sys.executable):
    def invoke(args):
        return runner(args,cwd=ROOT,text=True,capture_output=True)
    suite=invoke([python,'-m','pytest','-q'])
    print(suite.stdout,end='');print(suite.stderr,end='',file=sys.stderr)
    if suite.returncode:
        return {'status':'blocked_tests','test_exit':suite.returncode}
    state=invoke(['git','status','--porcelain'])
    if state.returncode or state.stdout.strip():
        return {'status':'blocked_dirty_or_unreadable_tree'}
    head=invoke(['git','rev-parse','HEAD'])
    if head.returncode:
        return {'status':'blocked_head_unreadable'}
    pushed=invoke(['git','push','origin','main'])
    print(pushed.stdout,end='');print(pushed.stderr,end='',file=sys.stderr)
    if pushed.returncode:
        return {'status':'blocked_push','push_exit':pushed.returncode,'head':head.stdout.strip()}
    remote=invoke(['git','ls-remote','origin','refs/heads/main'])
    if remote.returncode or not remote.stdout.split() or remote.stdout.split()[0]!=head.stdout.strip():
        return {'status':'blocked_readback_mismatch','head':head.stdout.strip()}
    return {'status':'verified','head':head.stdout.strip()}


if __name__=='__main__':
    import json
    result=verified_push();print(json.dumps(result))
    raise SystemExit(0 if result['status']=='verified' else 1)
