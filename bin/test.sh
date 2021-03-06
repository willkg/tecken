#!/usr/bin/env bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -eo pipefail

# copy the .env template to .env if not there already
[ ! -f .env ] && cp .env-dist .env

# default variables
export DEVELOPMENT=1
export DJANGO_CONFIGURATION=Test

# run docker compose with the given environment variables

if [[ -n "${CI}" ]]; then
    # pass CI env vars into docker containers for codecov submission
    echo "Getting Codecov environment variables"
    export CI_ENV=`bash <(curl -s https://codecov.io/env)`

    docker-compose run -e DEVELOPMENT -e DJANGO_CONFIGURATION $CI_ENV test-ci test $@
else
    docker-compose run -e DEVELOPMENT -e DJANGO_CONFIGURATION test test $@
fi
