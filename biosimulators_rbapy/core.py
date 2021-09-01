""" BioSimulators-compliant command-line interface to the `RBApy <https://sysbioinra.github.io/RBApy/>`_ simulation program.

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-12
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from biosimulators_utils.combine.exec import exec_sedml_docs_in_archive
from biosimulators_utils.config import get_config, Config  # noqa: F401
from biosimulators_utils.log.data_model import CombineArchiveLog, TaskLog  # noqa: F401
from biosimulators_utils.model_lang.rba.validation import validate_model
from biosimulators_utils.report.data_model import ReportFormat, VariableResults, SedDocumentResults  # noqa: F401
from biosimulators_utils.sedml import validation
from biosimulators_utils.sedml.data_model import (Task, ModelLanguage, ModelAttributeChange,  # noqa: F401
                                                  SteadyStateSimulation, UniformTimeCourseSimulation,
                                                  Variable, Symbol)
from biosimulators_utils.sedml.exec import exec_sed_doc
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.utils.core import raise_errors_warnings
from biosimulators_utils.viz.data_model import VizFormat  # noqa: F401
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
import functools
import numpy
import rba

__all__ = ['exec_sedml_docs_in_combine_archive', 'exec_sed_task']


def exec_sedml_docs_in_combine_archive(archive_filename, out_dir, config=None):
    """ Execute the SED tasks defined in a COMBINE/OMEX archive and save the outputs

    Args:
        archive_filename (:obj:`str`): path to COMBINE/OMEX archive
        out_dir (:obj:`str`): path to store the outputs of the archive

            * CSV: directory in which to save outputs to files
              ``{ out_dir }/{ relative-path-to-SED-ML-file-within-archive }/{ report.id }.csv``
            * HDF5: directory in which to save a single HDF5 file (``{ out_dir }/reports.h5``),
              with reports at keys ``{ relative-path-to-SED-ML-file-within-archive }/{ report.id }`` within the HDF5 file

        config (:obj:`Config`, optional): BioSimulators common configuration

    Returns:
        :obj:`tuple`:

            * :obj:`SedDocumentResults`: results
            * :obj:`CombineArchiveLog`: log
    """
    sed_doc_executer = functools.partial(exec_sed_doc, exec_sed_task)
    return exec_sedml_docs_in_archive(sed_doc_executer, archive_filename, out_dir,
                                      apply_xml_model_changes=False,
                                      config=config)


def exec_sed_task(task, variables, log=None, config=None):
    """ Execute a task and save its results

    Args:
       task (:obj:`Task`): task
       variables (:obj:`list` of :obj:`Variable`): variables that should be recorded
       log (:obj:`TaskLog`, optional): log for the task
       config (:obj:`Config`, optional): BioSimulators common configuration

    Returns:
        :obj:`tuple`:

            :obj:`VariableResults`: results of variables
            :obj:`TaskLog`: log

    Raises:
        :obj:`NotImplementedError`:

          * Task requires a time course that RBApy doesn't support
          * Task requires an algorithm that RBApy doesn't support
    """
    config = config or get_config()

    if config.LOG and not log:
        log = TaskLog()

    # validate task
    model = task.model
    sim = task.simulation

    if config.VALIDATE_SEDML:
        raise_errors_warnings(validation.validate_task(task),
                              error_summary='Task `{}` is invalid.'.format(task.id))
        raise_errors_warnings(validation.validate_model_language(model.language, ModelLanguage.RBA),
                              error_summary='Language for model `{}` is not supported.'.format(model.id))
        raise_errors_warnings(validation.validate_model_change_types(model.changes, (ModelAttributeChange,)),
                              error_summary='Changes for model `{}` are not supported.'.format(model.id))
        raise_errors_warnings(*validation.validate_model_changes(model),
                              error_summary='Changes for model `{}` are invalid.'.format(model.id))
        raise_errors_warnings(validation.validate_simulation_type(sim, (SteadyStateSimulation, )),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))
        raise_errors_warnings(*validation.validate_simulation(sim),
                              error_summary='Simulation `{}` is invalid.'.format(sim.id))
        raise_errors_warnings(*validation.validate_data_generator_variables(variables),
                              error_summary='Data generator variables for task `{}` are invalid.'.format(task.id))

    # read model
    errors, warnings, rba_model = validate_model(model.source, name=model.id)

    raise_errors_warnings(errors, warnings,
                          error_summary='Model `{}` is invalid.'.format(model.id),
                          warning_summary='Model `{}` may be invalid.'.format(model.id))

    # validate variables
    constraint_matrix = rba.ConstraintMatrix(rba_model)

    valid_targets = ['objective']

    for name in constraint_matrix.col_names:
        valid_targets.append('variables.' + name)

    for name in constraint_matrix.row_names:
        valid_targets.append('constraints.' + name)

    invalid_variables = []
    for variable in variables:
        if variable.symbol:
            invalid_variables.append('{}: symbol: {}'.format(variable.id, variable.symbol))

        else:
            if variable.target not in valid_targets:
                invalid_variables.append('{}: target: {}'.format(variable.id, variable.target))

    if invalid_variables:
        msg = (
            'The following variables are not supported:\n  - {}'
            '\n'
            '\n'
            'Only following variable targets are supported:\n  - {}'
        ).format(
            '\n  - '.join(sorted(invalid_variables)),
            '\n  - '.join(sorted(valid_targets)),
        )
        raise ValueError(msg)

    # configure simulation algorithm
    algorithm_substitution_policy = get_algorithm_substitution_policy(config=config)
    exec_kisao_id = get_preferred_substitute_algorithm_by_ids(
        sim.algorithm.kisao_id, ['KISAO_0000669'],
        substitution_policy=algorithm_substitution_policy)

    # configure parameters of the simulation algorithm
    if sim.algorithm.changes:
        if (
            ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
            <= ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
        ):
            msg = 'No algorithm parameters are supported.'
            raise ValueError(msg)
        else:
            msg = "Algorithm changes were ignored because no algorithm parameters are supported."
            warn(msg, BioSimulatorsWarning)

    # instantiate simulation
    rba_results = rba_model.solve()

    # transform simulation results
    variable_results = VariableResults()
    for variable in variables:
        variable_type, _, rba_id = variable.target.partition('.')

        if variable_type == 'objective':
            variable_results[variable.id] = numpy.array(rba_results.mu_opt)

        elif variable_type == 'variables':
            variable_results[variable.id] = numpy.array(rba_results.variables[rba_id])

        else:
            variable_results[variable.id] = numpy.array(rba_results.dual_values[rba_id])

    # log action
    if config.LOG:
        log.algorithm = exec_kisao_id

        log.simulator_details = {}
        log.simulator_details['method'] = '{}.{}.{}'.format(rba_model.__module__, rba_model.__class__.__name__, rba_model.solve.__name__)
        log.simulator_details['lpSolver'] = rba_results._solver.lp_solver.name

    ############################
    # return the result of each variable and log
    return variable_results, log
