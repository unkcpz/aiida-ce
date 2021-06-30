# -*- coding: utf-8 -*-
"""pytest fixtures for simplified testing."""
# pylint: disable=redefined-outer-name
import os
import pytest

from aiida import orm
from icet import StructureContainer, CrossValidationEstimator

from aiida_ce.workflows.create_ce import StructureDbData

from . import TEST_DIR

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture
def generate_ase_structure():
    """Reture a ase structure"""
    def _generate_ase_structure(structure_id='Ag'):
        """Reture a ase structure Ag or """
        from ase.build import bulk

        if structure_id == 'Ag':
            ase_structure = bulk('Ag')

        if structure_id == 'Au':
            ase_structure = bulk('Au')

        if structure_id == 'Au1x2x4':
            ase_structure = bulk('Au').repeat((1, 2, 4))

        return ase_structure

    return _generate_ase_structure


@pytest.fixture
def primitive_structure(generate_ase_structure):
    """return a StructureData of primitive Ag"""
    yield orm.StructureData(ase=generate_ase_structure('Ag'))


@pytest.fixture
def supercell(generate_ase_structure):
    """Return a supercell StrucutrueData of Au"""
    yield orm.StructureData(ase=generate_ase_structure('Au1x2x4'))


@pytest.fixture
def cluster_space_aupd(generate_ase_structure):
    """Ruturn a cluster space"""
    from icet import ClusterSpace

    prim = generate_ase_structure('Au')
    cs = ClusterSpace(prim,
                      cutoffs=[8.0, 4.0],
                      chemical_symbols=[['Au', 'Pd']])

    yield cs


@pytest.fixture
def cluster_space(generate_ase_structure):
    """Ruturn a cluster space"""
    from icet import ClusterSpace

    prim = generate_ase_structure('Ag')
    cs = ClusterSpace(prim,
                      cutoffs=[7.0, 5.0],
                      chemical_symbols=[['Ag', 'Pd']])

    yield cs


@pytest.fixture
def ase_db():
    """return the aupd ase database"""
    from ase.db import connect

    reference_data_db = os.path.join(TEST_DIR, 'reference_data.db')
    db = connect(reference_data_db)

    yield db


@pytest.fixture
def structure_container(cluster_space, ase_db):
    """Ag Pd structure container"""
    sc = StructureContainer(cluster_space=cluster_space)
    for row in ase_db.select('natoms<=8'):
        sc.add_structure(structure=row.toatoms(),
                         user_tag=row.tag,
                         properties={'mixing_energy': row.mixing_energy})

    yield sc


@pytest.fixture
def optimizer(structure_container):
    """return a optimizer"""
    opt = CrossValidationEstimator(
        fit_data=structure_container.get_fit_data(key='mixing_energy'),
        fit_method='lasso')
    opt.validate()
    opt.train()

    yield opt


@pytest.fixture
def structure_db():
    """Return the aupd structure db data"""
    reference_data_db = os.path.join(TEST_DIR, 'reference_data.db')
    sdb = StructureDbData(reference_data_db)

    yield sdb


@pytest.fixture
def fixture_localhost(aiida_localhost):
    """Return a localhost `Computer`."""
    localhost = aiida_localhost
    localhost.set_default_mpiprocs_per_machine(1)
    return localhost
