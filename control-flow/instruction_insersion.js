const fs = require("fs").promises;
const { Opcode, createInstruction, dup, swap } = require("./evm_opcode");

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const ratio = parseFloat(process.argv[4]) || 0.5;

const TARGET_OPCODE = [
  Opcode.ADD,
  Opcode.MUL,
  Opcode.SUB,
  Opcode.DIV,
  Opcode.MOD,
  Opcode.EXP,
];

function injectInstruction(asm, ratio) {
  let res = [...asm];
  startIndex = 0;
  while (startIndex < res.length) {
    if (TARGET_OPCODE.includes(res[startIndex].name) && Math.random() < ratio) {
      let junkCode = [];
      junkCode.push(createInstruction(dup(2)));
      junkCode.push(createInstruction(swap(1)));
      junkCode.push(createInstruction(res[startIndex].name));
      junkCode.push(createInstruction(swap(1)));
      junkCode.push(createInstruction(Opcode.POP));

      res = [
        ...res.slice(0, startIndex),
        ...junkCode,
        ...res.slice(startIndex + 1),
      ];
      startIndex += 4;
    }
    startIndex++;
  }
  return res;
}

(async () => {
  let bytecodeJson = JSON.parse(await fs.readFile(inputPath, "utf8"));

  const runtimeAsm = bytecodeJson[".data"]["0"][".code"];
  // get the target code section
  let sourceAsm = runtimeAsm.filter((opcode) => opcode.source == 0);

  const obfuscatedAsm = injectInstruction(sourceAsm, ratio);

  bytecodeJson[".data"]["0"][".code"] = [
    ...obfuscatedAsm,
    ...runtimeAsm.filter((opcode) => opcode.source == 1),
  ];
  await fs.writeFile(outputPath, JSON.stringify(bytecodeJson));
})();
