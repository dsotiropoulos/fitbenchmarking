"""
Miscellaneous functions and utilities used in fitting benchmarking.
"""

from __future__ import absolute_import, division, print_function

import glob
import os

from utils import options, user_input
from utils.logging_setup import logger


def get_minimizers(software_options):
    """
    Gets an array of minimizers to fitbenchmark from the json file depending
    on which software is used.
    @param software_options :: dictionary containing software used in fitting
                               the problem and list of minimizers or location
                               of json file contain minimizers
    @returns :: an array of strings containing minimizer names and software used
    """
    if not isinstance(software_options, dict):
        raise ValueError('software_options must be a dictionary')

    try:
        software = software_options['software']
        minimizer_options = software_options['minimizer_options']
    except KeyError:
        raise ValueError('software_options required to be a dictionary with '
                         'keys software and minimizer_options')

    if minimizer_options is None:
        options_file = software_options.get('options_file', None)
        if options_file is None:
            minimizers_list = options.get_option(option='minimizers')
        else:
            minimizers_list = options.get_option(options_file=options_file, option='minimizers')
    elif isinstance(minimizer_options, dict):
        minimizers_list = minimizer_options
    else:
        raise ValueError('minimizer_options required to be None '
                         'or dictionary, type(minimizer_options) '
                         '= {}'.format(type(minimizer_options)))

    if not isinstance(software, list):
        return minimizers_list.get(software, []), software
    else:
        minimizers = []
        for x in software:
            minimizers.append(minimizers_list.get(x, []))
        return minimizers, software


def setup_fitting_problems(data_dir):
    """
    Sets up a problem group specified by the user by providing
    a respective data directory.

    @param data_dir :: full path of a directory that holds a group of problem definition files
    @returns :: array containing blocks of paths to the problems
                e.g. In NIST we would have
                [[low_difficulty/..., ...], [average_difficulty/..., ...], ...]
    """

    return get_problem_files(data_dir)


def save_user_input(software, minimizers, group_name, results_dir, use_errors):
    """
    All parameters inputed by the user are stored in an object.
    @params :: please check the user_input.py file in the utils dir.
    @returns :: an object containing all the information specified by the user.
    """
    if isinstance(software, str):
        uinput = user_input.UserInput(software, minimizers, group_name,
                                      results_dir, use_errors)
    elif isinstance(software, list):
        uinput = []
        for i in range(len(software)):
            uinput.append(user_input.UserInput(software[i], minimizers[i],
                                               group_name,
                                               results_dir, use_errors))
    else:
        raise TypeError('Software input required to be a string or list')
    return uinput


def get_problem_files(data_dir):
    """
    Gets all the problem definition files from the specified problem set directory.

    @param data_dir :: directory containing the problems

    @returns :: array containing blocks of paths to the problems
                e.g. In NIST we would have
                [[low_difficulty/..., ...], [average_difficulty/..., ...], ...]
    """
    probs_all = []
    dirs = filter(os.path.isdir, os.listdir(data_dir))
    if dirs == [] or dirs == ['data_files']:
        dirs.insert(0, data_dir)
    for directory in dirs:
        test_data = glob.glob(directory + '/*.*')
        problems = [os.path.join(directory, data) for data in test_data]
        problems.sort()
        for problem in problems:
            logger.info(problem)
        probs_all.append(problems)

    return probs_all
