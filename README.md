# Quickdish

## Setup

Set up the Python viirtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -e .
```

Set up the `.env` file at the root of the project:

```env
DATABASE_URL=...
JWT_SECRET=...
ALLOW_ORIGINS=...
ALLOW_METHODS=...
ALLOW_HEADERS=...
```

where `DATABASE_URL` is the URL of the PostgreSQL database and `JWT_SECRET` is
any arbitrary random string used to sign the JWT tokens.

The ALLOW\_\* variables are used to set the CORS policy.

**NOTE:** ALLOW_ORIGINS should be the URL of the frontend.

## Running the Server

Server must be run on the root of the project directory:

```bash
fastapi dev api/__init__.py
```

## Running the Tests

```bash
pytest api/tests/*.py
```

## Running the Tests with Coverage Info

```bash
pytest --cov=api --cov-report=lcov:lcov.info --cov-report=term api/tests/*.py
```
