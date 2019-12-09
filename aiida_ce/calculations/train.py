from aiida.engine import CalcJob
from aiida.common import datastructures
from aiida.plugins import DataFactory
from aiida.orm import Str, SinglefileData

StructureSet = DataFactory('ce.structures')
ClusterSpaceData = DataFactory('ce.cluster')

class TrainCalculation(CalcJob):
    """
    Calculation Job of train.py which is a wrapper of
    function cluster expansion evaluate in icet package.
    Script train.py in ../wrappers/
    """

    @classmethod
    def define(cls, spec):
        #yapf: disable
        super(TrainCalculation, cls).define(spec)
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines':1, 'num_mpiprocs_per_machine':1}, non_db=True)
        spec.input('metadata.options.parser_name', valid_type=str, default='ce.train', non_db=True)
        spec.input('metadata.options.input_filename', valid_type=str, default='aiida.json', non_db=True)
        spec.input('metadata.options.output_filename', valid_type=str, default='aiida.out', non_db=True)
        # TODO: Not just check the type but also check the energies are labelled
        spec.input('structures', valid_type=StructureSet, help='training set')
        spec.input('cluster_space', valid_type=ClusterSpaceData, help='cluster space used')
        spec.input('fit_method', valid_type=Str, default=Str('lasso'), help='fitting method used to train the model')

        # TODO: use a specific data type to store the model
        spec.output('model', valid_type=SinglefileData, help='parameters of model')

        spec.exit_code(100, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        self.write_input_files(folder)

        # Code
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = [self.options.input_filename, db_file]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename

        # Prepare a `CalaInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        retrieve_list = ['model.ce']
        calcinfo.retrieve_list = retrieve_list + [self.metadata.options.output_filename]

        return calcinfo

    def write_input_files(self, folder):
        import json

        cs = self.inputs.cluster_space
        param_str = cs.dumps()
        with folder.open(self.options.input_filename, 'w', encoding='utf8') as handle:
            handle.write(param_str)

        structureset = self.options.structures
        cells = structureset.get_cells()
        positions = structuresset.get_positionsn()
        atomic_numbers = structureset.get_atomic_numbers()
        natoms = structuresset.size()

        with open('cells.raw', 'w') as f:
            numpy.savetxt(cells, f)
        with open('coordinates.raw', 'w') as f:
            numpy.savetxt(positions, f)
        with open('atomic_numbers.raw', 'w') as f:
            numpy.savetxt(atomic_numbers, f, fmt='%d')
        with open('natoms.raw', 'w') as f:
            numpy.savetxt(natoms, f, fmt='%d')
