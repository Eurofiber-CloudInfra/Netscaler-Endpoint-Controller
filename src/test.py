import shlex
import subprocess
from kopf.testing import KopfRunner

'''
Tester for the operator.
TODO finalize code
'''

def test_operator():
    with KopfRunner(['run', '--verbose', 'examples/01-minimal/example.py']) as runner:
        # do something while the operator is running.

        subprocess.run("kubectl apply -f examples/obj.yaml",
                       shell=True, check=True)
        #time.sleep(1)  # give it some time to react and to sleep and to retry

        subprocess.run("kubectl delete -f examples/obj.yaml",
                       shell=True, check=True)
        #time.sleep(1)  # give it some time to react

    assert runner.exit_code == 0
    assert runner.exception is None
    assert 'And here we are!' in runner.stdout
    assert 'Deleted, really deleted' in runner.stdout
