#!/usr/bin/env bash
# Bash script to run upon starting the Dockerfile.
# The purpose of this script is to install desired plugin packages.
# Only packages that support the current list of pinned requirements version are
# installed, see `requirements.txt`.
#
# Any extra parameters supplied to this script will be passed on to `hypercorn`.
# This is relevant for, e.g., the `development` target.
set -e

# If a custom `oteapi-core` version is installed, the version for it may differ from
# that given in `requirements.txt`. To work around this, we copy the `requirements.txt`
# file into a `constraints.txt` file and replace the `oteapi-core` version there with
# the one currently installed. The `constraints.txt` file is then used as a hard
# constraint when installing the plugin packages. I.e., the plugin packages cannot change the versions of the
# already installed packages.
oteapi_core_requirement="$(pip list --format=freeze --include-editable | grep 'oteapi-core')"
sed -E -e "s|oteapi-core==.*|${oteapi_core_requirement}|" requirements.txt > constraints.txt

if [ -n "${OTEAPI_PLUGIN_PACKAGES}" ]; then
    echo "Installing plugins:"
    # Print out list of plugins in separate for-loop to avoid `pip` message interjections
    IFS="|"
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do echo "* ${plugin}"; done
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do eval "pip install -q -c constraints.txt ${plugin}" || FAILED_PLUGIN_INSTALLS=${FAILED_PLUGIN_INSTALLS:+$FAILED_PLUGIN_INSTALLS:}${plugin} && continue; done
    current_packages="$(pip freeze)"
    if [ -n "${FAILED_PLUGIN_INSTALLS}" ]; then
        echo "The following plugins failed to install:"
        for plugin in ${FAILED_PLUGIN_INSTALLS}; do echo "* ${plugin}"; done
        exit 1
    fi
else
    echo "No extra plugin packages provided. Specify 'OTEAPI_PLUGIN_PACKAGES' to specify plugin packages."
fi

if [ "$DEV_ENV" = "1" ]; then
    python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m hypercorn --bind 0.0.0.0:8080 asgi:app "$@"
else
    hypercorn --bind 0.0.0.0:8080 asgi:app "$@"
fi
