FROM ubuntu:21.04 as base

# Prevent writing .pyc files on the import of source modules
# and set unbuffered mode to ensure logging outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

RUN apt-get -qq update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -qq -y --fix-missing \
    python3-dev \
    python3-pip \
    curl \
    git

# Install requirements
COPY requirements.txt .
RUN pip install -q --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com -r requirements.txt


################# DEVELOPMENT ####################################
FROM base as development

# Run static security check and linters
COPY requirements_dev.txt .
RUN pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements_dev.txt

# Copy in all files - would it be better to copy selectively?
COPY . .

# Ignore ID 44715 for now.
# See this NumPy issue for more information: https://github.com/numpy/numpy/issues/19038
RUN pre-commit run --all-files  \
  && safety check -r requirements.txt -r requirements_dev.txt --ignore 44715

# Run pytest with code coverage
RUN pytest --cov app

# Run with reload option
CMD hypercorn asgi:app --bind 0.0.0.0:8080 --reload
EXPOSE 8080


################# PRODUCTION ####################################
FROM base as production
COPY app asgi.py ./

# Run app
CMD hypercorn asgi:app --bind 0.0.0.0:8080
EXPOSE 8080
