#!/bin/bash

mkdir -p tmp
mkdir -p output
base_name=$(basename $1)
# remove the extension
base_name_pure=${base_name%.*}

# for contrast
solc --bin-runtime $1 | tail -1 >"output/${base_name}.bin.runtime"
solc --bin $1 | tail -1 >"output/${base_name}.bin"

# source code obfucation
# python3 a/a.py $1 > "tmp/${base_name}_a.sol"
# python3 b/b.py "tmp/${base_name}_a.sol" > "tmp/${base_name}_b.sol"

# CURRENT INPUT FILE: examples/${base_name}
# dataflow obfuscation - Jiang Yihang Part
solc -o tmp/build --bin --ast-compact-json --asm examples/${base_name} --overwrite
python dataflow_obfuscator/split_array.py \
    --sol examples/${base_name} \
    --ast tmp/build/${base_name}_json.ast \
    --output_path ./tmp \
    --output_filename ${base_name_pure}_split_array.sol
solc -o tmp/build --bin --ast-compact-json --asm ./tmp/${base_name_pure}_split_array.sol --overwrite
wait

# layout obfuscation - Jiang Yihang Part
# add variables
python layout_obfuscator/add_variables.py \
    --sol tmp/${base_name_pure}_split_array.sol \
    --ast tmp/build/${base_name_pure}_split_array.sol_json.ast \
    --output_path ./tmp \
    --output_filename ${base_name_pure}_add_variables.sol
solc -o tmp/build --bin --ast-compact-json --asm ./tmp/${base_name_pure}_add_variables.sol --overwrite
wait
# replace variable names
python layout_obfuscator/replace_var_name.py \
    --sol tmp/${base_name_pure}_add_variables.sol \
    --ast tmp/build/${base_name_pure}_add_variables.sol_json.ast \
    --output_path ./tmp \
    --output_filename ${base_name_pure}_replace_var_name.sol

# CURRENT OUTPUT: ./tmp/${base_name_pure}_replace_var_name.sol

python layout_and_data_obfuscation/combination.py ./tmp/${base_name_pure}_replace_var_name.sol ./tmp/${base_name_pure}_ob.sol

# CURRENT OUTPUT: ./tmp/${base_name_pure}_ob.sol

python layout_and_dataflow_obfuscator/obfuscate_solidity.py ./tmp/${base_name_pure}_ob.sol ./tmp/${base_name_pure}_obfuscate.sol

# CURRENT OUTPUT: ./tmp/${base_name_pure}_obfuscate.sol

# bytecode obfuscation
solc --asm-json --overwrite "./tmp/${base_name_pure}_replace_var_name.sol" | tail -1 >"./tmp/${base_name}.asm.json"

node bytecode-obfuscator/instruction_insersion.js "./tmp/${base_name}.asm.json" "./tmp/${base_name}_ii.asm.json" 0.2
node bytecode-obfuscator/opaque_predicate.js "./tmp/${base_name}_ii.asm.json" "./tmp/${base_name}_op.asm.json" 1
node bytecode-obfuscator/random_jump.js "./tmp/${base_name}_op.asm.json" "./tmp/${base_name}_rj.asm.json" 5

solc --import-asm-json --bin-runtime "./tmp/${base_name}_rj.asm.json" | tail -1 >"output/${base_name}_obfuscated.bin.runtime"
solc --import-asm-json --bin "./tmp/${base_name}_rj.asm.json" | tail -1 >"output/${base_name}_obfuscated.bin"
