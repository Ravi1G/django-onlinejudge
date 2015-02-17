#!/usr/bin/env python
import os
import sys

from django.conf import settings

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'onlinejudge.tests.test_settings'
    #import django
    #django.setup()
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)
    failures = test_runner.run_tests(["onlinejudge.tests"])
    sys.exit(bool(failures))
