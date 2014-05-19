"""
Choose test runner class from --runner command line option
and execute test cases.
"""

import unittest
import optparse
import sys


def get_runner():
    parser = optparse.OptionParser()
    parser.add_option('--runner', default='unittest.TextTestRunner',
                                  help='name of test runner class to use')
    opts, args = parser.parse_args()

    fromsplit = opts.runner.rsplit('.', 1)
    if len(fromsplit) < 2:
        raise ValueError('Can\'t use module as a runner')
    else:
        runnermod = __import__(fromsplit[0])
    return getattr(runnermod, fromsplit[1])


def run(suite=None):
    runner = get_runner()
    if suite:
        if not runner().run(suite).wasSuccessful():
            sys.exit(1)
    else:
        unittest.main(argv=sys.argv[:1], testRunner=runner)


if __name__ == '__main__':
    run()
