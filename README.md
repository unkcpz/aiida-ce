[![Build Status](https://travis-ci.org/unkcpz/aiida-ce.svg?branch=master)](https://travis-ci.org/unkcpz/aiida-ce)
[![Coverage Status](https://coveralls.io/repos/github/unkcpz/aiida-ce/badge.svg?branch=master)](https://coveralls.io/github/unkcpz/aiida-ce?branch=master)
[![Docs status](https://readthedocs.org/projects/aiida-ce/badge)](http://aiida-ce.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/aiida-ce.svg)](https://badge.fury.io/py/aiida-ce)

# aiida-ce

The aiida-ce is an aiida plugin which running the cluster expansion by using [icet](https://icet.materialsmodeling.org/) a tool for the construction and sampling of alloy cluster expansions as the backend.
The plugin was designed to provided all the functions displayed in [tutorials of icet](https://icet.materialsmodeling.org/tutorial/index.html)

## Features

### orm data type
  * Structures collection for training is represented using `StructureContainer`, it can be initialize from a list of ase structures. Meanwhile, the energies of each structures can be attached to the data to constructed a training set input for `TrainCalculation`.
  ```python
  StructureContainer = DataFactory('ce.structures')
  ```

  * `ClusterSpaceData` is a data type to represent the cluster information used in the cluster expansion process. Though its real data is the information of each cluster, `ClusterSpaceData` store the data by its prototype inputs(primitive structure, cutoffs, chemical symbols). The ClusterSpace is then evaluated in the time of running.
  ```python
  ClusterSpaceData = DataFactory('ce.cluster')
  ```

### calculation job
Because icet is a pythonic package without the executable files, aiida-ce makes the wrappers of different functions as excutatble files.

  *  structure generators: EnumCalculation, SqsCalculation
  ```python
  EnumCalculation = CalculationFactory('ce.genenum')
  SqsCalculation = CalculationFactory('ce.gensqs')
  ```

  * Train the ce model. Inputs are a `StructureContainer` and a `ClusterSpaceData` and the name of fitting method. It will ouput a ce model which can then be used to predict the energies of alloy of the same type.
  ```python
  TrainCalculation = CalculationFactory('ce.train')
  ```

## Installation

```shell
pip install aiida-ce
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```

You need to copy the wrappers into the path in the computer where you gonna to run the executable file.

## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:
```shell
verdi daemon start         # make sure the daemon is running
cd examples
verdi run submit.py        # submit test calculation
verdi process list -a  # check status of calculation
```

The plugin also includes verdi commands to inspect its data types:
```shell
verdi data ce structures list
verdi data ce structures dump <PK>
verdi data ce structures export <PK> <INDEX>

verdi data ce cluster list
verdi data ce cluster show <PK>
verdi data ce cluster dump <PK>
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

morty.yu@yahoo.com
