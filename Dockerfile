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

RUN curl -L -o /tmp/dlite.deb https://github.com/SINTEF/dlite/releases/download/0.3.1/dlite-0.3.1-x86_64.deb

RUN apt-get install -y -f /tmp/dlite.deb \
  && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY ./requirements.txt .
RUN pip install -q --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com -r requirements.txt
ENV DLITE_ROOT=/usr
ENV DLITE_STORAGES=/app/entities/*.json
ENV PYTHONPATH=/usr/lib64/python3.9/site-packages
RUN mkdir -p /app/entities

################# DEVELOPMENT ####################################
FROM base as development
COPY requirements_dev.txt ./

# Run static security check and linters
RUN pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements_dev.txt

RUN pre-commit run --all-files  \
 && safety check -r requirements.txt -r requirements_dev.txt

# Run pytest with code coverage
RUN pytest --cov app

# Hack for debugging of oteapi-core togeter with oteapi-services:
# This requires to install oteapi locally
#COPY oteapi-core oteapi-core
#RUN pip install -U /app/oteapi-core
#RUN rm -r /usr/local/lib/python3.9/dist-packages/oteapi
#RUN ln -s /app/oteapi-core/oteapi /usr/local/lib/python3.9/dist-packages/oteapi
#RUN python3 -c "import oteapi; oteapi.load_plugins()"  # Quick check


# Run with reload option
CMD hypercorn asgi:app --bind 0.0.0.0:8080 --reload
EXPOSE 8080


################# PRODUCTION ####################################
FROM base as production
COPY . .
# Run app
CMD hypercorn asgi:app --bind 0.0.0.0:8080
EXPOSE 8080
