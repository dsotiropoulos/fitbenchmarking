"""
Tests for fitbenchmarking.core.fitting_benchmarking.benchmark
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import copy
import os
import unittest
from unittest import mock

from fitbenchmarking import mock_problems
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.utils import fitbm_result
from fitbenchmarking.core.fitting_benchmarking import benchmark
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.exceptions import NoResultsError

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


def make_cost_function(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = NLLSCostFunc(fitting_problem)
    return cost_func


def dict_test(expected, actual):
    """
    Test to check two dictionaries are the same

    :param expected: expected dictionary result
    :type expected: dict
    :param actual: actual dictionary result
    :type actual: dict
    """
    for key in actual.keys():
        assert key in expected.keys()
        assert sorted(actual[key]) == sorted(expected[key])


class BenchmarkTests(unittest.TestCase):
    """
    benchmark tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.cost_func = make_cost_function()
        self.problem = self.cost_func.problem
        self.options = Options()
        self.options.software = ["scipy"]
        self.scipy_len = len(self.options.minimizers["scipy"])
        bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
        self.default_parsers_dir = os.path.join(bench_prob_dir,
                                                "default_parsers")
        self.all_minimzers = copy.copy(self.options.minimizers)

    def shared_tests(self, expected_names, expected_unselected_minimzers,
                     expected_minimzers):
        """
        Shared tests for the `benchmark` function. The function test

        :param expected_names: expected sorted list of problem names
        :type expected_names: list
        :param expected_unselected_minimzers: expected unselected minimizers
        :type expected_unselected_minimzers: dict
        :param expected_minimzers: expected minimizers
        :type expected_minimzers: dict
        """
        results, failed_problems, unselected_minimzers = \
            benchmark(self.options, self.default_parsers_dir)

        assert len(results) == len(expected_names)
        for i, name in enumerate(expected_names):
            assert all(p.name == name for p in results[i])

        assert failed_problems == []
        dict_test(expected_unselected_minimzers, unselected_minimzers)
        dict_test(expected_minimzers, self.options.minimizers)

    @mock.patch('{}.loop_over_benchmark_problems'.format(FITTING_DIR))
    def test_check_no_unselected_minimizers(self,
                                            loop_over_benchmark_problems):
        """
        Checks benchmarking runs with no unselected minimizers
        """
        # define mock return for loop_over_benchmark_problems
        problem_names = ["random_1", "random_3", "random_2"]
        results = []
        for name in problem_names:
            result_args = {'options': self.options,
                           'cost_func': self.cost_func,
                           'jac': 'jac',
                           'initial_params': self.problem.starting_values[0],
                           'params': [],
                           'chi_sq': 1,
                           'name': name}
            list_results = [fitbm_result.FittingResult(**result_args)
                            for j in range(self.scipy_len)]
            results.extend(list_results)
        problem_fails = []
        expected_problem_names = sorted(problem_names)
        expected_minimzers = copy.copy(self.all_minimzers)
        expected_unselected_minimzers = {"scipy": []}
        loop_over_benchmark_problems.return_value = \
            (results, problem_fails, expected_unselected_minimzers,
             expected_minimzers)

        # run shared test and see if it match expected
        self.shared_tests(expected_problem_names,
                          expected_unselected_minimzers,
                          expected_minimzers)

    @mock.patch('{}.loop_over_benchmark_problems'.format(FITTING_DIR))
    def test_check_unselected_minimizers(self, loop_over_benchmark_problems):
        """
        Checks benchmarking runs with a few unselected minimizers
        """
        # define mock return for loop_over_benchmark_problems
        problem_names = ["random_1", "random_3", "random_2"]
        expected_names = sorted(problem_names)
        results = []
        for name in problem_names:
            result_args = {'options': self.options,
                           'cost_func': self.cost_func,
                           'jac': 'jac',
                           'initial_params': self.problem.starting_values[0],
                           'params': [],
                           'chi_sq': 1,
                           'name': name}
            list_results = [fitbm_result.FittingResult(**result_args)
                            for j in range(self.scipy_len)]
            results.extend(list_results)

        problem_fails = []
        expected_unselected_minimzers = {"scipy": ['SLSQP', 'Powell', 'CG']}

        # run shared test and see if it match expected
        expected_minimzers = copy.copy(self.all_minimzers)
        for keys, minimzers in expected_unselected_minimzers.items():
            expected_minimzers[keys] = \
                list(set(expected_minimzers[keys]) - set(minimzers))

        loop_over_benchmark_problems.return_value = \
            (results, problem_fails, expected_unselected_minimzers,
             expected_minimzers)

        self.shared_tests(expected_names, expected_unselected_minimzers,
                          expected_minimzers)


if __name__ == "__main__":
    unittest.main()
