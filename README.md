# sensors
Repository for the sensors reader solution deployed on a Raspberry PI

## How to run the solution locally

The project is developed in Python 3.12, you have to install it beforehand to start working, here are the steps.

- Install Python framework from [here](https://www.python.org/).
- Install [Pipenv](https://pipenv.pypa.io/en/latest/).
- Download the solution and create a virtual environment locally to it, it is similar to the folder node_modules in
  NodeJS projects.

```
export PIPENV_VENV_IN_PROJECT=1
pipenv --python 3.12
```

- Install the dependencies, it is similar to the npm install command from NodeJS projects.

```
export PIPENV_URL=https://pypi.org/simple
pipenv install --dev
```

- Install pre-commit hooks to ensure the code quality.

```
 ./.venv/bin/pre-commit install
```
