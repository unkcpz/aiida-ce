"""pytest fixtures for simplified testing."""
from __future__ import absolute_import
import pytest
pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture(scope='function', autouse=True)
def clear_database_auto(clear_database):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""


@pytest.fixture(scope='function')
def ce_train_code(aiida_local_code_factory):
    """Get a ce train code.
    """
    import os

    path = os.getcwd()
    code_path = os.path.join(path, 'wrappers/train.py')
    code = aiida_local_code_factory(executable=code_path, entry_point='ce.train')
    return code

@pytest.fixture(scope='function')
def ce_enum_code(aiida_local_code_factory):
    """Get a ce enum code.
    """
    import os

    path = os.getcwd()
    code_path = os.path.join(path, 'wrappers/genenum.py')
    code = aiida_local_code_factory(executable=code_path, entry_point='ce.genenum')
    return code

@pytest.fixture(scope='function')
def ce_sqs_code(aiida_local_code_factory):
    """Get a ce sqs code.
    """
    import os

    path = os.getcwd()
    code_path = os.path.join(path, 'wrappers/gensqs.py')
    code = aiida_local_code_factory(executable=code_path, entry_point='ce.gensqs')
    return code
