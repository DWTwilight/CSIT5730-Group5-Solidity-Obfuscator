const Opcode = {
  LT: "LT",
  GT: "GT",
  SLT: "SLT",
  SGT: "SGT",
  EQ: "EQ",
  ISZERO: "ISZERO",
  JUMPI: "JUMPI",
  JUMP: "JUMP",
  PUSH: "PUSH",
  PUSH_TAG: "PUSH [tag]",
  DUP: "DUP",
  ADD: "ADD",
  SUB: "SUB",
  MUL: "MUL",
  DIV: "DIV",
  MOD: "MOD",
  TAG: "tag",
  JUMPDEST: "JUMPDEST",
  EXP: "EXP",
  SWAP: "SWAP",
  POP: "POP",
  ADDRESS: "ADDRESS",
};

function offsetDup(dup, offset) {
  const dupI = parseInt(dup.replace(/^\D+/g, ""));
  return `${Opcode.DUP}${dupI + offset}`;
}

function dup(index) {
  return `${Opcode.DUP}${index}`;
}

function swap(index) {
  return `${Opcode.SWAP}${index}`;
}

function createInstruction(opcode, value) {
  if (value) {
    return {
      begin: 855,
      end: 875,
      name: opcode,
      value: value,
      source: 0,
    };
  } else {
    return {
      begin: 855,
      end: 875,
      name: opcode,
      source: 0,
    };
  }
}

const C0_OPCODE = [
  [Opcode.PUSH, 5],
  [Opcode.DUP, 5],
  [Opcode.ADDRESS, 1],
];

const BI_OPCODE = [
  [Opcode.ADD, 5],
  [Opcode.SUB, 4],
  [Opcode.MUL, 4],
  [Opcode.DIV, 2],
  [Opcode.EXP, 1],
  [Opcode.MOD, 2],
];

const COMP_OPCODE = [
  [Opcode.LT, 3],
  [Opcode.GT, 3],
  [Opcode.EQ, 1],
];

const STRUCT_TYPE = {
  SEQ: "SEQ",
  IF: "IF",
  LOOP: "LOOP",
};

const STRUCTURE = [
  [STRUCT_TYPE.SEQ, 10],
  [STRUCT_TYPE.IF, 4],
  [STRUCT_TYPE.LOOP, 2],
];

function getRandomObjectByWeight(weightedObjects) {
  let totalWeight = 0;
  weightedObjects.forEach((element) => {
    totalWeight += element[1];
  });

  const randomNum = Math.random() * totalWeight;

  let cumulativeWeight = 0;
  for (const [object, weight] of weightedObjects) {
    cumulativeWeight += weight;
    if (randomNum < cumulativeWeight) {
      return object;
    }
  }
}

function getRandomNumber(min, max) {
  if (min != undefined && max != undefined && min === max) {
    return min;
  }
  return Math.floor(
    Math.random() * ((max || 0xffff) - (min || 0) + 1) + (min || 0)
  );
}

function getRandomHexNumber(min, max) {
  return getRandomNumber(min, max).toString(16);
}

function createJunkCode(complexity, tagIndex, depth, outerFlag) {
  if (complexity <= 0) {
    const op = getRandomObjectByWeight(C0_OPCODE);
    if (op == Opcode.PUSH) {
      return [createInstruction(Opcode.PUSH, getRandomHexNumber())];
    }
    if (op == Opcode.DUP) {
      return [createInstruction(dup(getRandomNumber(1, depth)))];
    }
    return [createInstruction(op)];
  }

  let code = [];
  let structure = getRandomObjectByWeight(STRUCTURE);
  while (complexity < 2 && structure == STRUCT_TYPE.LOOP) {
    structure = getRandomObjectByWeight(STRUCTURE);
  }
  if (structure == STRUCT_TYPE.SEQ) {
    code = code.concat(
      createJunkCode(getRandomNumber(0, complexity - 1), tagIndex, depth)
    );
    code = code.concat(
      createJunkCode(getRandomNumber(0, complexity - 1), tagIndex, depth + 1)
    );
    const op = getRandomObjectByWeight(BI_OPCODE);
    code.push(createInstruction(op));
  } else if (structure == STRUCT_TYPE.IF) {
    const tagI = tagIndex.value;
    tagIndex.value++;
    code.push(createInstruction(Opcode.PUSH, getRandomHexNumber()));
    code.push(createInstruction(dup(getRandomNumber(2, depth + 1))));
    code.push(createInstruction(getRandomObjectByWeight(COMP_OPCODE)));
    if (getRandomNumber(0, 1) == 0) {
      code.push(createInstruction(Opcode.ISZERO));
    }
    code.push(createInstruction(Opcode.PUSH_TAG, `${tagI}`));
    code.push(createInstruction(Opcode.JUMPI));

    // if
    code = code.concat(
      createJunkCode(getRandomNumber(0, complexity - 1), tagIndex, depth)
    );

    code.push(createInstruction(Opcode.TAG, `${tagI}`));
    code.push(createInstruction(Opcode.JUMPDEST));

    // else
    code = code.concat(
      createJunkCode(getRandomNumber(0, complexity - 1), tagIndex, depth)
    );
  } else if (structure == STRUCT_TYPE.LOOP) {
    const tagI1 = tagIndex.value++;
    const tagI2 = tagIndex.value++;

    code.push(createInstruction(Opcode.TAG, `${tagI1}`));
    code.push(createInstruction(Opcode.JUMPDEST));
    code.push(createInstruction(Opcode.PUSH, getRandomHexNumber()));
    code.push(createInstruction(dup(getRandomNumber(2, depth + 1))));
    code.push(createInstruction(getRandomObjectByWeight(COMP_OPCODE)));
    if (getRandomNumber(0, 1) == 0) {
      code.push(createInstruction(Opcode.ISZERO));
    }
    code.push(createInstruction(Opcode.PUSH_TAG, `${tagI2}`));
    code.push(createInstruction(Opcode.JUMPI));
    // Loop body
    code = code.concat(
      createJunkCode(getRandomNumber(1, complexity - 1), tagIndex, depth)
    );
    code.push(createInstruction(swap(getRandomNumber(1, depth))));
    code.push(createInstruction(Opcode.POP));
    code.push(createInstruction(Opcode.PUSH_TAG, `${tagI1}`));
    code.push(createInstruction(Opcode.JUMP));
    code.push(createInstruction(Opcode.TAG, `${tagI2}`));
    code.push(createInstruction(Opcode.JUMPDEST));
    code.push(createInstruction(dup(getRandomNumber(1, depth))));
  }

  if (outerFlag) {
    code.push(createInstruction(swap(1)));
    code.push(createInstruction(Opcode.POP));
  }

  return code;
}

module.exports = {
  Opcode,
  offsetDup,
  dup,
  swap,
  createInstruction,
  getRandomNumber,
  createJunkCode,
};
