import sys
import json
import subprocess
import time
from random import random


def main(args):
    STATUSES = ["OK", "RF", "ML", "OL", "TL", "RT", "AT"]
    #"PD", "IE", "BP",  "EX"
    cpu = int(args[5])
    fin = open(args[1], "r")
    fout = open(args[2], "w")
    ferr = open(args[3], "w")
    config = {
        'args': args[8:],  # targeted program
        'stdin': fin,      # input to targeted program
        'stdout': fout,    # output from targeted program
        'stderr': subprocess.PIPE,    # error from targeted program
        #'quota': dict(wallclock=int(args[4]),
        #              cpu=int(args[5]),
        #              memory=int(args[6]),
        #              disk=int(args[7]))
        #'bufsize' :1,
        #'close_fds': ON_POSIX,
        }
    process = subprocess.Popen(**config)
    time.sleep(cpu/1000*(random()+1))
    while process.poll() is None:
        try:
            process.kill()
        except WindowsError:
            pass
        time.sleep(0.1)
    fin.close()
    fout.close()
    ferr.close()

    # return random data
    d = {}
    d['cputime'] = int(1000*random())
    d['memory'] = int(1000*random())
    d['status'] = STATUSES[int(random()*(len(STATUSES)))]
    d['outpath'] = args[2]
    d['errpath'] = args[3]
    d['program'] = args[8]
    sys.stdout.write(json.dumps(d))
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    sys.exit(main(sys.argv))
