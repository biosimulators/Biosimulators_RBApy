Tutorial
========

BioSimulators-RBApy is available as a command-line program and as a command-line program encapsulated into a Docker image.


Creating COMBINE/OMEX archives and encoding simulation experiments into SED-ML
------------------------------------------------------------------------------

Information about how to create COMBINE/OMEX archives which can be executed by BioSimulators-RBApy is available at `BioSimulators <https://biosimulators.org/help>`_.

A list of the algorithms and algorithm parameters supported by RBApy is available at `BioSimulators <https://biosimulators.org/simulators/rbapy>`_.


Models (RBApy)
^^^^^^^^^^^^^^

BioSimulators-RBApy can execute models encoded in `RBApy format <https://sysbioinra.github.io/RBApy/usage.html>`_ (``urn:sedml:language:rba``).


Simulation experiments (SED-ML, KISAO)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

BioSimulators-RBApy can execute simulation experiments encoded in SED-ML, using KiSAO to indicate specific algorithms and their parameters. Information about the algorithms (KiSAO terms), algorithm parameters (KiSAO terms), and outputs supported by BioSimulators-RBApy is available from the `BioSimulators registry <https://biosimulators.org/simulators/rbapy>`_.


Models (``sedml.Model``)
""""""""""""""""""""""""

The TSV and XML files for a model should be packaged into a zip archive and specified using language URN ``urn:sedml:language:rba``::

    <model id="model" language="urn:sedml:language:rba" source="model.zip" />


Targets for model changes (``sedml.AttributeChange``)
"""""""""""""""""""""""""""""""""""""""""""""""""""""
Targets for changes to model parameters should be encoded using the name of the parameter as ``target="parameters.functions.{ function id }.parameters.{ parameter id }"`` such as ``target="parameters.functions.LINEAR_CONSTANT.parameters.amino_acid_concentration"``.::

    <attributeChange target=""parameters.functions.LINEAR_CONSTANT.parameters.amino_acid_concentration" newValue="0.25" />


Simulations (``sedml.SteadyState``, ``sedml.Algorithm``)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

RBA simulations should be encoded using the ``SteadyState`` class with simulation algorithm ``KISAO_0000669``::

    <steadyState id="simulation">
      <algorithm kisaoID="KISAO:0000669" />
    </steadyState>


Targets for observables (``sedml.Variable`` of ``sedml.DataGenerator``)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Targets for objectives should be encoded as ``target="objective"``::

    <dataGenerator id="data_generator_objective">
      <math xmlns="http://www.w3.org/1998/Math/MathML">
        <ci> variable_objective </ci>
      </math>
      <listOfVariables>
        <variable id="variable_objective" target="objective" taskReference="task"/>
      </listOfVariables>
    </dataGenerator>

Targets for the primals of variables should be encoded using the names of the variables as ``target="variables.{ variable name }"`` such as ``target="variables.M_e1_c"``.::

    <dataGenerator id="data_generator_M_e1_c">
      <math xmlns="http://www.w3.org/1998/Math/MathML">
        <ci> variable_M_e1_c </ci>
      </math>
      <listOfVariables>
        <variable id="variable_M_e1_c" target="variables.M_e1_c" taskReference="task"/>
      </listOfVariables>
    </dataGenerator>

Targets for the duals of constraints should be encoded using the names of the constraints as ``target="constraints.{ contraint name }"`` such as ``target="constraints.test_process_2_machinery"``.::

    <dataGenerator id="data_generator_test_process_2_machinery">
      <math xmlns="http://www.w3.org/1998/Math/MathML">
        <ci> variable_test_process_2_machinery </ci>
      </math>
      <listOfVariables>
        <variable id="variable_test_process_2_machinery" target="constraints.test_process_2_machinery" taskReference="task"/>
      </listOfVariables>
    </dataGenerator>


Example COMBINE/OMEX archives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Examples of COMBINE/OMEX archives for simulations which BioSimulators-RBApy can execute are available in the `BioSimulators test suite <https://github.com/biosimulators/Biosimulators_test_suite/tree/deploy/examples>`_.


Command-line program
--------------------

The command-line program can be used to execute COMBINE/OMEX archives that describe simulations as illustrated below.

.. code-block:: text

    usage: biosimulators-rbapy [-h] [-d] [-q] -i ARCHIVE [-o OUT_DIR] [-v]

    BioSimulators-compliant command-line interface to the RBApy <https://sysbioinra.github.io/RBApy/> simulation program.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           full application debug mode
      -q, --quiet           suppress all console output
      -i ARCHIVE, --archive ARCHIVE
                            Path to OMEX file which contains one or more SED-ML-
                            encoded simulation experiments
      -o OUT_DIR, --out-dir OUT_DIR
                            Directory to save outputs
      -v, --version         show program's version number and exit

For example, the following command could be used to execute the simulations described in ``./modeling-study.omex`` and save their results to ``./``:

.. code-block:: text

    biosimulators-rbapy -i ./modeling-study.omex -o ./


Docker image with a command-line entrypoint
-------------------------------------------

The entrypoint to the Docker image supports the same command-line interface described above.

For example, the following command could be used to use the Docker image to execute the same simulations described in ``./modeling-study.omex`` and save their results to ``./``:

.. code-block:: text

    docker run \
        --tty \
        --rm \
        --mount type=bind,source="$(pwd),target=/tmp/working-dir \
        ghcr.io/biosimulators/rbapy:latest \
            -i /tmp/working-dir/modeling-study.omex \
            -o /tmp/working-dir


Using BioSimulators-RBApy with a Gurobi license
-----------------------------------------------

Gurobi licenses can be used either by setting environment variables prefixed with ``GRB_`` or by saving your license to your home directory (``~/gurobi.lic``) or the appropriate location for your OS (e.g., ``/opt/gurobi/gurobi.lic`` for Linux).
