const {
  loadFixture,
} = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Example2 Test", function () {
  async function deployContract() {
    const ControlFlowExample = await ethers.getContractFactory(
      "ControlFlowExample"
    );
    const target = await ControlFlowExample.deploy();
    const users = await ethers.getSigners();

    return { target, users };
  }

  it("test1", async function () {
    const { target, users } = await loadFixture(deployContract);

    await target.loop();
    expect(await target.res()).to.equal(14);
  });
});
