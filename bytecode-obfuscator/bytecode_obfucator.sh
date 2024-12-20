#!/bin/bash

mkdir -p tmp
mkdir -p output
base_name=$(basename $1)

solc --asm-json --overwrite $1 | tail -1 >"./tmp/${base_name}.asm.json"

solc --asm --overwrite $1 >"./tmp/${base_name}.asm"

solc --bin-runtime $1 | tail -1 >"output/${base_name}.bin.runtime"
solc --bin $1 | tail -1 >"output/${base_name}.bin"

node bytecode-obfuscator/instruction_insersion.js "./tmp/${base_name}.asm.json" "./tmp/${base_name}_ii.asm.json" 0.2
node bytecode-obfuscator/opaque_predicate.js "./tmp/${base_name}_ii.asm.json" "./tmp/${base_name}_op.asm.json" 1
node bytecode-obfuscator/random_jump.js "./tmp/${base_name}_op.asm.json" "./tmp/${base_name}_rj.asm.json" 5

solc --import-asm-json --bin-runtime "./tmp/${base_name}_rj.asm.json" | tail -1 >"output/${base_name}_obfuscated.bin.runtime"
solc --import-asm-json --bin "./tmp/${base_name}_rj.asm.json" | tail -1 >"output/${base_name}_obfuscated.bin"

solc --import-asm-json --asm "./tmp/${base_name}_rj.asm.json" >"output/${base_name}_obfuscated.asm"
