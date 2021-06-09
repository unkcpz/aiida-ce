# -*- coding: utf-8 -*-
"""test calculations"""
# pylint: disable=redefined-outer-name
import pytest

from aiida import orm
from aiida.common import CalcInfo

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture(scope='function')
def fixture_sandbox():
    """Return a `SandboxFolder`."""
    from aiida.common.folders import SandboxFolder
    with SandboxFolder() as folder:
        yield folder


@pytest.fixture
def generate_calc_job():
    """Fixture to construct a new `CalcJob` instance and call `prepare_for_submission` for testing `CalcJob` classes.
    The fixture will return the `CalcInfo` returned by `prepare_for_submission` and the temporary folder that was passed
    to it, into which the raw input files will have been written.
    """
    def _generate_calc_job(folder, entry_point_name, inputs=None):
        """Fixture to generate a mock `CalcInfo` for testing calculation jobs."""
        from aiida.engine.utils import instantiate_process
        from aiida.manage.manager import get_manager
        from aiida.plugins import CalculationFactory

        manager = get_manager()
        runner = manager.get_runner()

        process_class = CalculationFactory(entry_point_name)
        process = instantiate_process(runner, process_class, **inputs)

        calc_info = process.prepare_for_submission(folder)

        return calc_info

    return _generate_calc_job


# @pytest.fixture
# def generate_singlefile():
#     """gererate a SinglefileData from file"""
#     def _generate_singlefile(file_path):
#         """create SinglefileData from file and return"""
#         return orm.SinglefileData(file_path)

#     return _generate_singlefile


@pytest.fixture
def fixture_code(fixture_localhost):
    """Return a `Code` instance configured to run calculations of given entry point on localhost `Computer`."""
    def _fixture_code(code_name, entry_point_name=None):
        from aiida.common import exceptions
        from aiida.orm import Code

        if not entry_point_name:
            entry_point_name = code_name

        label = f'test.{code_name}'

        try:
            return Code.objects.get(label=label)  # pylint: disable=no-member
        except exceptions.NotExistent:
            return Code(
                label=label,
                input_plugin_name=entry_point_name,
                remote_computer_exec=[fixture_localhost, '/bin/true'],
            )

    return _fixture_code


@pytest.fixture
def generate_inputs(fixture_code):
    """Generate inputs for calculation"""
    def _generate_inputs(entry_point_name):

        # input primitive structure
        primitive_structure = orm.StructureData(
            cell=[[1., 0, 0], [
                0.5,
                0.866,
                0,
            ], [0., 0., 1.63333]])
        primitive_structure.append_atom(position=[0., 0., 0.],
                                        symbols=['Ni', 'Fe'],
                                        weights=[0.5, 0.5],
                                        name='NiFe1')
        primitive_structure.append_atom(position=[0., 0.57735, 0.81666],
                                        symbols=['Ni', 'Fe'],
                                        weights=[0.5, 0.5],
                                        name='NiFe2')

        supercell = orm.StructureData(
            cell=[[2., 0., 0.], [1., 1.7321, 0.], [0., 0., 3.26666]])

        if entry_point_name == 'atat.mcsqs':
            inputs = {
                'code':
                fixture_code('atat.mcsqs'),
                'code_corrdump':
                fixture_code('atat.corrdump', entry_point_name='atat.mcsqs'),
                'primitive_structure':
                primitive_structure,
                'sqscell':
                supercell,
            }

        return inputs

    return _generate_inputs


def test_atat_mcsqs_default(fixture_sandbox, generate_calc_job,
                            generate_inputs, file_regression):
    """Test mcsqs"""
    entry_point_name = 'atat.mcsqs'
    inputs = generate_inputs(entry_point_name)

    calc_info = generate_calc_job(fixture_sandbox, entry_point_name, inputs)

    assert isinstance(calc_info, CalcInfo)
    assert len(calc_info.codes_info) == 2

    with fixture_sandbox.open('rndstr.in') as handle:
        rndstr_written = handle.read()
    file_regression.check(rndstr_written,
                          encoding='utf-8',
                          extension='.in',
                          basename='rndstr')

    with fixture_sandbox.open('sqscell.out') as handle:
        sqscell_written = handle.read()
    file_regression.check(sqscell_written,
                          encoding='utf-8',
                          extension='.in',
                          basename='sqscell')
