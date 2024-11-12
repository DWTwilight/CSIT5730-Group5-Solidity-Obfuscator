#!/bin/bash

solc -o ./tmp --asm --overwrite $1
solc -o ./tmp --pretty-json --asm-json --overwrite $1
