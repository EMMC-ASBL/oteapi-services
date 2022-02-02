FROM python:3.9-slim as base

# Prevent writing .pyc files on the import of source modules
# and set unbuffered mode to ensure logging outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install requirements
COPY ./requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip \
  && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com -r requirements.txt

################# DEVELOPMENT ####################################
FROM base as development
COPY . .

# Run static security check, linters, and pytest with code coverage
RUN pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements_dev.txt \
# Ignore ID 44715 for now.
# See this NumPy issue for more information: https://github.com/numpy/numpy/issues/19038
  && pre-commit run --all-files \
  && safety check -r requirements.txt -r requirements_dev.txt --ignore 44715 \
  && pytest --cov app

# Run app with reload option
EXPOSE 8080
CMD hypercorn asgi:app --bind 0.0.0.0:8080 --reload

################# PRODUCTION ####################################
FROM base as production
COPY . .

# Run app
EXPOSE 8080
CMD hypercorn asgi:app --bind 0.0.0.0:8080
