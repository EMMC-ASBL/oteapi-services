# Open Translation Environment (OTE) API

## Run in Docker

### Development target

The development target will allow for automatic reloading when source code changes.
This requires that the local directory is bind-mounted using the `-v` or `--volume` argument.
To build the development target from the command line:

```shell
docker build --rm -f Dockerfile \
    --label "emmc-asbl.oteapi=development" \
    --target development \
    -t "emmc-asbl/oteapi-development:latest" .
```

### Production target

The production target will not reload itself on code change and will run a predictable version of the code.
Also you might want to use a named container with the `--restart=always` option to ensure that the container is restarted indefinitely regardless of the exit status.
To build the production target from the command line:

```shell
docker build --rm -f Dockerfile \
    --label "oteapi=production" \
    --target production \
    -t "emmc-asbl/oteapi:latest" .
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
    emmc-asbl/oteapi-development:latest
```

One can also use a local `oteapi-core` repository by specifying the `PATH_TO_OTEAPI_CORE` environment variable:

```shell
export PATH_TO_OTEAPI_CORE=/local/path/to/oteapi-core
docker run \
    --rm \
    --network otenet \
    --detach \
    --volume ${PWD}:/app \
    --volume ${PATH_TO_OTEAPI_CORE}:/oteapi_core \
    --publish 8080:8080 \
    --env OTEAPI_REDIS_TYPE=redis \
    --env OTEAPI_REDIS_HOST=redis \
    --env OTEAPI_REDIS_PORT=6379 \
    --env PATH_TO_OTEAPI_CORE \
    ontotrans/oteapi-development:latest
```

Open the following URL in a browser [http://localhost:8080/redoc](http://localhost:8080/redoc).

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
    emmc-asbl/oteapi:latest
```

Open the following URL in a browser [http://localhost/redoc](http://localhost:80/redoc).

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

## Run with Docker Compose

### Run with Docker Compose (development)

Ensure your current working directory is the root of the repository, then run:

```shell
docker-compose -f docker-compose_dev.yml pull  # Pull the latest images
docker-compose -f docker-compose_dev.yml build  # Build the central OTE service (from Dockerfile)
docker-compose -f docker-compose_dev.yml up -d  # Run the OTE Services (detached)
```

Note that default values will be used if certain environment variables are not present.
To inspect which environment variables can be specified, please inspect the [Docker Compose file](docker-compose_dev.yml).

This Docker Compose file will use your local files for the application, meaning updates in your local files (under `app/`) should be reflected in the running application upon storing the changes to disk, after hypercorn reloads.
You can go one step further and use your local files also for the `oteapi-core` repository by specifying the `PATH_TO_OTEAPI_CORE` environment variable:

```shell
export PATH_TO_OTEAPI_CORE=/local/path/to/oteapi-core
docker-compose -f docker-compose_dev.yml up --build -d  # Run the OTE Services detached, build if necessary
```

To see the logs from the OTEAPI service in real time from the server, run:

```shell
docker logs -f oteapi-services-oteapi-1
```

Leave out the `-f` option to write out the log to your terminal without following along and writing out new log messages.

### Run with Docker Compose (production)

Ensure your current working directory is the root of the repository, then run:

```shell
docker-compose pull  # Pull the latest images
docker-compose up -d  # Run the OTE Services (detached)
```

Note that default values will be used if certain environment variables are not present.
To inspect which environment variables can be specified, please inspect the [Docker Compose file](docker-compose.yml).

## OTEAPI Plugin Repositories

To use OTEAPI strategies other than those included in [OTEAPI Core](https://emmc-asbl.github.io/oteapi-core/latest/#types-of-strategies), one can install externally available OTEAPI plugin Python packages.
Currently, there is no index of available plugins, however, there might be in the future.

To install OTEAPI plugin packages for use in the OTEAPI service, one needs to specify the `OTEAPI_PLUGIN_PACKAGES` environment variable when running the service through either [Docker](#run-in-docker) or [Docker Compose](#run-with-docker-compose).
The variable should be a pipe-separated (`|`) string of each package name, possibly including a version range for the given package.

For example, to install the packages `oteapi-plugin` and `my_special_plugin` one could specify `OTEAPI_PLUGIN_PACKAGES` in the following way:

```shell
OTEAPI_PLUGIN_PACKAGES="oteapi-plugin|my_special_plugin"
```

Should there be special version constraints for the packages, these can be added after the package name, separated by commas:

```shell
OTEAPI_PLUGIN_PACKAGES="oteapi-plugin~=1.3|my_special_plugin>=2.1.1,<3,!=2.1.0"
```

To ensure this variable is used when running the service you could either `export` it, set it in the same command line as running the service, or define it in a separate file, telling `docker` or `docker-compose` to use this file as a source of environment variables through the `--env-file` option.

> **Warning**: Beware that the `OTEAPI_PLUGIN_PACKAGES` variable will be run from the `entrypoint.sh` file within the container using the `eval` Bash function.
> This means one can potentially execute arbitrary code by appending it to the `OTEAPI_PLUGIN_PACKAGES` environment variable.
> However, this is mitigated by the fact that this exploit cannot be invoked in an already running instance.
> To be able to exploit this, one would need access to change the `OTEAPI_PLUGIN_PACKAGES` environment variable and restart the running docker containers.
> If anyone has access to do this, they essentially have complete control of the system, and this issue is the least of one's problems.
> But beware too keep the `OTEAPI_PLUGIN_PACKAGES` variable value secret in production and always take proper safety measures for public services.

### For plugin developers

This environment variable allows you to pass _any_ parameters and values to `pip install`, hence you could map a local folder for your plugin repository into the container and use the full path within the container to install the plugin.

If passing it with the `-e` option, it will be an editable installation.
This means any changes in the plugin will be echoed in the service as soon as the file is stored to disk and hypercorn has reloaded.

Example:

```shell
OTEAPI_PLUGIN_PACKAGES="oteapi-plugin~=1.3|my_special_plugin>=2.1.1,<3,!=2.1.0|-v -e /oteapi-plugin-dev[dev]"
```

Here, the constant `-q` (silent) option for `pip install` has been reversed by using the `-v` (verbose) option, and the package at `/oteapi-plugin-dev` within the container is being installed as an editable installation, including the `dev` extra.

Now in the local `docker-compose.yml` file, one would need to add:

```yaml
- "${PWD}:/oteapi-plugin-dev"
```

Under `volumes` under `oteapi`.
Assuming the `docker-compose.yml` file in question is placed in the root of the plugin repository.
If not, the first part (`${PWD}`) should be changed accordingly.

#### Local `oteapi-core`

It is also possible to install a local version of `oteapi-core` using the public image.
To do this, the `ENTRYPOINT` command in the image needs to be overwritten, which can be done with the `entrypoint` value in the docker compose file:

```yaml
entrypoint: |
  /bin/bash -c "if [ \"${PATH_TO_OTEAPI_CORE}\" != \"/dev/null\" ] && [ -n \"${PATH_TO_OTEAPI_CORE}\" ]; then \
  pip install -U --force-reinstall -e /oteapi-core; fi \
  && ./entrypoint.sh --reload --debug --log-level debug"
```

Here the hypercorn command is called with the options `--reload`, `--debug`, and `--log-level debug` as well.
This makes sure we see all relevant logging output during development as well as having the server restart/reload every time a file is updated that relates to the locally installed packages (for the plugins, they need to have the `-e` option invoked - see above.)

A full example of how a docker compose file may look for a plugin is shown below, but can also be seen in the [OTEAPI Plugin template](https://github.com/EMMC-ASBL/oteapi-plugin-template) repository.

In the following example, there is a possibility that a second plugin may be needed (`oteapi-another-plugin`).
This possibility has been expressed in the docker compose file through the `PATH_TO_OTEAPI_ANOTHER_PLUGIN` environment variable.

```yaml
version: "3"

services:
  oteapi:
    image: ghcr.io/emmc-asbl/oteapi:${DOCKER_OTEAPI_VERSION:-latest}
    ports:
      - "${PORT:-8080}:8080"
    environment:
      OTEAPI_REDIS_TYPE: redis
      OTEAPI_REDIS_HOST: redis
      OTEAPI_REDIS_PORT: 6379
      OTEAPI_prefix: "${OTEAPI_prefix:-/api/v1}"
      PATH_TO_OTEAPI_CORE:
      # default
      OTEAPI_PLUGIN_PACKAGES: "-v -e /oteapi-plugin[dev]"

      # use this if PATH_TO_OTEAPI_ANOTHER_PLUGIN is defined
      # OTEAPI_PLUGIN_PACKAGES: "-v -e /oteapi-plugin[dev]:-v -e /oteapi-another-plugin"
    depends_on:
      - redis
    networks:
      - otenet
    volumes:
      - "${PATH_TO_OTEAPI_CORE:-/dev/null}:/oteapi-core"
      - "${PATH_TO_OTEAPI_ANOTHER_PLUGIN:-/dev/null}:/oteapi-another-plugin"
      - "${PWD}:/oteapi-plugin"
    entrypoint: |
      /bin/bash -c "if [ \"${PATH_TO_OTEAPI_CORE}\" != \"/dev/null\" ] && [ -n \"${PATH_TO_OTEAPI_CORE}\" ]; then \
      pip install -U --force-reinstall -e /oteapi-core; fi \
      && ./entrypoint.sh --reload --debug --log-level debug"

  redis:
    image: redis:latest
    volumes:
      - redis-persist:/data
    networks:
      - otenet

  sftp:
    image: atmoz/sftp
    volumes:
      - sftp-storage:${HOME:-/home/foo}/download
    command: ${USER:-foo}:${PASSWORD:-pass}:1001
    networks:
      - otenet

volumes:
  redis-persist:
  sftp-storage:

networks:
  otenet:
```


## Acknowledgment

OTEAPI Core has been supported by the following projects:

* __OntoTrans__ (2020-2024) that receives funding from the European Union’s Horizon 2020 Research and Innovation Programme, under Grant Agreement no. 862136.

* __VIPCOAT__ (2021-2025) receives funding from the European Union’s Horizon 2020 Research and Innovation Programme - DT-NMBP-11-2020 Open Innovation Platform for Materials Modelling, under Grant Agreement no: 952903.

* __OpenModel__ (2021-2025) receives funding from the European Union’s Horizon 2020 Research and Innovation Programme - DT-NMBP-11-2020 Open Innovation Platform for Materials Modelling, under Grant Agreement no: 953167.
