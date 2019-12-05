import aiida.orm as orm
from aiida.engine import CalcJob
from aiida.plugins import DataFactory
from aiida.common import datastructures

class EnumCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the script of function
    enumerate_structures the wrapped file is geneum.py in
    ../wrappers/
    """
    StructureSet = DataFactory('ce.structures')

    @classmethod
    def define(cls, spec):
        # yapf: disable
        super(EnumCalculation, cls).define(spec)
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines':1, 'num_mpiprocs_per_machine':1}, non_db=True)
        spec.input('metadata.options.parser_name', valid_type=str, default='ce.genenum', non_db=True)
        spec.input('metadata.options.input_filename', valid_type=str, default='aiida.json', non_db=True)
        spec.input('metadata.options.output_filename', valid_type=str, default='aiida.out', non_db=True)
        spec.input('structure', valid_type=orm.StructureData, help='prototype structure to expand')
        spec.input('pbc', valid_type=orm.List, default=orm.List(list=[True, True, True]))
        spec.input('chemical_symbols', valid_type=orm.List, help='An N elements list of which that each element is the possible symbol of the site.')
        spec.input('min_volume', valid_type=orm.Int, default=orm.Int(1))
        spec.input('max_volume', valid_type=orm.Int, default=orm.Int(1), help='If None, no hnf cells to be considered.')
        spec.input('concentration_restrictions', required=False, valid_type=orm.Dict, help='dict indicate the concentration of each elements.')
        # spec.output('enumerate_structures', valid_type=StructureSet, help='enumerate structures store the outputs of the process')
        spec.output('arr_len', valid_type=orm.Int, required=True)

        spec.exit_code(100, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')

    def prepare_for_submission(self, folder):
        """
        """
        # Code
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = [self.options.input_filename]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename

        # Prepare a `CalaInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.retrieve_list = [self.metadata.options.output_filename, 'cells.raw']

        return calcinfo

    def write_input_files(folder):
        # prepare a param.json which contain the parameters needed to
        # run the code. param read from the inputs.
        param = dict()
        ase_structure = self.inputs.structure.get_ase()
        cell = ase_structure.cell.tolist()
        positions = ase_structure.positions.tolist()
        pbc = self.inputs.pbc.get_list()
        param['structure'] = {'cell': cell,
                              'positions': positions,
                              'pbc': pbc}

        chemical_symbols = self.inputs.chemical_symbols.get_list()
        minv = self.inputs.min_volume.value
        maxv = self.inputs.max_volume.value
        if maxv > minv:
            sizes = [i for i in range(minv, maxv)]
        else:
            sizes = [minv]
        concentration_restrictions = self.inputs.concentration_restrictions.value
        param['chemical_symbols'] = chemical_symbols
        param['sizes'] = sizes
        param['concentration_restrictions'] = concentration_restrictions
        if concentration_restrictions is None:
            param.pop('concentration_restrictions')

        param_str = json.dumps(param)
        with folder.open(self.options.input_filename, 'w', encoding='utf8') as handle:
            handle.write(param_str)
