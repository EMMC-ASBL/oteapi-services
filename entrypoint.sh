#!/usr/bin/env bash
# Bash script to run upon starting the Dockerfile.
# The purpose of this script is to install desired plugin packages.
# Only packages that support the current list of pinned requirements version are
# installed, see `requirements.txt`.
#
# Any extra parameters supplied to this script will be passed on to `hypercorn`.
# This is relevant for, e.g., the `development` target.
set -e

# If a custom `oteapi-core` version is installed, the package versions may differ from
# those given in `requirements.txt`. To work around this, we store the currently
# packages in a `constraints.txt` file to be used as a hard constraint when installing
# the plugin packages. I.e., the plugin packages cannot change the versions of the
# already installed packages.
pip list --format=freeze --include-editable --not-required > constraints.txt

if [ -n "${OTEAPI_PLUGIN_PACKAGES}" ]; then
    echo "Installing plugins:"
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do echo "* ${plugin}"; done
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do pip install -q -c constraints.txt ${plugin} || continue; done
else
    echo "No extra plugin packages provided. Specify 'OTEAPI_PLUGIN_PACKAGES' to specify plugin packages."
fi

hypercorn asgi:app --bind 0.0.0.0:8080 $@
