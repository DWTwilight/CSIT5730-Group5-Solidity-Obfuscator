#!/bin/bash
solc -o examples/output --bin --ast-compact-json --asm examples/example.sol --overwrite
python dataflow_ob/split_array.py \
        --sol examples/example.sol \
        --ast examples/output/example.sol_json.ast \
        --output_path ./tmp \
        --output_filename split_array.sol

solc -o ./tmp/output --bin --ast-compact-json --asm ./tmp/split_array.sol --overwrite
wait
python layout_ob/add_variables.py \
        --sol tmp/split_array.sol \
        --ast tmp/output/split_array.sol_json.ast \
        --output_path ./tmp \
        --output_filename add_variables.sol

solc -o ./tmp/output --bin --ast-compact-json --asm ./tmp/add_variables.sol --overwrite
wait
python layout_ob/replace_var_name.py \
        --sol tmp/add_variables.sol \
        --ast tmp/output/add_variables.sol_json.ast \
        --output_path ./tmp \
        --output_filename replace_var_name.sol
