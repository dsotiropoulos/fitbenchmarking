.. _jacobian_extend:

####################
Adding new Jacobians
####################

*This section describes how to add further methods to approximate the
Jacobian within FitBenchmarking*

In order to add a new Jacobian evaluation method, ``<jac_method>``,
you will need to:

1. Create ``fitbenchmarking/jacobian/<jac_method>_jacobian.py``,
   which contains a new subclass of
   :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian`.
   Then implement the methods:

    -  .. automethod:: fitbenchmarking.jacobian.base_jacobian.Jacobian.eval()
              :noindex:
    -  .. automethod:: fitbenchmarking.jacobian.base_jacobian.Jacobian.eval_cost()
              :noindex:

   The numerical method is set sequentially within
   :meth:`~fitbenchmarking.core.fitting_benchmarking.loop_over_jacobians()` by
   using the ``method`` attribute of the class.

2. Document the available Jacobians by:

  * adding ``<jac_method>`` as an option in :ref:`fitting_option`.
  * adding a list of available ``method`` options to the docs for :ref:`jacobian_option`.
  * updating any example files in the ``examples`` directory

3. Create tests for the Jacobian evaluation in
   ``fitbenchmarking/jacobian/tests/test_jacobians.py``.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new Jacobian, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
and subclasses of :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, cache_model_x, data_x, data_y, data_e
          :noindex:

.. currentmodule:: fitbenchmarking.cost_func.base_cost_func
.. autoclass:: fitbenchmarking.cost_func.base_cost_func.CostFunc
          :members: eval_cost, cache_cost_x
          :noindex:


.. note::
   If using cached values, use the
   :meth:`~fitbenchmarking.jacobian.base_jacobian.Jacobian.cached_func_values` method,
   which first checks if a cached function evaluation is available to use
   for the given parameters.
