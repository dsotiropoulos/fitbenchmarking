"""
This file implements a parser for the Fitbenchmark data format.
"""

from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict

import numpy as np
import os

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.logging_setup import logger

import_success = {}
try:
    import mantid.simpleapi as msapi
    import_success['mantid'] = True
except ImportError:
    import_success['mantid'] = False


try:
    from sasmodels.data import load_data, empty_data1D
    from sasmodels.core import load_model
    from sasmodels.bumps_model import Experiment, Model
    import_success['sasview'] = True
except ImportError:
    import_success['sasview'] = False


class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def parse(self):
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        fitting_problem = FittingProblem()

        self._entries = self._get_data_problem_entries()
        software = self._entries['software'].lower()
        if (software not in import_success) or (not import_success[software]):
            raise ImportError('Could not import necessary modules for software'
                              ' ({})'.format(software))

        self._parsed_func = self._parse_function()

        # NAME
        fitting_problem.name = self._entries['name']

        # DATA
        if software == 'mantid':
            data_points = self._get_mantid_data_points()

            fitting_problem.data_x = data_points[:, 0]
            fitting_problem.data_y = data_points[:, 1]
            if data_points.shape[1] > 2:
                fitting_problem.data_e = data_points[:, 2]
        elif software == 'sasview':
            data_file_path = self._get_data_file()
            data_obj = load_data(data_file_path)

            fitting_problem.data_x = data_obj.x
            fitting_problem.data_y = data_obj.y

        # FUNCTION
        if software == 'mantid':
            fitting_problem.function = self._create_mantid_function()
        elif software == 'sasview':
            fitting_problem.function = self._create_sasview_function()

        # EQUATION
        equation_count = len(self._parsed_func)
        if equation_count == 1:
            fitting_problem.equation = self._parsed_func[0]['name']
        else:
            fitting_problem.equation = '{} Functions'.format(equation_count)

        if software == 'mantid':
            # String containing the function name(s) and the starting parameter
            # values for each function
            fitting_problem._mantid_equation = self._entries['function']

        # STARTING VALUES
        fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        vr = self._parse_range('parameter_ranges')
        fitting_problem.value_ranges = vr if vr != {} else None

        # FIT RANGES
        fit_ranges = self._parse_range('fit_ranges')
        try:
            fitting_problem.start_x = fit_ranges['x'][0]
            fitting_problem.end_x = fit_ranges['x'][1]
        except KeyError:
            pass

        return fitting_problem

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a FitBenchmark
        definition file, where the data_file is searched for in the directory
        of the definition file and subfolders of this file

        :returns: (full) path to a data file. Return None if not found
        :rtype: str or None
        """
        data_file = None
        data_file_name = self._entries['input_file']
        # find or search for path for data_file_name
        for root, _, files in os.walk(os.path.dirname(self._filename)):
            for name in files:
                if data_file_name == name:
                    data_file = os.path.join(root, data_file_name)

        if data_file is None:
            logger.error("Data file %s not found", data_file_name)

        return data_file

    def _get_data_problem_entries(self):
        """
        Get the problem entries from a problem definition file.

        :returns: The entries from the file with string values
        :rtype: dict
        """

        entries = {}
        for line in self.file.readlines():
            # Discard comments
            line = line.split('#', 1)[0]
            if line.strip() == '':
                continue

            lhs, rhs = line.split("=", 1)
            entries[lhs.strip()] = rhs.strip().strip('"').strip("'")

        return entries

    def _parse_function(self):
        """
        Get the params from the function as a list of dicts from the data
        file.

        :return: Function definition in format:
                 [{name1: value1, name2: value2, ...}, ...]
        :rtype: list of dict
        """
        function_def = []

        functions = self._entries['function'].split(';')

        for f in functions:
            params_dict = OrderedDict()
            # To handle brackets, must split on comma or split after an
            # opening backet
            tmp_params_list = f.split(',')
            if '(' in f:
                params_list = []
                for p in tmp_params_list:
                    if '(' in p:
                        vals = [v+'(' for v in p.split('(', 1)]
                        vals[-1] = vals[-1][:-1]
                        params_list.extend(vals)
                    else:
                        params_list.append(p)
            else:
                params_list = tmp_params_list

            pop_stack = False
            stack = [params_dict]
            for p in params_list:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()

                if val == '(':
                    val = OrderedDict()
                    stack[-1][name] = val
                    stack += [val]
                    continue

                elif val[-1] == ')':
                    pop_stack = val.count(')')
                    if len(stack) <= pop_stack:
                        raise ValueError('Could not parse.'
                                         + 'Check parentheses in input')
                    val = val.strip(')')

                # Parse to an int/float if possible else assume string
                tmp_val = None
                for t in [int, float]:
                    if tmp_val is None:
                        try:
                            tmp_val = t(val)
                        except ValueError:
                            pass

                if tmp_val is not None:
                    val = tmp_val

                stack[-1][name] = val

                if pop_stack > 0:
                    stack = stack[:-pop_stack]
                    pop_stack = 0

            function_def.append(params_dict)

        return function_def

    def _get_starting_values(self):
        """
        Get the starting values for the problem

        :returns: Starting values for the function
        :rtype: list of OrderedDict
        """
        ignore = ['name', 'BinWidth', 'ties', 'Formula']

        name_template = '{1}' if len(self._parsed_func) == 1 else 'f{0}_{1}'
        starting_values = [
            OrderedDict([(name_template.format(i, name), val)
                         for i, f in enumerate(self._parsed_func)
                         for name, val in f.items()
                         if name not in ignore])]

        return starting_values

    def _parse_range(self, key):
        """
        Parse a range string for the problem into a dict

        :param key: The key in self._entries to parse
        :type key: string

        :return: The ranges in a dictionary with key as the var and value as a
                 list with min and max
                 e.g. {'x': [0, 10]}
        :rtype: dict
        """
        if key not in self._entries:
            return {}

        output_ranges = {}
        range_str = self._entries[key].strip('{').strip('}')
        tmp_ranges = range_str.split(',')
        ranges = []
        cur_str = ''
        for r in tmp_ranges:
            cur_str += r
            balanced = True
            for lb, rb in ['[]', '{}', '()']:
                if cur_str.count(lb) > cur_str.count(rb):
                    balanced = False
                elif cur_str.count(lb) < cur_str.count(rb):
                    raise ValueError('Could not parse {}: {}'.format(key, r))
            if balanced:
                ranges.append(cur_str)
                cur_str = ''
            else:
                cur_str += ','

        for r in ranges:
            name, val = r.split(':')
            name = name.strip().strip('"').strip("'").lower()

            # Strip off brackets and split on comma
            val = val.strip(' ')[1:-1].split(',')
            val = [v.strip() for v in val]
            try:
                pair = [float(val[0]), float(val[1])]
            except ValueError:
                raise ValueError('Could not parse {}: {}'.format(key, r))

            if pair[0] >= pair[1]:
                raise ValueError('Could not parse {}: {}'.format(key, r))

            output_ranges[name] = pair

        return output_ranges

    def _create_mantid_function(self):
        """
        Processing the function in the FitBenchmark problem definition into a
        python callable.

        :returns: A callable function
        :rtype: callable
        """
        fit_function = None

        for f in self._parsed_func:
            name = f['name']
            params = f.copy()
            for key in ['name', 'ties']:
                if key in params:
                    params.pop(key)
            tmp_function = msapi.__dict__[name](**params)
            if fit_function is None:
                fit_function = tmp_function
            else:
                fit_function += tmp_function

        for i, f in enumerate(self._parsed_func):
            if 'ties' in f:
                ties = {'f{}.{}'.format(i, tie): val
                        for tie, val in f['ties'].items()}
                fit_function.tie(ties)

        return fit_function

    def _create_sasview_function(self):
        """
        Creates callable function

        :return: the model
        :rtype: callable
        """
        equation = self._parsed_func[0]['name']
        starting_values = self._get_starting_values()
        value_ranges = self._parse_range('parameter_ranges')
        param_names = starting_values[0].keys()

        def fitFunction(x, *tmp_params):

            model = load_model(equation)

            data = empty_data1D(x)
            param_dict = {name: value
                          for name, value
                          in zip(param_names, tmp_params)}

            model_wrapper = Model(model, **param_dict)
            if value_ranges is not None:
                for name, values in value_ranges.items():
                    model_wrapper.__dict__[name].range(values[0], values[1])
            func_wrapper = Experiment(data=data, model=model_wrapper)

            return func_wrapper.theory()

        return fitFunction

    def _get_mantid_data_points(self):
        """
        Get the data points of the problem from the mantid data file.

        :return: data points
        :rtype: np.ndarray
        """

        data_file_path = self._get_data_file()

        with open(data_file_path, 'r') as f:
            data_text = f.readlines()

        first_row = data_text[2].strip()
        dim = len(first_row.split())
        data_points = np.zeros((len(data_text)-2, dim))

        for idx, line in enumerate(data_text[2:]):
            point_text = line.split()
            point = [float(val) for val in point_text]
            data_points[idx, :] = point

        return data_points
