const fs = require("fs").promises;
const { Opcode, createInstruction, dup, offsetDup } = require("./evm_opcode");

const ARITHMETIC_COMP_OPCODE = [Opcode.LT, Opcode.GT];

const ARITHMETIC_COMP = {
  LT: "LT",
  LTE: "LTE",
  GT: "GT",
  GTE: "GTE",
};

function getSwapedArithmeticComp(op, swap) {
  if (swap) {
    switch (op) {
      case ARITHMETIC_COMP.LT:
        return ARITHMETIC_COMP.GT;
      case ARITHMETIC_COMP.GT:
        return ARITHMETIC_COMP.LT;
      case ARITHMETIC_COMP.LTE:
        return ARITHMETIC_COMP.GTE;
      case ARITHMETIC_COMP.GTE:
        return ARITHMETIC_COMP.LTE;
    }
  }
  return op;
}

function getArithmeticComp(opcode, reverse, swap) {
  if (reverse) {
    switch (opcode) {
      case Opcode.LT:
        return getSwapedArithmeticComp(ARITHMETIC_COMP.GTE, swap);
      case Opcode.GT:
        return getSwapedArithmeticComp(ARITHMETIC_COMP.LTE, swap);
    }
  } else {
    switch (opcode) {
      case Opcode.LT:
        return getSwapedArithmeticComp(ARITHMETIC_COMP.LT, swap);
      case Opcode.GT:
        return getSwapedArithmeticComp(ARITHMETIC_COMP.GT, swap);
    }
  }
}

function createOpaquePredicate(a, b, op, tagIndex) {
  const tagI = tagIndex.value;
  const b1 = parseInt(b.value, 16);
  const b2 =
    op == ARITHMETIC_COMP.GT || op == ARITHMETIC_COMP.GTE
      ? Math.floor(Math.random() * (b1 + 1))
      : Math.ceil(Math.random() * 100) + b1;
  console.log(b1, b2);

  let code = [];
  code.push(createInstruction(Opcode.PUSH, (b1 * b2).toString(16)));
  code.push(createInstruction(a.name));
  code.push(createInstruction(Opcode.MUL));
  code.push(createInstruction(a.name));
  code.push(createInstruction(dup(1)));
  code.push(createInstruction(Opcode.MUL));
  code.push(createInstruction(Opcode.PUSH, (b1 + b2).toString(16)));
  code.push(createInstruction(Opcode.ADD));
  if (op == ARITHMETIC_COMP.GT || op == ARITHMETIC_COMP.LT) {
    code.push(createInstruction(Opcode.GT));
    code.push(createInstruction(Opcode.ISZERO));
  } else {
    code.push(createInstruction(Opcode.LT));
  }
  code.push(createInstruction(Opcode.PUSH_TAG, `${tagI}`));
  tagIndex.value++;
  code.push(createInstruction(Opcode.JUMPI));

  // insert junk code:

  // jump tag
  code.push(createInstruction(Opcode.TAG, `${tagI}`));
  code.push(createInstruction(Opcode.JUMPDEST));

  console.log("--------start opaque predicate ---------");
  console.log(code);
  console.log("--------end opaque predicate ---------");
}

function injectOpaquePredicates(asm, startIndex, tagIndex) {
  while (startIndex <= asm.length - 6) {
    let jump = 1;
    if (ARITHMETIC_COMP_OPCODE.includes(asm[startIndex].name)) {
      // constant
      let b = asm[startIndex - 2];
      // variable
      let a = asm[startIndex - 1];
      let swap = false;
      let reverse = false;

      if (a.name == Opcode.PUSH && b.name.startsWith(Opcode.DUP)) {
        let t = a;
        a = b;
        b = t;
        swap = true;
        // a: DUP%d -> DUP%d+1
        a.name = offsetDup(a.name, 1);
      } else if (!a.name.startsWith(Opcode.DUP) || b.name != Opcode.PUSH) {
        startIndex += 1;
        continue;
      }

      if (
        asm[startIndex + 1].name == Opcode.ISZERO &&
        asm[startIndex + 2].name == Opcode.PUSH_TAG &&
        asm[startIndex + 3].name == Opcode.JUMPI
      ) {
        jump += 3;
      } else if (
        asm[startIndex + 1].name == Opcode.PUSH_TAG &&
        asm[startIndex + 2].name == Opcode.JUMPI
      ) {
        // reverse arithmetic comp
        reverse = true;
        jump += 2;
      } else {
        startIndex += 1;
        continue;
      }

      // create and insert opaque predicate
      console.log(
        a.name,
        parseInt(b.value, 16),
        getArithmeticComp(asm[startIndex].name, reverse, swap),
        reverse,
        swap
      );
      createOpaquePredicate(
        a,
        b,
        getArithmeticComp(asm[startIndex].name, reverse, swap),
        tagIndex
      );
    }
    startIndex += jump;
  }
}

const filePath = process.argv[2];

(async () => {
  let bytecodeJson = JSON.parse(await fs.readFile(filePath, "utf8"));

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

  injectOpaquePredicates(sourceAsm, 2, { value: tagIndex });
})();