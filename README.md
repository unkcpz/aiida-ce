# aiida-ce

The aiida-ce is an aiida plugin for icet and ATAT to:

1. Training the cluster expansion (icet only)
2. Generating Special Quasi-random Structure (SQS). (icet and `mcsqs` from ATAT)
3. Enumerating unduplicated structures for cluster expansion. (coming, using icet and [enumlib](https://github.com/msg-byu/enumlib))
4. Sampling the cluster expansion using Monte Carlo simulation at different ensembles (coming)
5. Giving the phase diagram of simple alloy, include running the property (energy only) evaluation of structures with aiida-common-workflow. (coming)

The plugin in going to provide all the functions displayed in [tutorials of icet](https://icet.materialsmodeling.org/tutorial/index.html).
Moreover, it can be used to complete a throught cluster expansion study on alloy systems.

## data type
  * `StructureDBData` is to represent a collection of structures with their properties (mostly the energies, if given). Structures are stored as a ase database with sqllite in the aiida file repository. This data type is the input of the cluster expansion training if the properties of the structures are also stored. If the properties are not calculated, this data type is the input of a energy evaluation workflow which give a `StructureDBData` as output with all structures tagged with their evaluated energies.

  ```python
  StructureDBData = DataFactory('structure_db')
  ```

  * `ClusterSpaceData` is a data type to represent the cluster information used in the cluster expansion process.
  ```python
  ClusterSpaceData = DataFactory('cluster_space')
  ```

  * `ClusterExpansioneData` is a data type to represent the cluster expansion information. It can be used to predict the energy of specific configurations.
  ```python
  ClusterExpansionData = DataFactory('cluster_expansion')
  ```

## Usage

### Special Quasi-random Structure (SQS)

The SQS generation is implement for both icet and ATAT. Since icet is a python library the engine to generate SQS is installed as a library with `aiida-ce` plugin, this makes running a long time calculation become unfeasiable. If you are going to generating SQS with big supercell and long distance cutoff, it is strongly recommend to run SQS with the `mcsqs` engine by `AtatMcsqsCalculation`.

Here is a simple example of generating SQS with icet engine:
```python
from aiida import orm
from aiida.engine import run_get_node
from aiida.plugins import WorkflowFactory, DataFactory

from ase.build import bulk

ClusterExpansionData = DataFactory('cluster_expansion')
IcetSqsWorkChain = WorkflowFactory('icet.sqs')

cluster_space_data = ClusterSpaceData()
cluster_space_data.set(ase=bulk('Au'),
                      cutoffs=[7.0, 4.5],
                      chemical_symbols=[['Au', 'Pd']])

supercell = orm.StructureData(ase=generate_ase_structure('Au1x2x4'))

inputs = {
    'cluster_space': cluster_space_data,
    'supercell': supercell,
    'n_steps': orm.Int(1000),
    'random_seed': orm.Int(1234),
    'target_concentrations': orm.Dict(dict={'Au': 0.5, 'Pd': 0.5})
}

res, node = run_get_node(IcetSqsWorkChain, **inputs)
sqs = res['output_structure']
```

In the example above, user create a cluster space which contain the cluster information for further calculation, and then running sqs process to get the best sqs structure in a 1x2x4 supercell.

Here is a example of generating SQS with ATAT's `mcsqs` engine:
```python
from aiida import orm
from aiida.plugins import CalculationFactory

McsqsCalculation = CalculationFactory('atat.mcsqs')

primitive_structure = orm.StructureData(cell=[[1.,0,0],[0.5,0.866,0,],[0.,0.,1.63333]])
primitive_structure.append_atom(position=[0.,0.,0.], symbols=['Ni', 'Fe'], weights=[0.5,0.5], name='NiFe1')
primitive_structure.append_atom(position=[0.,0.57735,0.81666], symbols=['Ni', 'Fe'], weights=[0.5,0.5], name='NiFe2')

supercell = orm.StructureData(cell=[[2., 0., 0.], [1., 1.7321, 0.], [0., 0., 3.26666]])

inputs = {
    'code': <code atat.mcsqs>,
    'code_corrdump': <code atat.corrdump>,
    'primitive_structure': primitive_structure,
    'sqscell': supercell,
}

res, node = run_get_node(McsqsCalculation, **inputs)
sqs = res['bestcorr']
```

### Evaluation the properties(energies only) of structures for cluster expansion

### Running cluster expansion and predict energy of a given configuration

## Installation

```shell
pip install aiida-ce
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```

## Development

```shell
git clone https://github.com/unkcpz/aiida-ce .
cd aiida-ce
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-ce.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT


## Contact

morty.yeu@gmail.com
