# -*- coding: utf-8 -*-
"""cluster related date types"""
from typing import List, Union
import tempfile

from ase import Atoms
from icet import ClusterSpace, ClusterExpansion

from aiida import orm


class ClusterSpaceData(orm.StructureData):
    """Data type of ClusterSpace"""
    def __init__(self, **kwargs):
        """
        init
        """
        super().__init__(**kwargs)

    def set(self,
            cutoffs: List[float],
            chemical_symbols: Union[List[str], List[List[str]]],
            ase: Atoms = None,
            symprec: float = 1e-5,
            position_tolerance: float = None):
        """set the parameters of the cluster space"""
        if ase:
            # set or reset ase
            self.set_ase(ase)

        self.set_attribute('cutoffs', cutoffs)
        self.set_attribute('chemical_symbols', chemical_symbols)
        self.set_attribute('symprec', symprec)
        self.set_attribute('position_tolerance', position_tolerance)

    @property
    def _cluster_space(self):
        """this give cluster space of icet type"""
        ase = self.get_ase()
        cutoffs = self.get_attribute('cutoffs')
        chemical_symbols = self.get_attribute('chemical_symbols')
        symprec = self.get_attribute('symprec')
        position_tolerance = self.get_attribute('position_tolerance')

        cs = ClusterSpace(ase, cutoffs, chemical_symbols, symprec,
                          position_tolerance)

        return cs

    def print_overview(self):
        """print the overview of cluster space"""
        self._cluster_space.print_overview()

    def get_noumenon(self):
        """return the icet type cluster space"""
        return self._cluster_space

    def set_from_cluster_space(self, cluster_space):
        """set from a icet type cluster space"""
        ase = cluster_space.primitive_structure
        cutoffs = cluster_space.cutoffs
        chemical_symbols = cluster_space.chemical_symbols
        symprec = cluster_space.symprec
        position_tolerance = cluster_space.position_tolerance

        self.set(ase=ase,
                 cutoffs=cutoffs,
                 chemical_symbols=chemical_symbols,
                 symprec=symprec,
                 position_tolerance=position_tolerance)


class ClusterExpansionData(orm.Data):
    """Data type of ClusterExpansion"""
    def set(self, cluster_space, parameters, metadata=None):
        """set cluster expansion after initial create it"""
        ce = ClusterExpansion(cluster_space, parameters, metadata)

        filename = 'stored.ce'
        self.set_attribute('filename', filename)

        tmp_file = tempfile.NamedTemporaryFile()
        ce.write(tmp_file.name)
        self.put_object_from_file(tmp_file.name, filename)

    @property
    def filename(self):
        """Return the name of the file stored.

        :return: the filename under which the file is stored in the repository
        """
        return self.get_attribute('filename')

    @property
    def _cluster_expansion(self):
        """get the cluster expansion from store file"""
        with self.open(self.filename, mode='rb') as handle:
            file_abs_path = handle.name  # pylint: disable=no-member

        return ClusterExpansion.read(file_abs_path)

    def print_overview(self):
        """print overview of cluster expansion"""
        return self._cluster_expansion.print_overview()

    def get_noumenon(self):
        """get icet type cluster expansion"""
        return self._cluster_expansion
