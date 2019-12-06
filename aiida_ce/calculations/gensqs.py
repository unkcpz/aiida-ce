from aiida.engine import CalcJob
from aiida.common import datastructures

from aiida.orm import StructureData, Int, List, Dict, Bool

class SqsCalculation(CalcJob):
    """
    Calculation Job of gensqs.py which is a wrapper of
    function generate_sqs in icet package. Script gensqs.py
    in ../wrappers/
    """

    @classmethod
    def define(cls, spec):
        #yapf: disable
        super(SqsCalculation, cls).define(spec)
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines':1, 'num_mpiprocs_per_machine':1}, non_db=True)
        spec.input('metadata.options.parser_name', valid_type=str, default='ce.gensqs', non_db=True)
        spec.input('metadata.options.input_filename', valid_type=str, default='aiida.json', non_db=True)
        spec.input('metadata.options.output_filename', valid_type=str, default='aiida.out', non_db=True)
        spec.input('structure', valid_type=StructureData, help='prototype structure to expand')
        spec.input('pbc', valid_type=List, default=List(list=[True, True, True]))
        spec.input('chemical_symbols', valid_type=List, help='An N elements list of which that each element is the possible symbol of the site.')
        spec.input('target_concentrations', valid_type=Dict, help='target concentration of elements of the sqs')
        spec.input('include_smaller_cells', valid_type=Bool, default=Bool(False), help='if false, only cell with >32 atoms will calculated')
        spec.input('cutoffs', valid_type=List, help='cutoffs of each NN distance')
        spec.input('max_size', valid_type=Int, default=Int(16), help='structures having up to max size times in the supercell')
        spec.input('n_steps', valid_type=Int, default=Int(10000), help='max annealing steps to run')

        spec.output('sqs', valid_type=StructureData, help='sqs structure')
        spec.output('cluster_vector', valid_type=List, help='cluster vector of sqs')
        # TODO:
        # spec.output('cluster_space', valid_type=ClusterSpaceData, help='cluster space used to generate sqs')

        spec.exit_code(100, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')

    def prepare_for_submission(self, folder):
        """
        """
        self.write_input_files(folder)

        # Code
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = [self.options.input_filename]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename

        # Prepare a `CalaInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        retrieve_list = ['sqs.out']
        calcinfo.retrieve_list = retrieve_list + [self.metadata.options.output_filename]

        return calcinfo

    def write_input_files(self, folder):
        import json

        # prepare a json file contain the parameters to
        # run the code.
        param = dict()
        ase_structure = self.inputs.structure.get_ase()
        cell = ase_structure.cell.tolist()
        positions = ase_structure.positions.tolist()
        pbc = self.inputs.pbc.get_list()
        param['structure'] = {'cell': cell,
                              'positions': positions,
                              'pbc': pbc}

        param['chemical_symbols'] = self.inputs.chemical_symbols.get_list()
        param['target_concentrations'] = self.inputs.target_concentrations.get_dict()
        param['cutoffs'] = self.inputs.cutoffs.get_list()
        param['max_size'] = self.inputs.max_size.value
        param['n_steps'] = self.inputs.n_steps.value
        param['include_smaller_cells'] = self.inputs.include_smaller_cells.value

        param_str = json.dumps(param, indent=4, sort_keys=True)
        with folder.open(self.options.input_filename, 'w', encoding='utf8') as handle:
            handle.write(param_str)
