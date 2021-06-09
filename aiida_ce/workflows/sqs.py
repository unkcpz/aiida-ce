# -*- coding: utf-8 -*-
"""workflow to get a sqs"""
from __future__ import absolute_import
from aiida import orm

from aiida.engine import WorkChain
from aiida.plugins import DataFactory

from icet.tools.structure_generation import generate_sqs_from_supercells

from aiida_ce.workflows.create_ce import ClusterSpaceData

ClusterSpaceData = DataFactory('cluster_space')


class SqsWorkChain(WorkChain):
    """A workchain to generate sqs"""
    @classmethod
    def define(cls, spec):
        """Define the process spec"""
        super().define(spec)
        spec.input(
            'cluster_space',
            valid_type=ClusterSpaceData,
            help='The cluster space defining the lattice to be occupied.')
        spec.input(
            'supercell',
            valid_type=orm.StructureData,
            help='The supercell which optimal structure will be search.')
        spec.input(
            'target_concentrations',
            valid_type=orm.Dict,
            help=
            'concentration of each species in the target structure, per sublattice'
        )
        spec.input(
            'temperature_start',
            valid_type=orm.Float,
            default=lambda: orm.Float(5.),
            help=
            'artificial temperature at which the simulated annealing starts')
        spec.input(
            'temperature_stop',
            valid_type=orm.Float,
            default=lambda: orm.Float(0.001),
            help=
            'artificial temperature at which the simulated annealing starts')
        spec.input('n_steps',
                   valid_type=orm.Int,
                   default=lambda: orm.Int(10000),
                   help='total number of Monte Carlo steps in the simulation')
        spec.input('optimality_weight',
                   valid_type=orm.Float,
                   default=lambda: orm.Float(1.),
                   help='controls weighting :math:`L` of perfect correlations')
        spec.input(
            'random_seed',
            valid_type=orm.Int,
            default=lambda: orm.Int(1234),
            help=
            'seed for the random number generator used in the Monte Carlo simulation'
        )
        spec.input('tolerant',
                   valid_type=orm.Float,
                   default=lambda: orm.Float(1e-5),
                   help='Numerical tolerance')
        spec.outline(
            cls.setup,
            cls.run_sqs,
        )
        spec.output('output_structure',
                    valid_type=orm.StructureData,
                    help='The output special quasirandom structure (SQS).')
        spec.output('output_cluster_vector',
                    valid_type=orm.List,
                    help='The output cluster vector of the output SQS.')

    def setup(self):
        """setup the parameters for actual run"""
        self.ctx.n_steps = self.inputs.n_steps.value
        self.ctx.T_start = self.inputs.temperature_start.value
        self.ctx.T_stop = self.inputs.temperature_stop.value
        self.ctx.optimality_weight = self.inputs.optimality_weight.value
        self.ctx.tol = self.inputs.tolerant.value
        self.ctx.random_seed = self.inputs.random_seed.value
        self.ctx.target_concentrations = self.inputs.target_concentrations.get_dict(
        )

    def run_sqs(self):
        """running and get sqs using icet"""
        cs = self.inputs.cluster_space.get_noumenon()
        the_supercell = self.inputs.supercell.get_ase()

        sqs = generate_sqs_from_supercells(
            cluster_space=cs,
            supercells=[the_supercell],
            n_steps=self.ctx.n_steps,
            T_start=self.ctx.T_start,
            T_stop=self.ctx.T_stop,
            optimality_weight=self.ctx.optimality_weight,
            random_seed=self.ctx.random_seed,
            target_concentrations=self.ctx.target_concentrations,
            tol=self.ctx.tol)

        cluster_vecter = cs.get_cluster_vector(sqs).tolist()
        self.out('output_cluster_vector',
                 orm.List(list=cluster_vecter).store())

        output_structure = orm.StructureData(ase=sqs)
        self.out('output_structure', output_structure.store())
