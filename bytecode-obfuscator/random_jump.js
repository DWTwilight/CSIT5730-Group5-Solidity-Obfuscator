const fs = require("fs").promises;
const { Opcode, createInstruction, getRandomNumber } = require("./evm_opcode");

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const count = parseInt(process.argv[4]) || 0;

function randomJump(source, tagIndex) {
  let cutA = getRandomNumber(1, source.length - 2);
  while (source[cutA - 1].name == Opcode.TAG) {
    cutA = getRandomNumber(1, source.length - 2);
  }
  let cutB = cutA;
  while (Math.abs(cutA - cutB) < 3 || source[cutB - 1].name == Opcode.TAG) {
    cutB = getRandomNumber(1, source.length - 2);
  }

  if (cutA > cutB) {
    const t = cutA;
    cutA = cutB;
    cutB = t;
  }

  const tag1 = tagIndex.value++;
  const tag2 = tagIndex.value++;
  const tag3 = tagIndex.value++;

  return [
    ...source.slice(0, cutA),
    createInstruction(Opcode.PUSH_TAG, `${tag1}`),
    createInstruction(Opcode.JUMP),
    createInstruction(Opcode.TAG, `${tag2}`),
    createInstruction(Opcode.JUMPDEST),
    ...source.slice(cutB, source.length),
    createInstruction(Opcode.PUSH_TAG, `${tag3}`),
    createInstruction(Opcode.JUMP),
    createInstruction(Opcode.TAG, `${tag1}`),
    createInstruction(Opcode.JUMPDEST),
    ...source.slice(cutA, cutB),
    createInstruction(Opcode.PUSH_TAG, `${tag2}`),
    createInstruction(Opcode.JUMP),
    createInstruction(Opcode.TAG, `${tag3}`),
    createInstruction(Opcode.JUMPDEST),
    source[source.length - 1],
  ];
}

(async () => {
  let bytecodeJson = JSON.parse(await fs.readFile(inputPath, "utf8"));

  const runtimeAsm = bytecodeJson[".data"]["0"][".code"];
  // get the target code section
  let sourceAsm = [...runtimeAsm];

  const tagIndex = {
    value:
      Math.max(
        ...runtimeAsm
          .filter((opcode) => opcode.name == "tag")
          .map((opcode) => Number(opcode.value))
      ) + 1,
  };

  for (let i = 0; i < count; i++) {
    sourceAsm = randomJump(sourceAsm, tagIndex);
  }

  bytecodeJson[".data"]["0"][".code"] = [...sourceAsm];
  await fs.writeFile(outputPath, JSON.stringify(bytecodeJson));
})();
