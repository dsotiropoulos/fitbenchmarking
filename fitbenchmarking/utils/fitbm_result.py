from __future__ import (absolute_import, division, print_function)

import os

import numpy as np


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options=None, problem=None, fit_status=None,
                 chi_sq=None, fit_wks=None, params=None, errors=None,
                 runtime=None, minimizer=None, ini_function_params=None,
                 fin_function_params=None):
        self.options = options
        self.problem = problem
        self.fit_status = fit_status
        self.chi_sq = chi_sq
        self._min_chi_sq = None
        # Workspace with data to fit
        self.fit_wks = fit_wks
        self.params = params
        self.errors = errors

        # Time it took to run the Fit algorithm
        self.runtime = runtime
        self._min_runtime = None

        # Best minimizer for a certain problem and its function definition
        self.minimizer = minimizer
        self.ini_function_params = ini_function_params
        self.fin_function_params = fin_function_params

        self.value = None
        self.norm_value = None

        self.colour = None
        self.colour_runtime = None
        self.colour_acc = None

        # Defines the type of table to be produced
        self._table_type = None
        self.output_string_type = {"abs": '{:.4g}',
                                   "rel": '{:.4g}',
                                   "both": '{0:.4g} ({1:.4g})'}

        # Paths to vaious output files
        self.support_page_link = ''
        self.start_figure_link = ''
        self.figure_link = ''
        # Links will be displayed relative to this dir
        self.relative_dir = os.path.abspath(os.sep)

        # Error written to support page if plotting failed
        # Default can be overwritten with more information
        self.figure_error = 'Plotting Failed'

        # Print with html tag or not
        self.html_print = False

    def __str__(self):
        if self.table_type is not None:
            output = self.table_output
            if self.html_print:
                link = os.path.relpath(path=self.support_page_link,
                                       start=self.relative_dir)
                output = '<a href="{0}">{1}</a>'.format(link, output)
        else:
            output = 'Fitting problem class: minimizer = {0}'.format(
                self.minimizer)
        return output

    @property
    def table_type(self):
        return self._table_type

    @table_type.setter
    def table_type(self, value):
        self._table_type = value
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[comp_mode]

        if value == "runtime":
            abs_value = [self.runtime]
            rel_value = [self.norm_runtime]
            self.colour = self.colour_runtime
        elif value == "acc":
            abs_value = [self.chi_sq]
            rel_value = [self.norm_acc]
            self.colour = self.colour_acc
        elif value == "compare":
            abs_value = [self.chi_sq, self.runtime]
            rel_value = [self.norm_acc, self.norm_runtime]
            self.colour = [self.colour_acc, self.colour_runtime]

        if comp_mode == "abs":
            self.table_output = \
                '<br>'.join([result_template.format(v) for v in abs_value])
        elif comp_mode == "rel":
            self.table_output = \
                '<br>'.join([result_template.format(v) for v in rel_value])
        elif comp_mode == "both":
            self.table_output = \
                '<br>'.join([result_template.format(v1, v2)
                             for v1, v2 in zip(abs_value, rel_value)])

    def set_colour_scale(self):
        """
        Utility function set colour rendering for html tables
        """
        colour_scale = self.options.colour_scale
        colour_bounds = [colour[0] for colour in colour_scale]
        # prepending 0 value for colour bound
        colour_bounds = [0] + colour_bounds
        html_colours = [colour[1] for colour in colour_scale]
        self.colour_runtime = colour_scale[-1]
        self.colour_acc = colour_scale[-1]
        for i in range(len(colour_bounds) - 1):
            if colour_bounds[i] < self.norm_runtime <= colour_bounds[i + 1]:
                self.colour_runtime = html_colours[i]
            if colour_bounds[i] < self.norm_acc <= colour_bounds[i + 1]:
                self.colour_acc = html_colours[i]

    @property
    def min_chi_sq(self):
        return self._min_chi_sq

    @min_chi_sq.setter
    def min_chi_sq(self, value):
        self._min_chi_sq = value
        if not self.chi_sq > 0:
            self.chi_sq = np.inf
        self.norm_acc = self.chi_sq / self.min_chi_sq

    @property
    def min_runtime(self):
        return self._min_runtime

    @min_runtime.setter
    def min_runtime(self, value):
        self._min_runtime = value
        self.norm_runtime = self.runtime / self.min_runtime
