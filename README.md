# CSIT5730-Group5-Solidity-Obfuscator

## Requirements

- solc ^0.8.28
- node.js ^18.19.1
- python ^3.12 (with dependencies in `requirements.txt`)
- npm ^9.2.0 (for testing)

## Usage

```sh
pip install -r requirements.txt

./solidity_obfuscator.sh ${.sol filePath}
```

- obfuscated source code: `/output/${fileName}_obfusacted.sol`
- obfuscated binary: `/output/${fileName}.sol_obfuscated.bin`
- obfuscated runtime binary: `/output/${fileName}.sol_obfuscated.bin.runtime`

## Test with Obfuscated Binary

- go to `/gas-consumption-benchmark`
- install dependencies with `npm install`
- put original contract file to `/gas-consumption-benchmark/contracts`
- use `npx hardhat clean; npx hardhat compile` to build original contract
- run `solidity_obfuscator.sh` on original contract and get obfusacted binary
- go to `/gas-consumption-benchmark/artifacts/contracts` and find target contract folder
- edit `${contractName}.json`, rewrite `bytecode` to `${fileName}.sol_obfuscated.bin`, rewrite `deployedBytecode` to `${fileName}.sol_obfuscated.bin.runtime`
- run `npx hardhat test --no-compile`

## Resources

- Solidity Document: https://docs.soliditylang.org/en/v0.8.27/
- Install solc: https://docs.soliditylang.org/en/latest/installing-solidity.html
- solc usage: https://docs.soliditylang.org/en/latest/using-the-compiler.html
- Bytecode decompiler: https://app.dedaub.com/decompile?network=ethereum
- EVM opcode: https://github.com/wolflo/evm-opcodes
