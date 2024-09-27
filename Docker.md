# Docker

## Setting up the Evnironment Variables

Before starting executing the commands, create a file which will hold the
environment variables -- for convenience, name a file that ends with `.env`
so that `.gitignore` can ignore it. Let's name it `docker.env`.

It should look like this:

```bash
DB_NAME=quickdish
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
CONTAINER_PORT=8000
FORWARD_PORT=8000
JWT_SECRET=secret
```

## Running the Docker Container

```bash
docker compose --env-file docker.env up --build
```

This command will build the image and run the container. The backend should be
running on the specified port in the `docker.env` file.

The flag `--build` is used to rebuild the image if there are any changes in the
Dockerfile or the source code.
