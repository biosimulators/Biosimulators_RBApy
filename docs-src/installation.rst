Installation instructions
=========================

BioSimulators-RBApy is available as a command-line program and as a command-line program encapsulated into a Docker image.

BioSimulators-RBApy requires one of the linear programming solvers `IBM CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`_, `GLPK <https://www.gnu.org/software/glpk/>`_, or `Gurobi <https://www.gurobi.com/products/gurobi-optimizer/>`_. Note, GLPK is slower than CPLEX and Gurobi. IBM and Gurobi both provide free licenses for academic research.

Command-line program
--------------------

First, install `Python <https://python.org>`_, `Pip <https://pip.pypa.io/>`_, and optionally `IBM CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`_.

Second, run the following command to install BioSimulators-RBApy:

.. code-block:: text

    pip install biosimulators-rbapy

To use BioSimulators-RBApy with CPLEX, install BioSimulators-RBApy with the ``cplex`` option. Note, this requires CPLEX and a CPLEX license.::

    pip install rbapy[cplex]

To use BioSimulators-RBApy with GLPK, install BioSimulators-RBApy with the ``glpk`` option. Note, this requires ``libglpk-dev``.::

   pip install rbapy[glpk]

To use BioSimulators-RBApy with Gurobi, install BioSimulators-RBApy with the ``gurobi`` option. Note, this requires a Gurobi license.::

    pip install rbapy[gurobi]


Docker image with a command-line entrypoint
-------------------------------------------

After installing `Docker <https://docs.docker.com/get-docker/>`_, run the following command to install the Docker image for BioSimulators-RBApy:

.. code-block:: text

    docker pull ghcr.io/biosimulators/rbapy
