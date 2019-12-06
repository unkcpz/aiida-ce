from aiida.manage.tests.unittest_classes import PluginTestCase

from aiida.plugins import DataFactory

from ase.build import bulk

ClusterSpaceData = DataFactory('ce.cluster')

def test_():
    pass

class TestClusterSpaceData(PluginTestCase):

    def setUp(self):
        prim = bulk('Au')
        cs_dict = {
            'cell': prim.cell,
            'positions': prim.positions,
            'pbc':prim.pbc,
            'cutoffs': [6.0, 4.0],
            'chemical_symbols': [['Au', 'Pd']]
        }
        self.cs = ClusterSpaceData(cs_dict)

    def test_properties(self):
        pass
