const {
  loadFixture,
} = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BytecodeObfuscation Test", function () {
  async function deployContract() {
    const BytecodeObfuscation = await ethers.getContractFactory(
      "BytecodeObfuscation"
    );
    const target = await BytecodeObfuscation.deploy();
    const users = await ethers.getSigners();

    return { target, users };
  }

  it("test1", async function () {
    const { target, users } = await loadFixture(deployContract);

    await target.loop();
    expect(await target.res()).to.equal(50);
    await target.cond();
    expect(await target.res()).to.equal(5);
    await target.arithmetic();
    expect(await target.res()).to.equal(4);
  });
});
