# -*- coding: utf-8 -*-
"""ce create"""
from icet import StructureContainer, CrossValidationEstimator
from aiida import orm
from aiida.engine import WorkChain, run_get_node
from aiida.plugins import DataFactory

from . import _create_cluster_space

StructureDbData = DataFactory('structure_db')
ClusterExpansionData = DataFactory('cluster_expansion')
ClusterSpaceData = DataFactory('cluster_space')


class ConstructClusterExpansion(WorkChain):
    """WorkChain to construct cluster expansion using a db"""
    @classmethod
    def define(cls, spec):
        """Define the process spec"""
        # yapf: disable
        super().define(spec)
        spec.expose_inputs(_create_cluster_space, namespace='cluster_space')
        spec.input('structure_db', valid_type=StructureDbData,
                   help='reference data contain structures and their properties.')
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
        self.ctx.fit_data_key = self.inputs.fit_data_key.value
        self.ctx.fit_method = self.inputs.fit_method.value

    def create_cluster_space(self):
        """create cluster space with icet and store it as a cluster space data type"""
        self.ctx.cluster_space, _ = run_get_node(_create_cluster_space,
                              **self.exposed_inputs(_create_cluster_space, namespace='cluster_space'))

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
