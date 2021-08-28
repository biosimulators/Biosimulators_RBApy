[![Latest release](https://img.shields.io/github/v/tag/biosimulators/Biosimulators_RBApy)](https://github.com/biosimulations/Biosimulators_RBApy/releases)
[![PyPI](https://img.shields.io/pypi/v/biosimulators_rbapy)](https://pypi.org/project/biosimulators_rbapy/)
[![CI status](https://github.com/biosimulators/Biosimulators_RBApy/workflows/Continuous%20integration/badge.svg)](https://github.com/biosimulators/Biosimulators_RBApy/actions?query=workflow%3A%22Continuous+integration%22)
[![Test coverage](https://codecov.io/gh/biosimulators/Biosimulators_RBApy/branch/dev/graph/badge.svg)](https://codecov.io/gh/biosimulators/Biosimulators_RBApy)

# BioSimulators-RBApy
BioSimulators-compliant command-line interface to the [RBApy](https://sysbioinra.github.io/RBApy/) simulation program for Resource Balance Analysis (RBA) models.

This command-line interface and Docker image enable users to use RBApy to execute [COMBINE/OMEX archives](https://combinearchive.org/) that describe one or more simulation experiments (in [SED-ML format](https://sed-ml.org)) of one or more RBA models in the [RBApy format](https://sysbioinra.github.io/RBApy/usage.html).

A list of the algorithms and algorithm parameters supported by RBApy is available at [BioSimulators](https://biosimulators.org/simulators/rbapy).

A simple web application and web service for using RBApy to execute COMBINE/OMEX archives is also available at [runBioSimulations](https://run.biosimulations.org).

## Installation

### Install Python package

1. Install requirements
   * [Python](https://python.org)
   * [Pip](https://pip.pypa.io/)
   * [IBM CPLEX](https://www.ibm.com/analytics/cplex-optimizer)
   * [IBM CPLEX Python API](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-setting-up-python-api)
   * [RBApy](https://sysbioinra.github.io/RBApy/)
2. Install this package
   ```
   pip install biosimulators-rbapy
   ```

### Install Docker image
```
docker pull ghcr.io/biosimulators/rbapy
```

## Usage

### Local usage
```
usage: biosimulators-rbapy [-h] [-d] [-q] -i ARCHIVE [-o OUT_DIR] [-v]

BioSimulators-compliant command-line interface to the RBApy simulation program <https://sysbioinra.github.io/RBApy/>.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           full application debug mode
  -q, --quiet           suppress all console output
  -i ARCHIVE, --archive ARCHIVE
                        Path to OMEX file which contains one or more SED-ML-
                        encoded simulation experiments
  -o OUT_DIR, --out-dir OUT_DIR
                        Directory to save outputs
  -v, --version         show program's version number and exit
```

### Usage through Docker container
The entrypoint to the Docker image supports the same command-line interface described above.

For example, the following command could be used to use the Docker image to execute the COMBINE/OMEX archive `./modeling-study.omex` and save its outputs to `./`.

```
docker run \
  --tty \
  --rm \
  --mount type=bind,source="$(pwd)",target=/root/in,readonly \
  --mount type=bind,source="$(pwd)",target=/root/out \
  ghcr.io/biosimulators/rbapy:latest \
    -i /root/in/modeling-study.omex \
    -o /root/out
```

## Documentation
Documentation is available at https://docs.biosimulators.org/Biosimulators_RBApy/.

## License
This package is released under the [MIT license](LICENSE).

## Development team
This package was developed by the [Center for Reproducible Biomedical Modeling](http://reproduciblebiomodels.org) and the [Karr Lab](https://www.karrlab.org) at the Icahn School of Medicine at Mount Sinai in New York.

## Questions and comments
Please contact the [BioSimulators Team](mailto:info@biosimulators.org) with any questions or comments.
