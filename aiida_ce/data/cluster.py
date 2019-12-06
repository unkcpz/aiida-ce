# -*- coding: utf-8 -*-

from icet import ClusterSpace

from aiida.orm import Data

class ClusterSpaceData(Data):

    def __init__(self, cs=None, **kwargs):
        """
        :param cs: a defined simplified version of ClusterSpace
        """
        super(ClusterSpaceData, self).__init__(**kwargs)
        if cs is not None:
            self.set_cluster_space(cs)

    def set_cluster_space(self, cs):
        import numpy

        self.set_attribute('cell', cs.get('cell', None))
        self.set_attribute('positions', cs.get('positions', None))
        self.set_attribute('pbc', cs.get('pbc', [True, True, True]))
        self.set_attribute('cutoffs', cs.get('cutoffs', None))
        self.set_attribute('chemical_symbols', cs.get('chemical_symbols', None))

    def _internal_validate(self):
        pass
