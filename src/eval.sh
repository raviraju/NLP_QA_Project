#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <output_file>"
  exit 1
fi
file=$1
echo "Total no of outputs to evaluate:"
wc -l $file
echo "No of Correct(1)/InCorrect(0) Matches:"
cat $file | awk '{print ($2 == $3)}' | sort | uniq -c
