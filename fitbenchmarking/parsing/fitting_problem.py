"""
Implements the FittingProblem class, this will be the object that inputs are
parsed into before being passed to the controllers
"""

from __future__ import (absolute_import, division, print_function)

try:
    from itertools import izip_longest
except ImportError:
    # python3
    from itertools import zip_longest as izip_longest
import numpy as np


class FittingProblem:
    """
    Definition of a fitting problem, normally populated by a parser from a
    problem definition file.

    Types of data:
        - strings: name, equation
        - floats: start_x, end_x
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values, value_ranges, functions
    """

    def __init__(self):

        # Name (title) of the fitting problem
        # str
        self.name = None

        # Equation (function or model) to fit against data
        # string
        self.equation = None

        # Define range to fit model data over if different from entire range
        # of data
        # floats
        self.start_x = None
        self.end_x = None

        # The data
        # numpy array of floats
        self.data_x = None
        self.data_y = None
        self.data_e = None

        # Starting values of the fitting parameters
        # list of dict -> [{p1_name: p1_val1, p2_name: p2_val1, ...},
        #                  {p1_name: p1_val2, ...},
        #                  ...]
        self.starting_values = None
        # dict -> {p1_name: [p1_min, p1_max], ...}
        self.value_ranges = None

        # Callable function
        self.function = None

        self._param_names = None

    @property
    def param_names(self):
        """
        Utility function to get the parameter names

        :return: the neames of the parameters
        :rtype: [type]
        """
        if self._param_names is None:
            self._param_names = list(self.starting_values[0].keys())
        return self._param_names

    @param_names.setter
    def param_names(self, value):
        raise ValueError('This property should not be set manually')

    def eval_f(self, x, params):
        """
        Function evaluation method

        :param x: x data values
        :type x: numpy array
        :param params: parameter value(s)
        :type params: list

        :return: y data values evaluated from the function of the problem
        :rtype: numpy array
        """
        if self.function is None:
            raise AttributeError('Cannot call function before setting'
                                 'function.')
        return self.function(x, *params)

    def eval_starting_params(self, param_set):
        """
        Evaluate the function using the starting parameters.

        :param param_set: The index of the parameter set in starting_params
        :type param_set: int

        :return: Results from evaluation
        :rtype: numpy array
        """
        if self.starting_values is None:
            raise AttributeError('Cannot call function before setting'
                                 'starting values.')
        return self.eval_f(self.data_x,
                           self.starting_values[param_set].values())

    def get_function_def(self, params):
        """
        Return the function definition in a string format for output

        :param params: The parameters to use in the function string
        :type params: list

        :return: Representation of the function
                 example format: 'b1 * (b2+x) | b1=-2.0, b2=50.0'
        :rtype: string
        """
        params = ['{}={}'.format(n, p) for n, p
                  in izip_longest(self.param_names,
                                  params if params is not None else [])]
        param_string = ', '.join(params)

        func_name = self.equation
        return '{} | {}'.format(func_name, param_string)

    def verify(self):
        """
        Basic check that minimal set of attributes have been set.

        Raise AttributeError if object is not properly initialised.
        """

        values = {'data_x': np.ndarray,
                  'data_y': np.ndarray,
                  'starting_values': list}

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            if not isinstance(attr, attr_type):
                raise TypeError('Attribute "{}" is not the expected type.'
                                'Expected "{}", got {}.'.format(attr_name,
                                                                attr_type,
                                                                type(attr)
                                                                ))
        if self.function is None:
            raise TypeError('Attribute "function" has not been set.')
