# -*- coding: utf-8 -*-

"""
AiiDA class in plugin aiida-ce store the collection of
structures.
"""

from __future__ import absolute_import

from aiida.orm import ArrayData

class StructureSet(ArrayData):
    """
    StructureSet stores a collection of structures and stores
    the energy labeling which calculated by using DFT software.
    The purpose of StructureSet is 1. prevent the number of nodes
    from increasing too rapidly 2. Can be used as the output node
    of the CalcJob or CalcFunction in the plugin 3. Can be used as
    the training set input for CE process.
    The class is similar to the TrajectoryData in aiida_core and some
    of methods are same.
    """
    def __init__(self, structurelist=None, **kwargs):
        super(StructureSet, self).__init__(**kwargs)
        if structurelist is not None:
            self.set_structurelist(structurelist)

    def _internal_validate(self, nframes, cells, positions, atomic_numbers, ids, energies):
        """
        To validate the type and shape of the array.
        """
        pass

    def set_collection(self, elements, nframes, frame_size, cells, positions, atomic_numbers, ids=None, energies=None):
        r"""
        Store the collection, after checking that types and dimensions
        are correct.

        This is the main method to initialize the object, all the arrays
        are set in this method.

        Parameters ``ids`` and ``energies`` are optional variables. If
        no input is given for ``ids`` a consecutive sequence
        [0,1,2,...,len(nframes)-1] will be assumed.

        :param nframes: number of frames needed to represent a structure.
                        An 1D int array, length N, which store the number
                        of frames needed to represent a structure.
                        As for primitive the number is 1, as for x times
                        volume supercell the number of frames is x.

        :param cells:

        :param positions:

        :param atomic_numbers:

        :param ids:

        :param energies:

        :(hide) param cnframes: deduced from nframes,
                        integral of number of frames. Initialized in the method.
                        An 1D int array, length N. Combined with number_of_frames,
                        user can easily index the location and extract the info of
                        the structures stored in this type.

        """

        import numpy

        self._internal_validate(nframes, cells, positions, atomic_numbers, ids, energies)

        # set attribute for easier query

        # length is the number of structurs
        # size is a list of atom numbers of each structures
        self.set_attribute('length', len(nframes))
        size = nframes * frame_size
        self.set_attribute('size', size.tolist())

        self.set_attribute('elements', elements)

        # set arrays
        self.set_array('cells', cells)
        self.set_array('positions', positions)
        self.set_array('atomic_numbers', atomic_numbers)

        self.set_array('nframes', nframes)
        cnframes = numpy.cumsum(nframes) - nframes
        self.set_array('cnframes', cnframes)

        if energies is not None:
            self.set_array('energies', energies)

        if ids is not None:
            self.set_array('indices', ids)
        else:  # use consecutive sequence if not given
            self.set_array('indices', numpy.arange(len(nframes)))

    @property
    def size(self):
        return self.get_attribute('size')

    @property
    def length(self):
        return self.get_attribute('length')

    def set_structurelist(self, structurelist):
        """
        Create collection from the list of
        :py:class:`aiida.orm.nodes.data.structure.StructureData` instances.

        :param structurelist: a list of
            :py:class:`aiida.orm.nodes.data.structure.StructureData` instances.

        :raises ValueError: if symbol lists of supplied structures are
            invalid
        """
        import numpy
        from math import gcd
        from functools import reduce
        from ase.atoms import Atoms
        from aiida.orm import StructureData

        def to_ase(structure):
            if isinstance(structure, Atoms):
                return structure
            elif isinstance(structure, StructureData):
                return structure.get_ase()
            else:
                raise ValueError('structure must be ase.atoms.Atoms or StructureData')

        structurelist = [to_ase(x) for x in structurelist]

        arr_cells = numpy.array([x.cell for x in structurelist])

        # the size of a frame is the common greatest divisor of the number of atoms
        number_of_atoms = [s.get_number_of_atoms() for s in structurelist]
        frame_size = reduce(gcd, number_of_atoms)
        nframes = numpy.array([i/frame_size for i in number_of_atoms], dtype=int)
        cnframes = numpy.cumsum(nframes) - nframes
        total_frames = sum(nframes)

        arr_positions = numpy.zeros(shape=[total_frames, frame_size, 3])
        arr_atomic_numbers = numpy.zeros(shape=[total_frames, frame_size], dtype=int)

        ase_structurelist = [s for s in structurelist]
        elements = set()
        for i, x in enumerate(ase_structurelist):
            size_n = nframes[i]
            start = cnframes[i]
            elements.update(set(x.get_chemical_symbols()))

            for j in range(size_n):
                part_positions = x.arrays['positions'][j*frame_size:(j+1)*frame_size,:]
                arr_positions[start+j,:,:] = part_positions

                part_atomic_numbers = x.arrays['numbers'][j*frame_size:(j+1)*frame_size]
                arr_atomic_numbers[start+j,:] = part_atomic_numbers

        self.set_collection(elements=elements, nframes=nframes, frame_size=frame_size, cells=arr_cells, positions=arr_positions, atomic_numbers=arr_atomic_numbers)

    def set_energies(self, energies):
        """
        :param energies: energies is a arrayable type. list or array.
        The number of elements of energies should be equal to number of structures.
        """
        import numpy

        self.set_array('energies', numpy.array(energies))

    def get_structure(self, idx):
        """
        Return structure as StructureData by index
        """
        from aiida.orm import StructureData
        from ase.atoms import Atoms

        cell = self.get_cells()[idx]

        n = self.size[idx]
        nframes = self.get_nframes()
        cnframes = self.get_cnframes()

        start = cnframes[idx]
        end = cnframes[idx] + nframes[idx]
        arr_positions = self.get_positions()[start:end,:,:]
        arr_atomic_numbers = self.get_atomic_numbers()[start:end, :]
        positions = arr_positions.reshape([n,3])
        atomic_numbers = arr_atomic_numbers.reshape([n])

        ase_structure = Atoms(cell=cell, positions=positions, numbers=atomic_numbers, pbc=True)
        return StructureData(ase=ase_structure)

    def get_cells(self):
        """
        Return the array of cells, if it has already been set.
        """
        return self.get_array('cells')

    def get_positions(self):
        """
        Return the array of positions, if it has already been set.
        """
        return self.get_array('positions')

    def get_atomic_numbers(self):
        """
        Return the array of atomic numbers.
        """
        return self.get_array('atomic_numbers')

    def get_nframes(self):
        return self.get_array('nframes')

    def get_cnframes(self):
        return self.get_array('cnframes')

    def get_energies(self):
        """
        Return the energies labeled for the structures.
        """
        try:
            return self.get_array('energies')
        except (AttributeError, KeyError):
            return None
