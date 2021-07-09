#!/bin/bash

function print_usage {
	echo "usage: gitgrep_all.sh '<regexp>' '<date>' ['<invert_regexp>']"
	echo "    <date> can be 'Jun 1 2021' for example"
}

function grep_repo {
	# $1 : regexp
	# $2 : oldest_epoch
	# $3 : invert_regexp
	
	INTER="/tmp/gitgrep_all_buf"

	echo ".....grep in $PWD....."

	git grep -n ${1} $(git rev-list --all --max-age=${2}) > $INTER

	if [ -z "$3" ] ; then
		cat $INTER
	else
		cat $INTER | grep -v $3
	fi
	# clean up
	rm $INTER
}


# usage: gitgrep_all.sh <regexp>
if [[ "$#" < 2 ]]; then
	print_usage
	exit 1
fi

OLDEST_EPOCH=$(date -d "${2}" +%s)

# find in this main repo first
grep_repo $1 $OLDEST_EPOCH $3

for dir in `git submodule | awk '{print $2}'`
do
	#echo $dir
	pushd $dir > /dev/null
	grep_repo $1 $OLDEST_EPOCH $3
	popd > /dev/null
done

