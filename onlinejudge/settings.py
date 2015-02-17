from django.conf import settings

OJ_COMPILE_COMMAND = getattr(settings, "OJ_COMPILER",
                             ("gcc -DDEBUG(...) --static %(program)s.c -lm "
                              "-o %(program)s"))
OJ_RUNNER = getattr(settings, "OJ_RUNNER", None)

#select default runner based on the system
if OJ_RUNNER is None:
    import platform
    pl = platform.system()
    if pl=="Windows":
        OJ_RUNNER = "pydevrunner.py"
    elif pl=="Linux":
        OJ_RUNNER = "pysandboxrunner.py"
    else:
        raise Exception("Unsupported OS %s" % pl)

OJ_IP_FILTER = getattr(settings, "OJ_IP_FILTER", False)
OJ_PROXY_SIGNATURE = getattr(settings, "OJ_PROXY_SIGNATURE", "")
OJ_USERS_IPS = getattr(settings, "OJ_USERS_IPS", {})
OJ_REMOTE_ADDR = getattr(settings, "OJ_REMOTE_ADDR", "")
OJ_PROGRAM_ROOT = getattr(settings, "OJ_PROGRAM_ROOT",
                          getattr(settings, "MEDIA_ROOT", "."))
