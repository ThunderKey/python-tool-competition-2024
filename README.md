# Python Tool Competition Runner

![GitHub Actions](https://github.com/ThunderKey/python-tool-competition-2024/actions/workflows/check.yaml/badge.svg)

## Usage

### Installation

This tool requires Python 3.11 and [poetry](https://python-poetry.org/).

`pip install git+ssh://git@github.com/ThunderKey/python-tool-competition-2024.git`
(until made public)

### Creating a New Test Generator Project

Run `python-tool-competition-2024 init` and follow the instructions on screen.

This will create a [poetry](https://python-poetry.org/) project with all
required files.
It creates a template of the generator and exposes it as a plugin of the
competition runner.

Additionally, some very basic example targets are created as well.
You can add your own files to the `targets` directory.

Now you can implement the `build_test` function of your generator.
This will be called for each target file and it expects that either a
`TestGenerationSuccess` or `TestGenerationFailure` is returned.
The success contains the body of the generated test file.
Storing the file is handled by the runner that runs `build_test`.
The failure contains a reason and lines that describe the failure.

For examples see:

* <https://github.com/ThunderKey/python-tool-competition-2024-klara>
* <https://github.com/ThunderKey/python-tool-competition-2024-hypothesis-ghostwriter>

### Running inside of the Project

Inside of the create project run
`poetry run python-tool-competition-2024 run <generator name>`.

With `poetry run python-tool-competition-2024 run -h` you can find out what
generators were detected.

The tool does not only execute the test generator, it also runs the generated tests
against the code to measure different metrics: it measures line and branch coverage
using the [coverage](https://github.com/nedbat/coveragepy) framework;
it furthermore computes [mutation score](https://en.wikipedia.org/wiki/Mutation_testing)
utilizing the [cosmic-ray](https://github.com/sixty-north/cosmic-ray) tool.

## Improving the Competition Runner

* Installation: `poetry install`
* Testing: `tox` (`tox -p auto` for parallel execution)
* Use [pre-commit](https://pre-commit.com/) if possible.
