![Python](https://img.shields.io/badge/python-3.12.2-blue.svg)
![CI](https://github.com/cosmofactory/triptip_backend/actions/workflows/push.yml/badge.svg)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/cosmofactory/triptip_backend.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/cosmofactory/triptip_backend)


# TripTip project - triptip_backend

Backend part of travel portal TripTip

## Preparation 

Before you start, make sure you have the following installed:

- Python 3.12+ (Make sure Python is added to your PATH)

- [uv](https://docs.astral.sh/uv/getting-started/) (for dependency management)
## Installation

Install uv with our standalone installers:

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or, from [PyPI](https://pypi.org/project/uv/):

```bash
# With pip.
pip install uv
```

```bash
# Or pipx.
pipx install uv
```

If installed via the standalone installer, uv can update itself to the latest version:

```bash
uv self update
```

See the [installation documentation](https://docs.astral.sh/uv/getting-started/installation/) for
details and alternative installation methods.

## Documentation

uv's documentation is available at [docs.astral.sh/uv](https://docs.astral.sh/uv).

Additionally, the command line reference documentation can be viewed with `uv help`.

## Features

### Projects

uv manages project dependencies and environments, with support for lockfiles, workspaces, and more,
similar to `rye` or `poetry`:

**To run this project do the following:**

1. Install poetry dependencies:

```bash
uv venv
```
2. Install venv:
```bash
source .venv/bin/activate
```
3. Sync dependencies:
```bash
uv sync
```

4. Copy environment sample
```bash
cp .env_sample .env
```

5. Run project:

Locally:

```bash
make run
```

In container:

```bash
make run_trip_tip_backend_in_container
```


[API Documentation](http://127.0.0.1:8000/docs)

***Code style:***

1. Use black style - [Black style guide](https://black.readthedocs.io/en/stable/);

2. Line length 100 symbols;

3. Don't forget to docstring and comment. 




**Current stack:**

Python 3.12, FastAPI, Uvicorn, Postgres, Docker, pytest, nginx, Ruff

**Creators:**

[Ivan Murzinov](https://github.com/IMurzinov) *Frontend, Project Founder* 

[Polina Bykova](https://github.com/pnbykova) *UX/UI*  

[Pavel Surint](https://github.com/PavelHightTower) *QA/Backend* 

[Nikita Assorov](https://github.com/cosmofactory) *Backend* 
