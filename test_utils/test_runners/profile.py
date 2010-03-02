import cProfile
import pstats
from django.test.simple import run_tests as django_test_runner

def run_tests(test_labels, verbosity=1, interactive=True,
        extra_tests=[], nodatabase=False):
    """
    Test runner which displays basic profile data.
    Needs some improvement, mostly here for Continuous Integration purposes.
    """
    print "Using profiling test runner"
    cProfile.runctx("django_test_runner(test_labels, verbosity, interactive, extra_tests)", globals(), locals(), filename="django_tests.profile")
    stats = pstats.Stats('django_tests.profile')
    stats.strip_dirs().sort_stats('time').print_stats(30)
    return 0
