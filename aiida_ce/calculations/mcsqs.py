# -*- coding: utf-8 -*-
"""
Calculations of ATAT mcsqs.
"""
from aiida.engine import CalcJob
from aiida.common import CodeInfo, CalcInfo, CodeRunMode

from aiida import orm


class AtatMcsqsCalculation(CalcJob):
    """
    Calculation Job of mcsqs
    """
    _valid_mcsqs_params = ['tol', 'wr', 'wn', 'wd', 'T']

    @classmethod
    def define(cls, spec):
        #yapf: disable
        super().define(spec)
        spec.input('code_corrdump', valid_type=orm.Code,
                   help='The `Code` to run corrdump before mcsqs.')
        spec.input('primitive_structure', valid_type=orm.StructureData,
                   help='primitive structure with fraction atom weight in sites.')
        spec.input('supercell', valid_type=orm.StructureData,
                   help='sqscell receieve a StructureData and read its cell.')
        spec.input('cutoffs', valid_type=orm.List,
                   help='cutoff distance of different order particles.')
        spec.input('random_seed', valid_type=orm.Int, default=lambda: orm.Int(1234),
                    help='seed for the random number generator used in the Monte Carlo simulation')
        spec.input('parameters', valid_type=orm.Dict, required=False,
                   help='option parameters for mcsqs.')

        spec.output('bestsqs', valid_type=orm.StructureData, help='sqs structure file')
        spec.output('bestcorr', valid_type=orm.Float, help='bestcorr of sqs')

        spec.input('metadata.options.parser_name', valid_type=str, default='atat.mcsqs')
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines': 1})
        spec.input('metadata.options.max_wallclock_seconds', valid_type=int, default=1800, required=True)
        spec.input('metadata.options.input_rndstr_filename', valid_type=str, default='rndstr.in')
        spec.input('metadata.options.input_sqscell_filename', valid_type=str, default='sqscell.out')
        spec.input('metadata.options.output_bestsqs_filename', valid_type=str, default='bestsqs.out')
        spec.input('metadata.options.output_bestcorr_filename', valid_type=str, default='bestcorr.out')

    def _get_cmdline_params(self):
        """cmdline params"""
        params = ['-rc']
        params.append(f'-sd={self.inputs.random_seed.value}')

        more_params = self.inputs.parameters.get_dict()
        for key, value in more_params.items():
            if key in self._valid_mcsqs_params:
                params.append(f'-{key}={value}')

        return params

    def prepare_for_submission(self, folder):
        """
        In preparing the inputs of mcsqs, first generate a clusters.out which
        contains the clusters information and then run `mcsqs`.
        """
        rndstr = self._generate_rndstr(self.inputs.primitive_structure)
        with folder.open(self.options.input_rndstr_filename, 'w', encoding='utf8') as handle:
            handle.write(rndstr)

        sqscellstr = self._generate_sqscell(self.inputs.supercell)
        with folder.open(self.options.input_sqscell_filename, 'w', encoding='utf8') as handle:
            handle.write(sqscellstr)

        helpercodeinfo = CodeInfo()
        helpercodeinfo.code_uuid = self.inputs.code_corrdump.uuid

        cmdline_cutoff = []
        for idx, cutoff in enumerate(self.inputs.cutoffs.get_list()):
            cmdline_cutoff.append(f'-{idx+2}={cutoff}')

        helpercodeinfo.cmdline_params = ['-ro', '-noe', '-nop', '-clus',
                                        f'-l={self.options.input_rndstr_filename}'] + cmdline_cutoff

        helpercodeinfo.withmpi = False

        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = self._get_cmdline_params()
        codeinfo.withmpi = False

        calcinfo = CalcInfo()
        calcinfo.codes_info = [helpercodeinfo, codeinfo]
        calcinfo.codes_run_mode = CodeRunMode.SERIAL
        calcinfo.retrieve_list = [self.options.output_bestcorr_filename, self.options.output_bestsqs_filename]

        return calcinfo

    @staticmethod
    def _generate_rndstr(structure: orm.StructureData) -> str:
        """return the str content write to rndstr.in"""
        # write cell
        content = """1 1 1 90 90 90\n"""
        for vector in structure.cell:
            content += '{0:<18.10f} {1:<18.10f} {2:<18.10f} \n'.format(*vector)

        for site, kind in zip(structure.sites, structure.kinds):
            str_pos = '{0:<18.10f} {1:<18.10f} {2:<18.10f} '.format(*site.position)

            str_kind_list = []
            for symbol, weight in zip(kind.symbols, kind.weights):
                str_kind_list.append(f'{symbol}={weight}')

            if kind.has_vacancies: # internal tolerance is 1.e-6, increase to 1.e-4
                weight = 1 - sum(kind.weights)
                if weight > 1.e-4:
                    str_kind_list.append(f'Vac={weight}')

            str_kinds = ', '.join(str_kind_list)
            content += str_pos + str_kinds + '\n'

        return content

    @staticmethod
    def _generate_sqscell(structure: orm.StructureData) -> str:
        """return the str content write to sqscell"""

        content = """1\n\n"""

        for vector in structure.cell:
            content += '{0:<18.10f} {1:<18.10f} {2:<18.10f} \n'.format(*vector)

        return content
