const fs = require("fs").promises;
const {
  Opcode,
  createInstruction,
  dup,
  offsetDup,
  createJunkCode,
  getRandomNumber,
} = require("./evm_opcode");

const ARITHMETIC_COMP_OPCODE = [Opcode.LT, Opcode.GT];

const ARITHMETIC_COMP = {
  LT: "LT",
  LTE: "LTE",
  GT: "GT",
  GTE: "GTE",
};

function getArithmeticComp(opcode, reverse) {
  if (reverse) {
    switch (opcode) {
      case Opcode.LT:
        return ARITHMETIC_COMP.GTE;
      case Opcode.GT:
        return ARITHMETIC_COMP.LTE;
    }
  } else {
    switch (opcode) {
      case Opcode.LT:
        return ARITHMETIC_COMP.LT;
      case Opcode.GT:
        return ARITHMETIC_COMP.GT;
    }
  }
}

function createOpaquePredicate(a, b, op, tagIndex) {
  const tagI = tagIndex.value++;
  let b1 = parseInt(b.value, 16);
  let b2 =
    op == (ARITHMETIC_COMP.GT || op == ARITHMETIC_COMP.GTE)
      ? Math.floor(Math.random() * b1)
      : Math.ceil(Math.random() * 100) + b1 + 1;
  b1 =
    op == (ARITHMETIC_COMP.GT || op == ARITHMETIC_COMP.GTE)
      ? Math.floor(Math.random() * b1)
      : Math.ceil(Math.random() * 100) + b1 + 1;

  let code = [];
  code.push(createInstruction(Opcode.PUSH, (b1 + b2).toString(16)));
  code.push(createInstruction(a.name));
  code.push(createInstruction(Opcode.MUL));
  code.push(createInstruction(a.name));
  code.push(createInstruction(dup(1)));
  code.push(createInstruction(Opcode.MUL));
  code.push(createInstruction(Opcode.PUSH, (b1 * b2).toString(16)));
  code.push(createInstruction(Opcode.ADD));
  console.log(op);
  code.push(createInstruction(Opcode.GT));
  // code.push(createInstruction(Opcode.POP));
  // code.push(createInstruction(Opcode.PUSH, "1"));
  code.push(createInstruction(Opcode.PUSH_TAG, `${tagI}`));
  code.push(createInstruction(Opcode.JUMPI));

  // insert junk code:
  code = code.concat(createJunkCode(20, tagIndex, 1, true));
  // jump tag
  code.push(createInstruction(Opcode.TAG, `${tagI}`));
  code.push(createInstruction(Opcode.JUMPDEST));

  return code;
}

function injectOpaquePredicates(asm, startIndex, tagIndex, ratio) {
  let res = [...asm];
  while (startIndex <= res.length - 6) {
    let jump = 1;
    if (
      ARITHMETIC_COMP_OPCODE.includes(res[startIndex].name) &&
      Math.random() < ratio
    ) {
      // constant
      let b = res[startIndex - 2];
      // variable
      let a = res[startIndex - 1];
      let reverse = false;

      if (!a.name.startsWith(Opcode.DUP) || b.name != Opcode.PUSH) {
        startIndex += 1;
        continue;
      }

      if (
        res[startIndex + 1].name == Opcode.ISZERO &&
        res[startIndex + 2].name == Opcode.PUSH_TAG &&
        res[startIndex + 3].name == Opcode.JUMPI
      ) {
        jump += 3;
      } else if (
        res[startIndex + 1].name == Opcode.PUSH_TAG &&
        res[startIndex + 2].name == Opcode.JUMPI
      ) {
        // reverse arithmetic comp
        reverse = true;
        jump += 2;
      } else {
        startIndex += 1;
        continue;
      }

      // create and insert opaque predicate
      const opaquePredicateCode = createOpaquePredicate(
        a,
        b,
        getArithmeticComp(res[startIndex].name, reverse),
        tagIndex
      );
      res = [
        ...res.slice(0, startIndex + jump),
        ...opaquePredicateCode,
        ...res.slice(startIndex + jump),
      ];
      jump += opaquePredicateCode.length;
    }
    startIndex += jump;
  }
  return res;
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const ratio = parseFloat(process.argv[4]) || 0.5;

(async () => {
  let bytecodeJson = JSON.parse(await fs.readFile(inputPath, "utf8"));

  const runtimeAsm = bytecodeJson[".data"]["0"][".code"];
  // get the target code section
  let sourceAsm = runtimeAsm.filter((opcode) => opcode.source == 0);
  // get the next tag index
  const tagIndex =
    Math.max(
      ...runtimeAsm
        .filter((opcode) => opcode.name == "tag")
        .map((opcode) => Number(opcode.value))
    ) + 1;

  const obfuscatedAsm = injectOpaquePredicates(
    sourceAsm,
    2,
    {
      value: tagIndex,
    },
    ratio
  );
  bytecodeJson[".data"]["0"][".code"] = [
    ...obfuscatedAsm,
    ...runtimeAsm.filter((opcode) => opcode.source == 1),
  ];
  await fs.writeFile(outputPath, JSON.stringify(bytecodeJson));
})();
