mkdir -p tmp
mkdir -p output
base_name=$(basename $1)
# remove the extension
base_name_pure=${base_name%.*}

# for contrast
solc --bin-runtime $1 | tail -1 >"output/${base_name}.bin.runtime"
solc --bin $1 | tail -1 >"output/${base_name}.bin"

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