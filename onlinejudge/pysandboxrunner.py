import os
import sys
import json

try:
    # check platform type
    system, machine = os.uname()[0], os.uname()[4]
    if system not in ('Linux', ) or machine not in ('i686', 'x86_64', ):
        raise AssertionError("Unsupported platform type.\n")
    # check package availability / version
    import sandbox
    if not hasattr(sandbox, '__version__') or sandbox.__version__ < "0.3.4-3":
        raise AssertionError("Unsupported sandbox version.\n")
    from sandbox import *
except ImportError:
    sys.stderr.write("Required package(s) missing.\n")
    sys.exit(os.EX_UNAVAILABLE)
except AssertionError as e:
    sys.stderr.write(str(e))
    sys.exit(os.EX_UNAVAILABLE)


def main(args):
    # sandbox configuration
    fin = open(args[1], "r")
    fout = open(args[2], "w")
    ferr = open(args[3], "w")
    config = {
        'args': args[8:],  # targeted program
        'stdin': fin,      # input to targeted program
        'stdout': fout,    # output from targeted program
        'stderr': ferr,    # error from targeted program
        'quota': dict(wallclock=int(args[4]),
                      cpu=int(args[5]),
                      memory=int(args[6]),
                      disk=int(args[7]))
        }
    # create a sandbox instance and execute till end
    msb = MiniSandbox(**config)
    msb.run()
    fin.close()
    fout.close()
    ferr.close()
    sys.stdout.write(json.dumps(msb.probe()))
    return os.EX_OK


# mini sandbox with embedded policy
class MiniSandbox(SandboxPolicy, Sandbox):
    sc_table = None
    # white list of essential linux syscalls for statically-linked C programs
    sc_safe = dict(i686=set([0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140,
        163, 192, 197, 224, 243, 252, ]), x86_64=set([0, 1, 5, 8, 9, 10,
        11, 12, 16, 25, 63, 158, 219, 231, ]), )
    # result code translation table
    result_name = dict((getattr(Sandbox, 'S_RESULT_%s' % r), r) for r in
        ('PD', 'OK', 'RF', 'RT', 'TL', 'ML', 'OL', 'AT', 'IE', 'BP'))

    def __init__(self, *args, **kwds):
        # initialize table of system call rules
        self.outpath = kwds['stdout'].name
        self.errpath = kwds['stderr'].name
        self.program = kwds['args'][0]
        self.sc_table = dict()
        if machine == 'x86_64':
            for (mode, abi) in ((0, 'x86_64'), (1, 'i686'), ):
                for scno in MiniSandbox.sc_safe[abi]:
                    self.sc_table[(scno, mode)] = self._CONT
        else:  # i686
            for scno in MiniSandbox.sc_safe[machine]:
                self.sc_table[scno] = self._CONT
        # initialize as a polymorphic sandbox-and-policy object
        SandboxPolicy.__init__(self)
        Sandbox.__init__(self, *args, **kwds)
        self.policy = self  # apply local policy rules

    def probe(self):
        # add custom entries into the probe dict
        d = Sandbox.probe(self, False)
        d['cputime'] = d['cpu_info'][0]
        d['memory'] = d['mem_info'][1]
        d['status'] = MiniSandbox.result_name.get(self.result, 'NA')
        d['outpath'] = self.outpath
        d['errpath'] = self.errpath
        d['program'] = self.program
        return d

    def __call__(self, e, a):
        # handle SYSCALL/SYSRET events with local rules
        if e.type in (S_EVENT_SYSCALL, S_EVENT_SYSRET):
            scinfo = (e.data, e.ext0) if machine == 'x86_64' else e.data
            rule = self.sc_table.get(scinfo, self._KILL_RF)
            return rule(e, a)
        # bypass other events to base class
        return SandboxPolicy.__call__(self, e, a)

    def _CONT(self, e, a):  # continue
        a.type = S_ACTION_CONT
        return a

    def _KILL_RF(self, e, a):  # restricted func.
        a.type, a.data = S_ACTION_KILL, S_RESULT_RF
        return a


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(os.EX_USAGE)
    sys.exit(main(sys.argv))
