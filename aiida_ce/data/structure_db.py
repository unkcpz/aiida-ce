# -*- coding: utf-8 -*-
"""
AiiDA class in plugin aiida-ce store the collection of
structures.
"""
import os

from aiida import orm


class StructureDbData(orm.ArrayData):
    """
    StructureSet stores a collection of structures and stores
    the energy labeling as an ase db file stored in repository.
    """
    def __init__(self, db_file=None, **kwargs):
        super().__init__(**kwargs)
        if db_file is not None:
            self.set_from_db_file(db_file)

    def get_db(self):
        """get the ase sqlsqlit db"""
        from ase.db import connect

        filename = self.get_attribute('filename')
        with self.open(filename, mode='rb') as handle:
            abs_path = handle.name  # pylint: disable=no-member

        return connect(abs_path, type='db')

    def set_from_db_file(self, file):
        """set StructureDbData from a db file"""
        key = os.path.basename(file)
        if not os.path.isabs(file):
            raise ValueError(f'path `{file}` is not absolute')

        if not os.path.isfile(file):
            raise ValueError(
                f'path `{file}` does not correspond to an existing file')

        self.put_object_from_file(file, key)
        self.set_attribute('filename', key)

    @property
    def status(self):
        """check whether the structures or the properties are set"""
        db = self.get_db()

        res = {'structures': False, 'properties': []}
        if db.count() != 0:
            res['structures'] = True

        return res
