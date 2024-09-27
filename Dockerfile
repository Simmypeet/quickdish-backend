FROM python:3.12
WORKDIR /code
COPY ./pyproject.toml /code/pyproject.toml
RUN pip install -e . --no-cache-dir
COPY ./alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations
COPY ./api /code/api