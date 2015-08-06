#!/bin/bash

# run process through gdb instead

DIRNAME=$(dirname $0)
set -x
gdb -q --eval-command="run" --eval-command="thread apply all bt" --eval-command="quit" --args ${DIRNAME}/qdoc.orig $@

