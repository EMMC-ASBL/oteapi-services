# Open Translation Environment (OTE) API

## Run in Docker

### Development target

The development target will allow for automatic reloading when source code changes.
This requires that the local directory is bind-mounted using the `-v` or `--volume` argument.
To build and run the development target from the command line:

```shell
docker build --rm -f Dockerfile \
    --label "ontotrans.oteapi=development" \
    --target development \
    -t "ontotrans/oteapi-development:latest" .
```

### Production target

The production target will not reload itself on code change and will run a predictable version of the code on port 80.
Also you might want to use a named container with the `--restart=always` option to ensure that the container is restarted indefinitely regardless of the exit status.
To build and run the production target from the command line:

```shell
docker build --rm -f Dockerfile \
    --label "ontotrans.oteapi=production" \
    --target production \
    -t "ontotrans/oteapi:latest" .
```

### Run redis

Redis with persistance needs to run as a prerequisite to starting oteapi.
Redis needs to share the same network as oteapi.

```shell
docker network create -d bridge otenet
docker volume create redis-persist
docker run \
    --detach \
    --name redis \
    --volume redis-persist:/data \
    --network otenet \
    redis:latest
```

### Run oteapi (development)

Run the services by attaching to the otenet network and set the environmental variables for connecting to Redis.

```shell
docker run \
    --rm \
    --network otenet \
    --detach \
    --volume ${PWD}:/app \
    --publish 8080:8080 \
    --env OTEAPI_REDIS_TYPE=redis \
    --env OTEAPI_REDIS_HOST=redis \
    --env OTEAPI_REDIS_PORT=6379 \
    ontotrans/oteapi-development:latest
```

Open the following URL in a browser [http://localhost:8080/redoc](http://localhost:8080/redoc).

One can also use a local `oteapi-core` repository by specifying the `PATH_TO_OTEAPI_CORE` environment variable:

```shell
export PATH_TO_OTEAPI_CORE=/local/path/to/oteapi-core
docker run \
    --rm \
    --network otenet \
    --detach \
    --volume ${PWD}:/app \
    --publish 8080:8080 \
    --env OTEAPI_REDIS_TYPE=redis \
    --env OTEAPI_REDIS_HOST=redis \
    --env OTEAPI_REDIS_PORT=6379 \
    ontotrans/oteapi-development:latest
```

### Run oteapi (production)

Run the services by attaching to the otenet network and set the environmental variables for connecting to Redis.

```shell
docker run \
    --rm \
    --network otenet \
    --detach \
    --publish 80:8080 \
    --env OTEAPI_REDIS_TYPE=redis \
    --env OTEAPI_REDIS_HOST=redis \
    --env OTEAPI_REDIS_PORT=6379 \
    ontotrans/oteapi:latest
```

Open the following URL in a browser [http://localhost:80/redoc](http://localhost:80/redoc).

### Run the Atmoz SFTP Server

To test the data access via SFTP, the atmoz sftp-server can be run:

```shell
docker volume create sftpdrive
PASSWORD="Insert your user password here" docker run \
    --detach \
    --network=otenet \
    --volume sftpdrive:${HOME}/download \
    --publish 2222:22 \
    atmoz/sftp ${USER}:${PASSWORD}:1001
```

For production, SSH public key authentication is preferred.

## Run with Docker Compose (development)

Ensure your current working directory is the root of the repository.
Then run:

```shell
docker-compose -f docker-compose_dev.yml pull  # Pull the latest images
docker-compose -f docker-compose_dev.yml build  # Build the central OTE service (from Dockerfile)
docker-compose -f docker-compose_dev.yml up -d  # Run the OTE Services (detached)
```

Note that default values will be used if certain environment variables are not present.
To inspect which environment variables can be specified, please inspect the [Docker Compose file](docker-compose_dev.yml).

This Docker Compose file will use your local files for the application, meaning updates in your local files (under `app/`) should be reflected in the running application after hypercorn reloads.
You can go one step further and use your local files also for the `oteapi-core` repository by specifying the `PATH_TO_OTEAPI_CORE` environment variable:

```shell
export PATH_TO_OTEAPI_CORE=/local/path/to/oteapi-core
docker-compose -f docker-compose_dev.yml up --build -d  # Run the OTE Services detached, build if necessary
```

To see the logs (in real time) from the server, run:

```shell
docker logs -f oteapi-services-oteapi-1
```

## Run with Docker Compose (production)

Ensure your current working directory is the root of the repository.
Then run:

```shell
docker-compose pull  # Pull the latest images
docker-compose up -d  # Run the OTE Services (detached)
```

Note that default values will be used if certain environment variables are not present.
To inspect which environment variables can be specified, please inspect the [Docker Compose file](docker-compose.yml).
