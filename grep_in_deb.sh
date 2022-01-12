#!/bin/bash


function grep_deb {
	# $1: .deb file path
	# $2: pattern to grep
	# $3: perform it quietly?
	if [ $3 = true ] ;
	then
		dpkg -c $1 | awk '{printf("%s\n", $6)}' - | grep -q $2
	else
		dpkg -c $1 | awk '{printf("%s\n", $6)}' - | grep $2
	fi
}

if [ -z "$1" ]
then
	echo You MUST provide the pattern you want to grep...
	exit 1
fi

echo start grepping $1 in .deb files recurisvely ...

# grep thru all availabl .deb files
eval find . | grep -P ".\.deb$" |
while
	read file
do
	grep_deb "$file" "$1" true
	if [ $? -eq 0 ]
	then
		echo --- Content of $file ---
		grep_deb "$file" "$1" false
	fi
done

