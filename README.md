# sensors
Repository for the sensors reader solution deployed on a Raspberry PI

## How to run the solution locally

The project is developed in Python 3.13, you have to install it beforehand to start working, here are the steps.

```
rm -rf .venv
export PIPENV_VENV_IN_PROJECT=1
pipenv --python 3.13
pipenv install --dev
 ./.venv/bin/pre-commit install
```
