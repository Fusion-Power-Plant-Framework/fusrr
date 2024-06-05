#!/bin/bash

set -e

if [[ $FUSRR_RUN_TYPE == "examples" ]]; then
    hatch run docker-examples:run
elif [[ $FUSRR_RUN_TYPE == "tests" ]]; then
    hatch run test:cov-all
else
    echo "Invalid FUSRR_RUN_TYPE '$FUSRR_RUN_TYPE'. Please set it to either 'examples' or 'tests'."
    exit 1
fi
