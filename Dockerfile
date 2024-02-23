FROM python:3.9-slim as base

# Prevent writing .pyc files on the import of source modules
# and set unbuffered mode to ensure logging outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy core parts and install requirements
COPY app app/
COPY requirements.txt LICENSE README.md asgi.py entrypoint.sh ./
RUN apt-get update \
  && apt-get -y install --fix-broken --fix-missing --no-install-recommends git build-essential \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip setuptools wheel \
  && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

################# DEVELOPMENT ####################################
FROM base as development

# Copy development parts
COPY tests tests/
COPY .git .git/
COPY .dev/requirements_dev.txt .pre-commit-config.yaml pyproject.toml ./

# Run static security check, linters, and pytest with code coverage
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements_dev.txt
ENV DEV_ENV=1
# Run app with reload option
EXPOSE 8080
CMD if [ "${PATH_TO_OTEAPI_CORE}" != "/dev/null" ] && [ -n "${PATH_TO_OTEAPI_CORE}" ]; then \
  pip install -U --force-reinstall -e /oteapi_core; fi \
  && ./entrypoint.sh --reload --debug --log-level debug

################# PRODUCTION #####################################
FROM base as production

# Run app
EXPOSE 8080
ENTRYPOINT [ "./entrypoint.sh" ]
