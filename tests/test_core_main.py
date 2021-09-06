""" Tests of the command-line interface

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-12
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from biosimulators_rbapy import __main__
from biosimulators_rbapy import core
from biosimulators_utils.combine import data_model as combine_data_model
from biosimulators_utils.combine.io import CombineArchiveWriter
from biosimulators_utils.config import get_config
from biosimulators_utils.report import data_model as report_data_model
from biosimulators_utils.report.io import ReportReader
from biosimulators_utils.sedml import data_model as sedml_data_model
from biosimulators_utils.sedml.io import SedmlSimulationWriter
from biosimulators_utils.sedml.utils import append_all_nested_children_to_doc
from biosimulators_utils.warnings import BioSimulatorsWarning
from kisao.exceptions import AlgorithmCannotBeSubstitutedException
from unittest import mock
import json
import numpy
import numpy.testing
import os
import shutil
import tempfile
import unittest
import yaml


class CliTestCase(unittest.TestCase):
    EXAMPLE_MODEL_FILENAME = os.path.join(os.path.dirname(__file__), 'fixtures', 'Escherichia-coli-K12-WT.zip')
    SPECIFICATIONS_FILENAME = os.path.join(os.path.dirname(__file__), '..', 'biosimulators.json')
    DOCKER_IMAGE = 'ghcr.io/biosimulators/biosimulators_rbapy/rbapy:latest'

    def setUp(self):
        self.dirname = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_exec_sed_task_successfully(self):
        # configure simulation
        task = sedml_data_model.Task(
            model=sedml_data_model.Model(
                source=self.EXAMPLE_MODEL_FILENAME,
                language=sedml_data_model.ModelLanguage.RBA.value,
            ),
            simulation=sedml_data_model.SteadyStateSimulation(
                algorithm=sedml_data_model.Algorithm(
                    kisao_id='KISAO_0000669',
                ),
            ),
        )

        variables = [
            sedml_data_model.Variable(
                id='objective',
                target='objective',
                task=task),
            sedml_data_model.Variable(
                id='R_EX_pqq_e',
                target="variables.R_EX_pqq_e",
                task=task),
            sedml_data_model.Variable(
                id='M_pqq_p',
                target="constraints.M_pqq_p",
                task=task),
        ]

        # execute simulation
        variable_results, log = core.exec_sed_task(task, variables)

        # check that the simulation was executed correctly
        self.assertEqual(set(variable_results.keys()), set(['objective', 'R_EX_pqq_e', 'M_pqq_p']))
        for variable_result in variable_results.values():
            self.assertFalse(numpy.isnan(variable_result))
        numpy.testing.assert_allclose(
            variable_results['objective'],
            0.6086182594299316,
        )

        # check that log can be serialized to JSON
        self.assertEqual(log.algorithm, 'KISAO_0000669')
        self.assertEqual(log.simulator_details['method'], 'rba.model.RbaModel.solve')
        self.assertIn(log.simulator_details['lpSolver'], ['cplex', 'glpk', 'glpk_exact', 'gurobi', 'scipy'])

        json.dumps(log.to_json())

        log.out_dir = self.dirname
        log.export()
        with open(os.path.join(self.dirname, get_config().LOG_PATH), 'rb') as file:
            log_data = yaml.load(file, Loader=yaml.Loader)
        json.dumps(log_data)

    def test_exec_sed_task_error_handling_invalid_variable(self):
        # configure simulation
        task = sedml_data_model.Task(
            model=sedml_data_model.Model(
                source=self.EXAMPLE_MODEL_FILENAME,
                language=sedml_data_model.ModelLanguage.RBA.value,
            ),
            simulation=sedml_data_model.SteadyStateSimulation(
                algorithm=sedml_data_model.Algorithm(
                    kisao_id='KISAO_0000019',
                ),
            ),
        )

        variables = [
            sedml_data_model.Variable(
                id='time',
                symbol=sedml_data_model.Symbol.time.value,
                task=task),
            sedml_data_model.Variable(
                id='undefined',
                target='variables.__undefined__',
                task=task),
        ]

        # execute simulation
        with self.assertRaises(ValueError):
            core.exec_sed_task(task, variables)

    def test_exec_sed_task_alt_alg(self):
        # configure simulation
        task = sedml_data_model.Task(
            model=sedml_data_model.Model(
                source=self.EXAMPLE_MODEL_FILENAME,
                language=sedml_data_model.ModelLanguage.RBA.value,
            ),
            simulation=sedml_data_model.SteadyStateSimulation(
                algorithm=sedml_data_model.Algorithm(
                    kisao_id='KISAO_0000019',
                ),
            ),
        )

        variables = [
            sedml_data_model.Variable(
                id='objective',
                target='objective',
                task=task),
        ]

        # execute simulation
        with self.assertRaises(AlgorithmCannotBeSubstitutedException):
            core.exec_sed_task(task, variables)

        task.simulation.algorithm.kisao_id = 'KISAO_0000669'
        task.simulation.algorithm.changes.append(sedml_data_model.AlgorithmParameterChange(kisao_id='KISAO_0000488', new_value='1'))
        with mock.patch.dict('os.environ', {'ALGORITHM_SUBSTITUTION_POLICY': 'NONE'}):
            with self.assertRaises(ValueError):
                core.exec_sed_task(task, variables)

        with mock.patch.dict('os.environ', {'ALGORITHM_SUBSTITUTION_POLICY': 'SIMILAR_VARIABLES'}):
            with self.assertWarns(BioSimulatorsWarning):
                core.exec_sed_task(task, variables)

    def test_exec_sedml_docs_in_combine_archive_successfully(self):
        doc, archive_filename = self._build_combine_archive()

        out_dir = os.path.join(self.dirname, 'out')
        _, log = core.exec_sedml_docs_in_combine_archive(archive_filename, out_dir)
        if log.exception:
            raise log.exception

        self._assert_combine_archive_outputs(doc, out_dir)

    def _build_combine_archive(self, algorithm=None):
        doc = self._build_sed_doc(algorithm=algorithm)

        archive_dirname = os.path.join(self.dirname, 'archive')
        if not os.path.isdir(archive_dirname):
            os.mkdir(archive_dirname)

        model_filename = os.path.join(archive_dirname, 'model.zip')
        shutil.copyfile(self.EXAMPLE_MODEL_FILENAME, model_filename)

        sim_filename = os.path.join(archive_dirname, 'sim.sedml')
        SedmlSimulationWriter().run(doc, sim_filename)

        archive = combine_data_model.CombineArchive(
            contents=[
                combine_data_model.CombineArchiveContent(
                    'model.zip', combine_data_model.CombineArchiveContentFormat.RBA.value),
                combine_data_model.CombineArchiveContent(
                    'sim.sedml', combine_data_model.CombineArchiveContentFormat.SED_ML.value),
            ],
        )
        archive_filename = os.path.join(self.dirname, 'archive.omex')
        CombineArchiveWriter().run(archive, archive_dirname, archive_filename)

        return (doc, archive_filename)

    def _build_sed_doc(self, algorithm=None):
        if algorithm is None:
            algorithm = sedml_data_model.Algorithm(
                kisao_id='KISAO_0000669',
            )

        doc = sedml_data_model.SedDocument()
        doc.models.append(sedml_data_model.Model(
            id='model',
            source='model.zip',
            language=sedml_data_model.ModelLanguage.RBA.value,
        ))
        doc.simulations.append(sedml_data_model.SteadyStateSimulation(
            id='sim_steady_state',
            algorithm=algorithm,
        ))

        doc.tasks.append(sedml_data_model.Task(
            id='task_1',
            model=doc.models[0],
            simulation=doc.simulations[0],
        ))

        doc.data_generators.append(sedml_data_model.DataGenerator(
            id='data_gen_objective',
            variables=[
                sedml_data_model.Variable(
                    id='var_objective',
                    target='objective',
                    task=doc.tasks[0],
                ),
            ],
            math='var_objective',
        ))

        doc.outputs.append(sedml_data_model.Report(
            id='report',
            data_sets=[
                sedml_data_model.DataSet(id='data_set_objective', label='Objective', data_generator=doc.data_generators[0]),
            ],
        ))

        append_all_nested_children_to_doc(doc)

        return doc

    def _assert_combine_archive_outputs(self, doc, out_dir):
        self.assertEqual(set(['reports.h5']).difference(set(os.listdir(out_dir))), set())

        report = ReportReader().run(doc.outputs[0], out_dir, 'sim.sedml/report', format=report_data_model.ReportFormat.h5)

        self.assertEqual(sorted(report.keys()), sorted([d.id for d in doc.outputs[0].data_sets]))

        numpy.testing.assert_allclose(report[doc.outputs[0].data_sets[0].id], 0.6086182594299316)

    def test_exec_sedml_docs_in_combine_archive_with_cli(self):
        doc, archive_filename = self._build_combine_archive()
        out_dir = os.path.join(self.dirname, 'out')
        env = self._get_combine_archive_exec_env()

        with mock.patch.dict(os.environ, env):
            with __main__.App(argv=['-i', archive_filename, '-o', out_dir]) as app:
                app.run()

        self._assert_combine_archive_outputs(doc, out_dir)

    def _get_combine_archive_exec_env(self):
        return {
            'REPORT_FORMATS': 'h5'
        }
