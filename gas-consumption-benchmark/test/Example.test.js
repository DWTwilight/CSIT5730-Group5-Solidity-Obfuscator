const {
  loadFixture,
} = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Example Test", function () {
  async function deployContract() {
    const Example = await ethers.getContractFactory("Example");
    const target = await Example.deploy(10);
    const users = await ethers.getSigners();

    return { target, users };
  }

  it("test1", async function () {
    const { target, users } = await loadFixture(deployContract);

    await target.set_value(0, 1);
    await target.get_value(0);
    // await target.replace_value([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 0);
    // await target.add_value([1], 2);
    await target.addCandidate("test");
    await target.authorizeVoter(users[1].address);
    // await target.connect(users[1]).vote("test");
    await target.deactivateContract();
    await target.withdrawFunds();
  });
});
