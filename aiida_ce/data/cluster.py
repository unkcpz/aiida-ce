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

    def get_cell(self):
        return self.get_attribute('cell')

    def get_positions(self):
        return self.get_attribute('positions')

    def get_pbc(self):
        return self.get_attribute('pbc')

    def get_chemical_symbols(self):
        return self.get_attribute('chemical_symbols')

    def get_cutoffs(self):
        return self.get_attribute('cutoffs')

    def dumps(self):
        import json

        params = dict()
        params['structure'] = {
            'cell': self.get_cell(),
            'positions': self.get_positions(),
            'pbc': self.get_pbc(),
        }
        params['cutoffs'] = self.get_cutoffs()
        params['chemical_symbols'] = self.get_chemical_symbols()

        return json.dumps(params, indent=4, sort_keys=True)
