![CI](https://github.com/cosmofactory/triptip_backend/actions/workflows/push.yml/badge.svg)

# TripTip project - triptip_backend

Backend part of travel portal TripTip


**To run this project do the following:**

1. Install poetry dependencies:

```bash
make install_dependents
```

2. Cope environment sample
```bash
cp .env_sample .env
```

3. Run project:

Locally:

```bash
make run_trip_tip_backend_locally
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
