#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <output_file>"
  exit 1
fi
file=$1
echo "Total:"
wc -l $file
echo "Correct:"
cat $file | awk '{print ($2 == $3)}' | sort | uniq -c
