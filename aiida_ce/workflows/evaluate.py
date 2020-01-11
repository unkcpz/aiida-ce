# -*- coding: utf-8 -*-
"""WorkChian to easily and controlablly evaluate the energy of the configurations(Using QE plugins)."""
from aiida import orm

from aiida_quantumespresso.utils.protocols.pw import ProtocalManager

class CeEvaluateWorkChain(WorkChain):
	"""WorkChian to easily and controlablly evaluate the energy of the configurations(Using QE plugins)."""
	
	@classmethod
	def define(cls, spec):
		"""Define the process specification"""
		# yapf: disable
		super(CeEvaluateWorkChain, cls).define(spec)
        spec.expose_inputs(PwRelaxWorkChain, namespace='relax', exclude=('clean_workdir', 'structure'),
            namespace_options={'required': False, 'populate_defaults': False,
            'help': 'Inputs for the `PwRelaxWorkChain`, if not specified at all, the relaxation step is skipped.'})
        spec.expose_inputs(PwBaseWorkChain, namespace='scf', exclude=('clean_workdir', 'pw.structure'),
            namespace_options={'help': 'Inputs for the `PwBaseWorkChain` for the SCF calculation.'})
		spec.input('code', valid_type=orm.Code,
			help='The `pw.x` code to use for the `PwCalculations`.')
		spec.input('structure', valid_type=orm.StructureData,
			help='The input structure.')
        spec.input('options', valid_type=orm.Dict, required=False,
            help='Optional `options` to use for the `PwCalculations`.')
        spec.input('protocol', valid_type=orm.Dict, default=orm.Dict(dict={'name': 'theos-ht-1.0'}),
            help='The protocol to use for the workchain.', validator=validate_protocol)
		spec.outline(
			cls.setup_protocol,
			cls.setup_parameters,
            if_(cls.should_do_relax)(
                cls.run_relax,
                cls.inspect_relax,
            ),
			cls.run_scf,
			cls.inspect_scf,
			cls.results,		
		)
        spec.exit_code(201, 'ERROR_INVALID_INPUT_UNRECOGNIZED_KIND',
            message='Input `StructureData` contains an unsupported kind.')
        spec.exit_code(401, 'ERROR_SUB_PROCESS_FAILED_RELAX',
            message='the PwRelaxWorkChain sub process failed')
        spec.exit_code(402, 'ERROR_SUB_PROCESS_FAILED_SCF',
            message='the scf PwBasexWorkChain sub process failed')
        spec.output('primitive_structure', valid_type=orm.StructureData,
            help='The normalized and primitivized structure for which the bands are computed.')
        spec.output('scf_parameters', valid_type=orm.Dict,
            help='The output parameters of the SCF `PwBaseWorkChain`.')

	def setup_protocol(self):
		pass

	def setup_parameters(self):
		pass

	def should_do_relax(self):
		pass

	def run_relax(self):
		pass

	def inspect_relax(self):
		pass

	def run_scf(self):
		pass

	def inspect_scf(self):
		pass

	def results(self):
		pass
