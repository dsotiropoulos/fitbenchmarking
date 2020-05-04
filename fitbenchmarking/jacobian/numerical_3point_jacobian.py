from abc import ABCMeta, abstractmethod

import numpy as np
"""
Module which calculates SciPy 3 point finite difference approximation
"""
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian


class ScipyThreePoint(Jacobian):
    """
    Implements SciPy 3 point finite difference approximation to the derivative
    """
    __metaclass__ = ABCMeta

    def __init__(self, problem):
        super(ScipyThreePoint, self).__init__(problem)

    def eval(self, params, func=None, **kwargs):
        """
        Evaluates Jacobian

        :param params: The parameter values to find the Jacobian at
        :type params: list
        :param func: Function to find the Jacobian for, defaults to
                     problem.eval_r
        :type func: Callable, optional

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        if func is None:
            func = self.problem.eval_r

        jac = approx_derivative(func, params, method="3-point",
                                rel_step=None, f0=func(params, **kwargs),
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
