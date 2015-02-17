from __future__ import absolute_import
from celery import shared_task
import os
import subprocess
from .settings import OJ_RUNNER
APP_DIR = os.path.dirname(os.path.dirname(__file__))


@shared_task
def run_popen(**rc):
    args = [
        "python",
        os.path.join(APP_DIR, "onlinejudge", OJ_RUNNER),
        rc['inpath'],
        rc['outpath'],
        rc['errpath'],
        str(rc['quota']['wallclock']),
        str(rc['quota']['cpu']),
        str(rc['quota']['memory']),
        str(rc['quota']['disk'])
    ]
    args.extend(rc['args'])
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    process.wait()
    return output


# Following code does not work, check sandbox issue #17
# https://github.com/openjudge/sandbox/issues/17
"""
from celery.exceptions import SoftTimeLimitExceeded
from platform import system, machine
import signal

if system() not in ('Linux', ) or machine() not in ('i686', 'x86_64', ):
    raise AssertionError("Unsupported platform type.\n")


import sandbox
if not hasattr(sandbox, '__version__') or sandbox.__version__ < "0.3.4-3":
    raise AssertionError("Unsupported sandbox version.\n")


from sandbox import *


class MinimalPolicy(SandboxPolicy):

    # white list of essential linux syscalls for statically-linked C programs
    sc_safe = {'i686': set([0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140, 163,
        192, 197, 224, 243, 252, ]), 'x86_64': set([0, 1, 5, 8, 9, 10, 11, 12,
        16, 25, 63, 158, 219, 231, ])}

    def __init__(self, sbox=None):
        super(MinimalPolicy, self).__init__()
        # initialize table of system call rules
        self.sc_table = {}
        if machine() == 'x86_64':
            for (mode, abi) in ((0, 'x86_64'), (1, 'i686'), ):
                for scno in MinimalPolicy.sc_safe[abi]:
                    self.sc_table[(scno, mode)] = self._CONT
        else:  # i686
            for scno in MinimalPolicy.sc_safe[machine()]:
                self.sc_table[scno] = self._CONT
        # save a local reference to the parent sandbox
        if isinstance(sbox, Sandbox):
            self.sbox = sbox
        pass

    def __call__(self, e, a):
        # handle SYSCALL/SYSRET events with local rules
        if e.type in (S_EVENT_SYSCALL, S_EVENT_SYSRET):
            sc = (e.data, e.ext0) if machine() == 'x86_64' else e.data
            rule = self.sc_table.get(sc, self._KILL_RF)
            return rule(e, a)
        # bypass other events to base class
        return super(MinimalPolicy, self).__call__(e, a)

    def _CONT(self, e, a):  # continue
        a.type = S_ACTION_CONT
        return a

    def _KILL_RF(self, e, a):  # restricted func.
        a.type, a.data = S_ACTION_KILL, S_RESULT_RF
        return a

    pass


class DefaultSandboxRunner(Sandbox):
    # result code translation table
    result_name = dict((getattr(Sandbox, 'S_RESULT_%s' % r), r) for r in
        ('PD', 'OK', 'RF', 'RT', 'TL', 'ML', 'OL', 'AT', 'IE', 'BP'))

    def __init__(self, *args, **kwds):
        self.outpath = kwds['stdout'].name
        self.errpath = kwds['stderr'].name
        kwds.update({'policy': MinimalPolicy()})
        super(DefaultSandboxRunner, self).__init__(*args, **kwds)

    def probe(self):
        # add custom entries into the probe dict
        d = Sandbox.probe(self, False)
        d['cputime'] = d['cpu_info'][0]
        d['memory'] = d['mem_info'][1]
        d['status'] = DefaultSandboxRunner.result_name.get(self.result, 'NA')
        d['outpath'] = self.outpath
        d['errpath'] = self.errpath
        return d


@shared_task
def add(x, y):
    return x + y


@shared_task
def run(**runner_configuration):
    # convert keys to strings to pass them to DefaultSandboxRunner
    runner_configuration = {str(k): v \
                            for (k, v) in runner_configuration.items()}
    fin = open(runner_configuration.pop('inpath'), 'r')
    fout = open(runner_configuration.pop('outpath'), 'wb')
    ferr = open(runner_configuration.pop('errpath'), 'wb')
    runner_configuration['stdin'] = fin
    runner_configuration['stdout'] = fout
    runner_configuration['stderr'] = ferr
    with open("/home/web/trace.txt", "w") as f:
        f.write("start")
    ojr = DefaultSandboxRunner(**runner_configuration)
    try:
        ojr.run()  # blocking
    except SoftTimeLimitExceeded:
        with open("/home/web/trace.txt", "a") as f:
            f.write("pid")
        with open("/home/web/trace.txt", "a") as f:
            f.write("pid %s" % ojr.pid)
        ret = ojr.probe()
        os.kill(ojr.pid, signal.SIGKILL)
    else:
        ret = ojr.probe()
    fin.close()
    fout.close()
    ferr.close()
    return ret
"""
