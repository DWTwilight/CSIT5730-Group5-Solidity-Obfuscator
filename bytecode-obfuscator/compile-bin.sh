#!/bin/bash

solc --import-asm-json --bin-runtime $1 >$1.bin.runtime
solc --import-asm-json --bin $1 >$1.bin
