#!/bin/bash

export CURDIR=$(pwd)
# First Empty path required to force frozen kooji to be found in firmware
# See https://github.com/micropython/micropython/issues/2322 for details
export MICROPYPATH=":$HOME/.micropython/lib:/usr/lib/micropython:$CURDIR"
echo $MICROPYPATH

for TEST_FILE in $(ls kooji/motor/*_test.py); do
  IMPORT_NAME="${TEST_FILE%.*}"
  echo "Testing $IMPORT_NAME"
  micropython-dev $TEST_FILE

  if [ $? -ne 0 ]; then
    echo "Failed test in $TEST_FILE"
    exit 1
  fi
done

echo "All tests passed."