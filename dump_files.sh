#!/bin/bash

# Usage: ./dump_files.sh *.txt

for file in "$@"
do
    echo === $file ===
    cat $file
done
