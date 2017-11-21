#!/usr/bin/env python
"""Nagios script to test CCI Open Data Portal CSW service
"""
__author__ = "P J Kershaw"
__date__ = "10/11/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import unittest
import logging

import nagiosplugin
from slack_logging_handler.handler import SlackHandler

log = logging.getLogger('nagiosplugin')


class UnittestCaseContext(nagiosplugin.context.Context):
    '''Nagios Context - sets tests to run and executes them'''

    def __init__(self, *args, **kwargs):
        '''Overload in order to obtain module name for unittests'''
        self._unittest_module_name = kwargs.pop('unittest_module_name', None)
        super(UnittestCaseContext, self).__init__(*args, **kwargs)

    def evaluate(self, metric, resource):
        '''Run tests from CSW unittest case'''
        # The test may be an individual one or a whole test case.  For the
        # latter, this may involve multiple tests
        test_name = metric[0]

        tests = unittest.defaultTestLoader.loadTestsFromName(test_name,
                                            module=self._unittest_module_name)

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

        return self.result_cls(status, hint=hint, metric=metric)

class UnittestCaseResource(nagiosplugin.Resource):
    '''Nagios resource abstraction for unittest case
    '''
    def __init__(self, test_names):
        '''Overload to pass special test_names parameter'''
        super(UnittestCaseResource, self).__init__()

        self.test_names = test_names

    def probe(self):
        '''Special probe method applies the metrics for the resource'''
        for test_name in self.test_names:
            yield nagiosplugin.Metric(test_name, True,
                                      context='UnittestCaseContext')


class UnittestCaseResultsSummary(nagiosplugin.Summary):
    """Present output summary
    """
    def ok(self, results):
        msg = ', '.join([result.hint for result in results])
        log.info(msg)
        return msg

    def problem(self, results):
        msg = 'Problems with test: ' + ', '.join([result.hint
                                                  for result in results])
        log.info(msg)
        return msg


@nagiosplugin.guarded
def main(unittest_module_name, unittestcase_class, slack_webhook_url=None,
         slack_channel=None, slack_user=None):
    '''Top-level function for script'''

    if slack_webhook_url is not None:
        log.addHandler(SlackHandler(slack_webhook_url,
                                    channel=slack_channel,
                                    username=slack_user))

    import sys
    import os
    if '-h' in sys.argv:
        prog_name = os.path.basename(sys.argv[0])

        test_names = ['{}.{}'.format(unittestcase_class.__name__, name_)
                          for name_ in dir(unittestcase_class)
                          if name_.startswith('test')]
        test_names_displ = '-h|{}|'.format(unittestcase_class.__name__) + \
                            '|'.join(test_names)
        raise SystemExit('Usage: {} <{}>{}'.format(prog_name,
                                                   test_names_displ,
                                                   os.linesep))

    elif len(sys.argv) > 1:
        test_names = sys.argv[1:]
    else:
        # If no explicit test names are set, pass the unit test class name -
        # This will cause all tests to be executed.
        test_names = [unittestcase_class.__name__]

    nagios_resource = UnittestCaseResource(test_names)
    nagios_context = UnittestCaseContext('UnittestCaseContext',
                                    unittest_module_name=unittest_module_name)

    nagios_results_summary = UnittestCaseResultsSummary()
    check = nagiosplugin.Check(nagios_resource, nagios_context,
                               nagios_results_summary)

    check.name = unittestcase_class.__name__
    check.main()


if __name__ == "__main__":
    SLACK_WEBHOOK_URL = #CHANGE-ME
    SLACK_CHANNEL = 'cci-odp-ops-logging'
    SLACK_USER = 'cci-ops-test'

    import ceda.cci_odp_ops_tests.test_csw
    from ceda.cci_odp_ops_tests.test_csw import CSWTestCase
    main(ceda.cci_odp_ops_tests.test_csw, CSWTestCase,
         slack_webhook_url=SLACK_WEBHOOK_URL,
         slack_channel=SLACK_CHANNEL, slack_user=SLACK_USER)
