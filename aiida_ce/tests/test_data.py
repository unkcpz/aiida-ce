"""
Test for data of plugin
"""

from __future__ import absolute_import

from aiida.manage.tests.unittest_classes import PluginTestCase

from aiida.orm import StructureData
from aiida.plugins import DataFactory

from icet.tools import enumerate_structures

import numpy

StructureSet = DataFactory('ce.structures')

def create_pdau_bcc_structurelist():
    from ase.build import bulk

    # Create the samples for test (totally 10, but only use even index structures):
    # Atoms(symbols='Pd', pbc=True, cell=[[0.0, 2.04, 2.04], [2.04, 0.0, 2.04], [2.04, 2.04, 0.0]]),
    # Atoms(symbols='PdAu', pbc=True, cell=[[0.0, -2.04, -2.04], [-2.04, 0.0, -2.04], [2.04, 2.04, -4.08]]),
    # Atoms(symbols='Pd2Au', pbc=True, cell=[[0.0, 2.04, 2.04], [-2.04, 0.0, -2.04], [-4.08, -4.08, 4.08]]),
    # Atoms(symbols='Pd2Au', pbc=True, cell=[[0.0, -2.04, -2.04], [-4.08, 0.0, 0.0], [2.04, 4.08, -2.04]]),
    # Atoms(symbols='Pd2Au', pbc=True, cell=[[0.0, 2.04, 2.04], [0.0, 2.04, -2.04], [-6.12, -2.04, 0.0]])

    primitive_structure = bulk('Au')
    ase_structurelist = []
    for structure in enumerate_structures(primitive_structure,
                                        range(1, 4),
                                        ['Pd', 'Au']):
        # generator of structure, convert it to StructureData
        # and store it in the aiida db
        ase_structurelist.append(structure)

    return ase_structurelist

def create_spinel_structurelist():
    from aiida.tools.dbimporters.plugins.cod import CodDbImporter
    from icet.tools import get_primitive_structure

    # Import the ordered MgAl2O4 from COD db
    importer = CodDbImporter()
    mgalo = importer.query(id=1010129)[0]

    ase_mgalo = mgalo.get_ase_structure()
    primitive_structure = get_primitive_structure(ase_mgalo)

    chemical_symbols = [['Mg', 'Al'] for i in range(6)] + [['O'] for i in range(8)]

    # The concentration of A is 2/14 \in (0.1428, 0.1429)
    concentration_restrictions = {'Mg':(0.1428, 0.1429)}

    ase_structurelist = []
    for structure in enumerate_structures(primitive_structure,
                                            range(1, 3),
                                             chemical_symbols,
                                             concentration_restrictions=concentration_restrictions):
        ase_structurelist.append(structure)

    return ase_structurelist

class TestStructureSet(PluginTestCase):
    """
    Test data type StructureSet.
    """

    def setUp(self):
        ase_structurelist = create_pdau_bcc_structurelist()

        self.ase_structurelist = ase_structurelist
        aiida_structurelist = [StructureData(ase=structure).store()
                                for structure in ase_structurelist]

        aiida_structurelist = [s for i,s in enumerate(aiida_structurelist) if i%2 ==0]

        self.structure_set_bcc = StructureSet(structurelist=aiida_structurelist)

    # def test_spinel_structue_set(self):
    #     spinel_list = create_spinel_structurelist()
    #     structureset_spinel = StructureSet(structurelist=spinel_list)
    #
    #     got_length = structureset_spinel.length
    #     got_size = structureset_spinel.size
    #
    #     expected_length = 78
    #     expected_size = [14]*3 + [28]*75
    #
    #     self.assertEqual(got_length, expected_length)
    #     self.assertEqual(got_size, expected_size)

    def test_init_from_ase_structurelist(self):
        structure_set_got = StructureSet(structurelist=self.ase_structurelist)

    def test_normal_operation(self):
        clone_set = self.structure_set_bcc.clone()
        clone_set.store()
        self.assertIsNotNone(clone_set.pk)
        self.assertIsNone(self.structure_set_bcc.pk)

    def test_shape(self):
        cells = self.structure_set_bcc.get_cells()
        self.assertEqual(cells.shape, (5, 3, 3))

        positions = self.structure_set_bcc.get_positions()
        self.assertEqual(positions.shape, (12, 1, 3))

        atomic_numbers = self.structure_set_bcc.get_atomic_numbers()
        self.assertEqual(atomic_numbers.shape, (12, 1))

    def test_set_energies(self):
        energies = self.structure_set_bcc.get_energies()
        self.assertIsNone(energies)

        in_energies = [0.0, 0.1, 0.5, 0.001, 0]
        clone_set = self.structure_set_bcc.clone()
        clone_set.set_energies(in_energies)
        energies = clone_set.get_energies()
        numpy.testing.assert_almost_equal(energies, numpy.array(in_energies))

        energies = self.structure_set_bcc.get_energies()
        self.assertIsNone(energies)


    def test_attribute(self):
        # test return of fundamental data:
        # number of structures, number of atoms of each structure
        # elements contained.
        ss = self.structure_set_bcc.clone()
        self.assertEqual(ss.get_attribute('length'), 5)
        self.assertEqual(ss.get_attribute('size'), [1, 2, 3, 3, 3])

        self.assertEqual(ss.get_attribute('elements'), set(['Au', 'Pd']))

    def test_get_structure(self):
        # return StructureData by index
        bcc_ss = self.structure_set_bcc.clone()
        structure = bcc_ss.get_structure(idx=3)

        ase_structure = structure.get_ase()
        self.assertEqual(ase_structure.get_chemical_formula(), 'AuPd2')

        cell_expected = numpy.array([[0.0, -2.04, -2.04], [-4.08, 0.0, 0.0], [2.04, 4.08, -2.04]])
        numpy.testing.assert_almost_equal(ase_structure.cell, cell_expected)

        positions_expected = numpy.array([[0.0, 0.0, 0.0],
                                        [-2.04, 0.0, -2.04],
                                        [0.0, 2.04, -2.04]])
        numpy.testing.assert_almost_equal(ase_structure.positions, positions_expected)
        self.assertEqual(ase_structure.get_atomic_numbers().tolist(), [46,46,79])


    def test_query(self):
        # make sure the specific data can be queried from DB
        pass

    def test_set_ase_db(self):
        pass

    def test_internal_validate(self):
        pass
