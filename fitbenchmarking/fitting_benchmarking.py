
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at:
# <https://github.com/mantidproject/fitbenchmarking>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

from parsing import parse_nist, parse_neutron
from utils.logging_setup import logger
from utils import create_dirs, setup_problem_groups
from fitbenchmark_one_problem import fitbm_one_problem


def do_fitting_benchmark(data_dir, minimizers=None, use_errors=True,
                         results_dir=None):
    """
    """

    results_dir = create_dirs.results(results_dir)
    problem_groups = setup_problem_groups.mantid(data_dir)

    prob_results = None
    for group_name in problem_groups:
        group_results_dir = create_dirs.group_results(results_dir, group_name)
        prob_results = \
        [do_fitting_benchmark_group(group_name, group_results_dir, problem_bl,
                                    minimizers, use_errors=use_errors)
         for problem_bl in problem_groups[group_name]]

    return prob_results, results_dir


def do_fitting_benchmark_group(group_name, group_results_dir, problem_files,
                               minimizers, use_errors=True):
    """
    """

    results_per_problem = []
    for prob_file in problem_files:
        prob = parse_problem_file(group_name, prob_file)
        results_prob = \
        fitbm_one_problem(prob, group_results_dir, minimizers, use_errors)
        results_per_problem.extend(results_prob)

    return results_per_problem


def parse_problem_file(group_name, prob_file):
    """
    """

    if group_name in ['nist']:
        prob = parse_nist.load_data(prob_file)
    elif group_name in ['neutron']:
        prob = parse_neutron.load_data(prob_file)
    else:
        raise NameError("Could not find group name! Please check if it was"
                        "given correctly...")

    logger.info("* Testing fitting of problem {0}".format(prob.name))

    return prob

