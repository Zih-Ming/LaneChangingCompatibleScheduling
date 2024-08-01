#!/bin/bash
python_program="./sa.py"
num_runs=$1

if [ "$#" -eq 2 ]; then
    output_file=$2

    if [ -f "$output_file" ]; then
        rm -f "$output_file"
        # echo "Error: $output_file already exists. Choose a different file name."
        # exit 1
    fi

    touch "$output_file"

    python3 "$python_program" "$num_runs" | tee -a "$output_file"
else
    python3 "$python_program" "$num_runs"
fi