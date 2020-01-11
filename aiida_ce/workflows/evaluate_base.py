# -*- coding: utf-8 -*-
"""WorkChian to easily and controlablly evaluate the energy of the configurations(Using QE plugins)."""
from aiida import orm
from aiida.engine import WorkChain, ToContext, if_
from aiida.plugins import WorkflowFactory
from aiida.common import AttributeDict

from aiida_quantumespresso.utils.protocols.pw import ProtocolManager
from aiida_quantumespresso.utils.pseudopotential import get_pseudos_from_dict
from aiida_quantumespresso.utils.resources import get_default_options
from aiida_quantumespresso.utils.mapping import prepare_process_inputs

PwBaseWorkChain = WorkflowFactory('quantumespresso.pw.base')
PwRelaxWorkChain = WorkflowFactory('quantumespresso.pw.relax')

def validate_protocol(protocol_dict):
    """Check that the protocol is one for which we have a definition."""
    try:
        protocol_name = protocol_dict['name']
    except KeyError as exception:
        return 'Missing key `name` in protocol dictionary'
    try:
        ProtocolManager(protocol_name)
    except ValueError as exception:
        return str(exception)

class CeEvaluateBaseWorkChain(WorkChain):
    """WorkChian to easily and controlablly evaluate the energy of the configurations(Using QE plugins)."""

    @classmethod
    def define(cls, spec):
        """Define the process specification"""
        # yapf: disable
        super(CeEvaluateBaseWorkChain, cls).define(spec)
        spec.input('code', valid_type=orm.Code,
            help='The `pw.x` code to use for the `PwCalculations`.')
        spec.input('structure', valid_type=orm.StructureData,
            help='The input structure.')
        spec.input('options', valid_type=orm.Dict, required=False,
            help='Optional `options` to use for the `PwCalculations`.')
        spec.input('protocol', valid_type=orm.Dict,
            default=orm.Dict(dict={'name': 'theos-ht-1.0', 'modifiers': {'parameters': 'default', 'pseudo': 'SSSP-efficiency-1.1'}}),
            help='The protocol to use for the workchain.', validator=validate_protocol)
        spec.input('do_relax', valid_type=orm.Bool, default=orm.Bool(True),
            help='If `True`, running the relax and then scf')
        spec.input('clean_workdir', valid_type=orm.Bool, default=orm.Bool(True),
            help='If `True`, work directories of all called calculation will be cleaned at the end of execution.')
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
            help='The normalized and primitivized structure for which the scf step are computed.')
        spec.output('scf_parameters', valid_type=orm.Dict,
            help='The output parameters of the SCF `PwBaseWorkChain`.')

    def _get_protocol(self):
        protocol_data = self.inputs.protocol.get_dict()
        protocol_name = protocol_data['name']
        protocol = ProtocolManager(protocol_name)

        protocol_modifiers = protocol_data.get('modifiers', {})

        return protocol, protocol_modifiers

    def setup_protocol(self):
        """Set up context variables and inputs for the `CeEvaluateWorkChain`

        Based on the specified protocol, we define values for variables that affect the execution of the calculations.
        """
        protocol, protocol_modifiers = self._get_protocol()
        self.report('running the workchain with the "{}" protocol'.format(protocol.name))
        self.ctx.protocol = protocol.get_protocol_data(modifiers=protocol_modifiers)

    def setup_parameters(self):
        """Set up the default input parameters required for the `PwBandsWorkChain`."""
        ecutwfc = []
        ecutrho = []

        for kind in self.inputs.structure.get_kind_names():
            try:
                dual = self.ctx.protocol['pseudo_data'][kind]['dual']
                cutoff = self.ctx.protocol['pseudo_data'][kind]['cutoff']
                cutrho = dual * cutoff
                ecutwfc.append(cutoff)
                ecutrho.append(cutrho)
            except KeyError:
                self.report('failed to retrieve the cutoff or dual factor for {}'.format(kind))
                return self.exit_codes.ERROR_INVALID_INPUT_UNRECOGNIZED_KIND

        self.ctx.parameters = orm.Dict(dict={
            'CONTROL': {
                'restart_mode': 'from_scratch',
                'tstress': self.ctx.protocol['tstress'],
                'tprnfor': self.ctx.protocol['tprnfor'],
            },
            'SYSTEM': {
                'ecutwfc': max(ecutwfc),
                'ecutrho': max(ecutrho),
                'smearing': self.ctx.protocol['smearing'],
                'degauss': self.ctx.protocol['degauss'],
                'occupations': self.ctx.protocol['occupations'],
            },
            'ELECTRONS': {
                'conv_thr': self.ctx.protocol['convergence_threshold_per_atom'] * len(self.inputs.structure.sites),
            }
        })

    def should_do_relax(self):
        """If the 'relax' input namespace was specified, we relax the input structure."""
        return self.inputs.do_relax.value

    def _get_common_inputs(self):
        """Return the dictionary of inputs to be used as the basis for each `PwBaseWorkChain`."""
        protocol, protocol_modifiers = self._get_protocol()
        checked_pseudos = protocol.check_pseudos(
            modifier_name=protocol_modifiers.get('pseudo', None),
            pseudo_data=protocol_modifiers.get('pseudo_data', None))
        known_pseudos = checked_pseudos['found']

        inputs = AttributeDict({
            'pw': {
                'code': self.inputs.code,
                'pseudos': get_pseudos_from_dict(self.inputs.structure, known_pseudos),
                'parameters': self.ctx.parameters,
                'metadata': {},
            }
        })

        if 'options' in self.inputs:
            inputs.pw.metadata.options = self.inputs.options.get_dict()
        else:
            inputs.pw.metadata.options = get_default_options(with_mpi=True)

        return inputs

    def run_relax(self):
        """Run the PwRelaxWorkChain to run a relax PwCalculation."""
        inputs = AttributeDict({
            'structure': self.inputs.structure,
            'base': self._get_common_inputs(),
            'relaxation_scheme': orm.Str('vc-relax'),
            'meta_convergence': orm.Bool(self.ctx.protocol['meta_convergence']),
            'volume_convergence': orm.Float(self.ctx.protocol['volume_convergence']),
        })
        inputs.base.kpoints_distance = orm.Float(self.ctx.protocol['kpoints_mesh_density'])

        running = self.submit(PwRelaxWorkChain, **inputs)

        self.report('launching PwRelaxWorkChain<{}>'.format(running.pk))

        return ToContext(workchain_relax=running)

    def inspect_relax(self):
        """Verify that the PwRelaxWorkChain finished successfully."""
        workchain = self.ctx.workchain_relax

        if not workchain.is_finished_ok:
            self.report('PwRelaxWorkChain failed with exit status {}'.format(workchain.exit_status))
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_RELAX

        self.ctx.current_structure = workchain.outputs.output_structure

    def run_scf(self):
        """Run the PwBaseWorkChain in scf mode on the primitive cell of (optionally relaxed) input structure."""
        inputs = self._get_common_inputs()
        if not self.should_do_relax():
            self.ctx.current_structure = self.inputs.structure
        inputs.pw.structure = self.ctx.current_structure
        inputs.pw.parameters = inputs.pw.parameters.get_dict()
        inputs.pw.parameters.setdefault('CONTROL', {})
        inputs.pw.parameters['CONTROL']['calculation'] = 'scf'

        inputs.kpoints_distance = orm.Float(self.ctx.protocol['kpoints_mesh_density'])

        inputs = prepare_process_inputs(PwBaseWorkChain, inputs)
        running = self.submit(PwBaseWorkChain, **inputs)

        self.report('launching PwBaseWorkChain<{}> in {} mode'.format(running.pk, 'scf'))

        return ToContext(workchain_scf=running)

    def inspect_scf(self):
        """Verify that the PwBaseWorkChain for the scf run finished successfully."""
        workchain = self.ctx.workchain_scf

        if not workchain.is_finished_ok:
            self.report('scf PwBaseWorkChain failed with exit status {}'.format(workchain.exit_status))
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_SCF

        self.ctx.current_folder = workchain.outputs.remote_folder

    def results(self):
        """Attach the desired output nodes directly as outputs of the workchain."""
        self.report('workchain succesfully completed')
        self.out('scf_parameters', self.ctx.workchain_scf.outputs.output_parameters)
        self.out('primitive_structure', self.ctx.current_structure)

    def on_terminated(self):
        """Clean the working directories of all child calculations if `clean_workdir=True` in the inputs."""
        super(CeEvaluateBaseWorkChain, self).on_terminated()

        if self.inputs.clean_workdir.value is False:
            self.report('remote folders will not be cleaned')
            return

        cleaned_calcs = []

        for called_descendant in self.node.called_descendants:
            if isinstance(called_descendant, orm.CalcJobNode):
                try:
                    called_descendant.outputs.remote_folder._clean()  # pylint: disable=protected-access
                    cleaned_calcs.append(called_descendant.pk)
                except (IOError, OSError, KeyError):
                    pass

        if cleaned_calcs:
            self.report('cleaned remote folders of calculations: {}'.format(' '.join(map(str, cleaned_calcs))))
