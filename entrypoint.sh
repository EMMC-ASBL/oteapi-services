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
sed -E -e "s|oteapi-core==[0-9.]+|${oteapi_core_requirement}|" requirements.txt > constraints.txt

if [ -n "${OTEAPI_PLUGIN_PACKAGES}" ]; then
    echo "Installing plugins:"
    # Print out list of plugins in separate for-loop to avoid `pip` message interjections
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do echo "* ${plugin}"; done
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do pip install -q -c constraints.txt ${plugin} || continue; done
    current_packages="$(pip freeze)"
    for plugin in ${OTEAPI_PLUGIN_PACKAGES}; do
        if [[ "${current_package}" != *"${plugin}"* ]]; then
            echo "One or more plugin packages failed to install. See above for more information."
            exit 1
        fi
    done
else
    echo "No extra plugin packages provided. Specify 'OTEAPI_PLUGIN_PACKAGES' to specify plugin packages."
fi

hypercorn asgi:app --bind 0.0.0.0:8080 $@
