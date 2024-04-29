#!/bin/bash

if [[ $FUSRR_RUN_TYPE == "examples" ]]; then
    ./scripts/run_examples.sh
elif [[ $FUSRR_RUN_TYPE == "tests" ]]; then
    ./scripts/run_tests_w_cov.sh
else
    echo "Invalid FUSRR_RUN_TYPE '$FUSRR_RUN_TYPE'. Please set it to either 'examples' or 'tests'."
    exit 1
fi