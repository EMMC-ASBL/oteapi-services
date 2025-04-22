FROM python:3.10-slim AS base

# Prevent writing .pyc files on the import of source modules
# and set unbuffered mode to ensure logging outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

# Set working directory
WORKDIR /app

# Copy core parts
COPY app app/
COPY requirements.txt LICENSE asgi.py entrypoint.sh ./

# Install system dependencies to support installing plugins for any target
RUN apt-get -qqy update && apt-get -qqy upgrade \
  && apt-get -qqy install --fix-broken --fix-missing --no-install-recommends procps build-essential

# install common requirements
RUN pip install -q --no-cache-dir --upgrade pip setuptools wheel \
  && pip install -q -r requirements.txt

ENTRYPOINT [ "/app/entrypoint.sh" ]

################# DEVELOPMENT ####################################
#
# Set the extra build context "oteapi-core" to point to the local oteapi-core directory.
# This can be set either through `docker build --build-context oteapi-core=/path/to/dir` or
# through the Docker Compose file's `additional_contexts` argument in the `build` section:
# https://docs.docker.com/compose/compose-file/build/#additional_contexts
#
FROM base AS development

## Comment out the following lines to avoid copying a local oteapi-core source code
## When running with Docker Compose, set OTEAPI_CORE_PATH to the path of the oteapi-core source code
COPY --from=oteapi-core . /oteapi-core
RUN pip install --force-reinstall -e /oteapi-core

# Copy development parts
COPY .dev/requirements_dev.txt .dev/requirements_ci.txt .pre-commit-config_docker.yaml pyproject.toml ./

# Install additional development tools in a separate virtual environment
RUN apt-get -qqy update && apt-get -qqy upgrade \
  && apt-get -qqy install --fix-broken --fix-missing --no-install-recommends git git-lfs \
  && apt-get purge -fqqy --auto-remove \
  && apt-get -qqy clean \
  && rm -rf /var/lib/apt/lists/*

# Install additional development requirements
RUN python -m venv /tmp/dev_venv \
  && /tmp/dev_venv/bin/pip install -q --upgrade pip setuptools wheel \
  && /tmp/dev_venv/bin/pip install -q -r requirements_ci.txt

# Run static security check, linters, and pytest with code coverage
RUN --mount=type=cache,target=/root/.cache/pre-commit \
  git init && git add . && /tmp/dev_venv/bin/pre-commit run -c .pre-commit-config_docker.yaml --all-files

# Install extra (non-dev tools) development requirements in main environment
RUN pip install -q -U -r requirements_dev.txt

# Clean up
RUN rm -rf /tmp/* ./.git

ENV DEV_ENV=1

# Run app with reload option during development
EXPOSE 8080 5678
CMD [ "--reload", "--debug", "--log-level=debug" ]

################# PRODUCTION #####################################
FROM base AS production

# Clean up
RUN apt-get purge -fqqy --auto-remove && apt-get -qqy clean && rm -rf /var/lib/apt/lists/* \
  && rm -rf /tmp/*

# Run app in production
EXPOSE 8080
