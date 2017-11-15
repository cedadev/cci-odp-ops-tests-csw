#!/usr/bin/env python
"""Nagios script to test CCI Open Data Portal CSW service
"""
from ceda.cci_odp_ops_tests.test_csw import CSWTestCase
__author__ = "P J Kershaw"
__date__ = "10/11/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import unittest
import logging

import nagiosplugin

import ceda.cci_odp_ops_tests.test_csw

log = logging.getLogger(__name__)


class CciCswNagiosCtx(nagiosplugin.context.Context):
    '''Nagios Context - sets tests to run and executes them'''
    def evaluate(self, metric, resource):
        '''Run tests from CSW unittest case'''
        # The test may be an individual one or a whole test case.  For the
        # latter, this may involve multiple tests
        test_name = metric[0]

        tests = unittest.defaultTestLoader.loadTestsFromName(test_name,
                                        module=ceda.cci_odp_ops_tests.test_csw)

        result = unittest.TestResult()
        tests.run(result)
        n_failures = len(result.failures)
        n_errors = len(result.errors)
        n_problems = n_failures + n_errors

        # If the whole test case is run then multiple tests will be executed
        # so need to cater for multiple results:
        if n_problems > 0:
            if result.testsRun == n_problems:
                # Overall fail
                status = nagiosplugin.context.Critical
                hint = 'All tests failed: '
            else:
                # Overall warning
                status = nagiosplugin.context.Warn
                hint = 'Some tests failed: '

            # Pass text for first error in the hint
            if n_errors:
                hint += str(result.errors[0][0])
            elif n_failures:
                hint += str(result.failures[0][0])

            # Log all the rest
            for error in result.errors:
                log.error(error[0])
                log.error(error[1])

            # Log all the rest
            for failure in result.failures:
                log.error(failure[0])
                log.error(failure[1])
        else:
            # Overall pass
            status = nagiosplugin.context.Ok
            hint = '{} test passed'.format(test_name)

        return self.result_cls(status, metric=metric)

class CciCSW(nagiosplugin.Resource):
    '''Nagios resource abstraction - CCI CSW in this case
    '''
    def __init__(self, test_names):
        '''Overload to pass special test_names parameter'''
        super(CciCSW, self).__init__()

        if test_names is None:
            self.test_names = ['CSWTestCase']
        else:
            self.test_names = test_names

    def probe(self):
        '''Special probe method applies the metrics for the resource'''
        for test_name in self.test_names:
            log.info('Running {}'.format(test_name))
            yield nagiosplugin.Metric(test_name, True, context='CciCswCtx')


class CciCswTestResultsSummary(nagiosplugin.Summary):
    """Present output summary
    """
    def ok(self, results):
        return ', '.join([result.hint for result in results])

    def problem(self, results):
        return 'Problems with test: ' + ', '.join([result.hint
                                                     for result in results])


@nagiosplugin.guarded
def main():
    '''Top-level function for script'''
    import sys
    import os
    if '-h' in sys.argv:
        prog_name = os.path.basename(sys.argv[0])
        csw_test_names = ['CSWTestCase.{}'.format(name_)
                          for name_ in dir(CSWTestCase)
                          if name_.startswith('test')]
        csw_test_names_displ = '-h|CSWTestCase|' + '|'.join(csw_test_names)
        raise SystemExit('Usage: {} <{}>{}'.format(prog_name,
                                                 csw_test_names_displ,
                                                 os.linesep))

    elif len(sys.argv) > 1:
        test_names = sys.argv[1:]
    else:
        test_names = None

    check = nagiosplugin.Check(CciCSW(test_names),
                               CciCswNagiosCtx('CciCswCtx'),
                               CciCswTestResultsSummary())
    check.name = 'CCI-CSW'
    check.main()


if __name__ == "__main__":
    main()
