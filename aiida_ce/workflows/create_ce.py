# -*- coding: utf-8 -*-
"""ce create"""
from icet import StructureContainer, CrossValidationEstimator
from aiida import orm
from aiida.engine import WorkChain
from aiida.plugins import DataFactory

StructureDbData = DataFactory('structure_db')
ClusterExpansionData = DataFactory('cluster_expansion')
ClusterSpaceData = DataFactory('cluster_space')


class ConstructClusterExpansion(WorkChain):
    """WorkChain to construct cluster expansion using a db(TODO to a specific datatype)"""
    @classmethod
    def define(cls, spec):
        """Define the process spec"""
        # yapf: disable
        super().define(spec)
        spec.input('primitive_structure', valid_type=orm.StructureData,
                   help='The primitive structure used to create cluster space')
        spec.input('structure_db', valid_type=StructureDbData,
                   help='reference data contain structures and their properties.')
        spec.input('cutoffs', valid_type=orm.List,
                   help='cutoff radii per order that define the cluster space.')
        spec.input('chemical_symbols', valid_type=orm.List,
                   help='list of chemical symbols.')
        spec.input('fit_data_key', valid_type=orm.Str, default=lambda: orm.Str('mixing_energy'),
                   help='The key of target properties for all structures.')
        spec.input('fit_method', valid_type=orm.Str, default=lambda: orm.Str('lasso'),
                   help='method to be used for training.')
        spec.input('options', valid_type=orm.Dict, required=False,
                   help='Optional `options` to use.')
        spec.outline(
            cls.setup,
            cls.create_cluster_space,
            cls.train,
            # cls.result,
        )
        spec.output('cluster_expansion', valid_type=ClusterExpansionData,
            help='The output cluster expansion.')

    def setup(self):
        """setup the ctx parameters"""
        self.ctx.cutoffs = self.inputs.cutoffs.get_list()
        self.ctx.chemical_symbols = self.inputs.chemical_symbols.get_list()
        self.ctx.fit_data_key = self.inputs.fit_data_key.value
        self.ctx.fit_method = self.inputs.fit_method.value

    def create_cluster_space(self):
        """create cluster space with icet and store it as a cluster space data type"""
        primitive_structure = self.inputs.primitive_structure.get_ase()  # primitive structure

        cs_data = ClusterSpaceData()
        cs_data.set(ase=primitive_structure,
                    cutoffs=self.ctx.cutoffs,
                    chemical_symbols=self.ctx.chemical_symbols)

        self.ctx.cluster_space = cs_data

    def train(self):
        """train and store cluster expansion data type"""
        cs = self.ctx.cluster_space.get_noumenon()

        db = self.inputs.structure_db.get_db()
        structures = db.select('natoms<=8')
        sc = StructureContainer(cluster_space=cs)
        for row in structures:
            sc.add_structure(structure=row.toatoms(),
                            user_tag=row.tag,
                            properties={self.ctx.fit_data_key: row.mixing_energy})

        opt = CrossValidationEstimator(fit_data=sc.get_fit_data(key=self.ctx.fit_data_key),
                                fit_method=self.ctx.fit_method)
        opt.validate()
        opt.train()

        ce_data = ClusterExpansionData()
        ce_data.set(cluster_space=cs,
                    parameters=opt.parameters,
                    metadata=opt.summary)

        self.out('cluster_expansion', ce_data.store())
