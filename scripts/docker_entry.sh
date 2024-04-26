#!/bin/bash

if [[ $FUSRR_RUN_TYPE == "examples" ]]; then
    ./run_examples.sh
elif [[ $FUSRR_RUN_TYPE == "tests" ]]; then
    ./run_tests.sh
else
    echo "Invalid FUSRR_RUN_TYPE. Please set it to either 'examples' or 'tests'."
    exit 1
fi