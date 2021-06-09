# -*- coding: utf-8 -*-
"""tests of ce data type"""
# pylint: disable=no-self-use, too-few-public-methods
import os

import pytest
import numpy as np
from aiida.plugins import DataFactory
from aiida import orm

from aiida_ce.workflows.create_ce import StructureDbData
from . import TEST_DIR

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name

ClusterSpaceData = DataFactory('cluster_space')
ClusterExpansionData = DataFactory('cluster_expansion')
StructureDbData = DataFactory('structure_db')


class TestClusterSpaceData:
    """test cases of `ClusterSpaceData`"""
    @pytest.mark.usefixtures('clear_database_before_test')
    def test_store(self, generate_ase_structure):
        """test store"""
        data = ClusterSpaceData()
        data.set(ase=generate_ase_structure(),
                 cutoffs=[7.0, 4.5],
                 chemical_symbols=[['Ag', 'Pd']])

        data_res = data.store()
        assert data_res is data
        assert data.print_overview() == data.get_noumenon().print_overview()
        assert data.is_stored

        # test stored data can be loaded
        data_loaded = orm.load_node(data_res.pk)
        assert data_loaded.print_overview() == data.print_overview()


class TestClusterExpansionData:
    """tests of `ClusterExpansionData`"""
    @pytest.mark.usefixtures('clear_database_before_test')
    def test_store(self, cluster_space):
        """test store"""
        parameters = np.array(len(cluster_space) * [1.0])
        data = ClusterExpansionData()
        data.set(cluster_space, parameters)

        data_res = data.store()
        assert data_res is data
        assert data.print_overview() == data.get_noumenon().print_overview()
        assert data.is_stored

        # test stored data can be loaded
        data_loaded = orm.load_node(data_res.pk)
        assert data_loaded.print_overview() == data.print_overview()

    @pytest.mark.usefixtures('clear_database_before_test')
    def test_set_and_load_metadata(self, cluster_space, optimizer):
        """set and load metadata"""
        data = ClusterExpansionData()
        data.set(cluster_space, optimizer.parameters, optimizer.summary)

        data_res = data.store()
        assert data.is_stored

        # test stored data can be loaded
        data_loaded = orm.load_node(data_res.pk)
        assert data_loaded.print_overview() == data.print_overview()


class TestStructureDbData:
    """test `StructureDbData`"""
    @pytest.mark.usefixtures('clear_database_before_test')
    def test_set_from_db_file(self):
        """test create from ase db file"""
        sdb = StructureDbData()
        db_file = os.path.join(TEST_DIR, 'reference_data.db')
        sdb.set_from_db_file(db_file)

        sdb_res = sdb.store()
        assert sdb_res is sdb
        assert sdb.is_stored

        sdb_loaded = orm.load_node(sdb_res.pk)
        assert sdb_loaded.status['structures']
        # assert sdb_loaded.status['properties'] == ['mix_energies']

    # def test_store_load_default(self, ase_db):
    #     """test store and then load from stored
    #     the db contains both structures and mix_eneries as properties."""
    #     structures_list = []
    #     mixing_energies = []
    #     for row in ase_db.select('natoms<=8'):
    #         structures_list.append(row.toatoms())
    #         mixing_energies.append(row.mixing_energy)

    #     sdb = StructureDbData()

    #     assert sdb.status['structures'] == False
    #     assert sdb.status['properties'] == []

    #     sdb.set_structures(structures_list)
    #     assert sdb.status['structures'] == True

    #     sdb.set_properties('mix_energies', mix_energies)
    #     assert sdb.status['properties'] == ['mix_energies']

    #     sdb_res = sdb.store()
    #     assert sdb_res is sdb
    #     assert sdb.is_stored

    #     sdb_loaded = orm.load_node(sdb_res.pk)
    #     assert sdb_loaded.status['structures'] == True
    #     assert sdb_loaded.status['properties'] == ['mix_energies']
