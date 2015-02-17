from platform import system, machine
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
        16, 25, 63, 158, 186, 219, 231, ])}

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
        #kwds.update({'policy': MinimalPolicy()})
        super(DefaultSandboxRunner, self).__init__(*args, **kwds)
        #self.policy = MinimalPolicy()

    def probe(self):
        # add custom entries into the probe dict
        d = Sandbox.probe(self, False)
        d['cputime'] = d['cpu_info'][0]
        d['memory'] = d['mem_info'][1]
        d['status'] = DefaultSandboxRunner.result_name.get(self.result, 'NA')
        return d


class DefaultSandboxRunner2(SandboxPolicy, Sandbox):
    """ Default Sandbox with whitelisted system calls. """
    sc_table = None
    # white list of essential linux syscalls for statically-linked C programs
    sc_safe = dict(i686=set([0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140,
        163, 192, 197, 224, 243, 252, ]), x86_64=set([0, 1, 5, 8, 9, 10,
        11, 12, 16, 25, 63, 158, 186, 219, 231, ]), )
    # result code translation table
    result_name = dict((getattr(Sandbox, 'S_RESULT_%s' % r), r) for r in
        ('PD', 'OK', 'RF', 'RT', 'TL', 'ML', 'OL', 'AT', 'IE', 'BP'))

    def __init__(self, *args, **kwds):
        # initialize table of system call rules
        self.sc_table = {}
        if machine() == 'x86_64':
            for (mode, abi) in ((0, 'x86_64'), (1, 'i686'), ):
                for scno in DefaultSandboxRunner.sc_safe[abi]:
                    self.sc_table[(scno, mode)] = self._CONT
        else:  # i686
            for scno in DefaultSandboxRunner.sc_safe[machine()]:
                self.sc_table[scno] = self._CONT
        # initialize as a polymorphic sandbox-and-policy object
        SandboxPolicy.__init__(self)
        Sandbox.__init__(self, *args, **kwds)
        self.policy = self  # apply local policy rules
        pass

    def probe(self):
        # add custom entries into the probe dict
        d = Sandbox.probe(self, False)
        d['cputime'] = d['cpu_info'][0]
        d['memory'] = d['mem_info'][1]
        d['status'] = DefaultSandboxRunner.result_name.get(self.result, 'NA')
        return d

    def __call__(self, e, a):
        return self._KILL_RF(e, a)
        # handle SYSCALL/SYSRET events with local rules
        if e.type in (S_EVENT_SYSCALL, S_EVENT_SYSRET):
            scinfo = (e.data, e.ext0) if machine() == 'x86_64' else e.data
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

    def _KILL_RT(self, e, a): # runtime error
        a.type, a.data = S_ACTION_KILL, S_RESULT_RT
        return a

    pass
