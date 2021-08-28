Installation instructions
=========================

BioSimulators-RBApy is available as a command-line program and as a command-line program encapsulated into a Docker image.

Command-line program
--------------------

First, install `Python <https://python.org>`_, `Pip <https://pip.pypa.io/>`_, `IBM CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`_ and `RBApy <https://sysbioinra.github.io/RBApy/>`_.

Second, run the following command to install BioSimulators-RBApy:

.. code-block:: text

    pip install biosimulators-rbapy


Docker image with a command-line entrypoint
-------------------------------------------

After installing `Docker <https://docs.docker.com/get-docker/>`_, run the following command to install the Docker image for BioSimulators-RBApy:

.. code-block:: text

    docker pull ghcr.io/biosimulators/rbapy
