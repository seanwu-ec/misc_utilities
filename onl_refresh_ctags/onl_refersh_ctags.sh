#!/bin/bash

CTAGS_DIRS_SRC_FILE="/home/ubuntu/sean_upload/onl_ctags_dirs.txt"
CTAGS_DIRS_INT_FILE="/tmp/onl_ctags_dirs.txt"

sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g'  ${CTAGS_DIRS_SRC_FILE} > ${CTAGS_DIRS_INT_FILE}

CTAGS_DIRS=`cat ${CTAGS_DIRS_INT_FILE}`
find ${CTAGS_DIRS} -iname "*.c" -o -iname "*.h" -o -iname "*.cpp" -o -iname "Makefile" > cscope.files
cscope -Rbq -i cscope.files

