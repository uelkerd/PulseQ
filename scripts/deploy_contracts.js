const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  // Deploy TestExecutionCoordinator
  const TestExecutionCoordinator = await ethers.getContractFactory(
    "TestExecutionCoordinator"
  );
  const coordinator = await TestExecutionCoordinator.deploy();
  await coordinator.deployed();
  console.log("TestExecutionCoordinator deployed to:", coordinator.address);

  // Save contract addresses to a JSON file
  const addresses = {
    testExecutionCoordinator: coordinator.address,
  };

  const addressesPath = path.join(__dirname, "..", "deployed_addresses.json");
  fs.writeFileSync(addressesPath, JSON.stringify(addresses, null, 2));
  console.log("Contract addresses saved to:", addressesPath);

  // Verify contracts on Etherscan
  console.log("Waiting for 5 block confirmations...");
  await coordinator.deployTransaction.wait(5);

  console.log("Verifying contracts on Etherscan...");
  try {
    await hre.run("verify:verify", {
      address: coordinator.address,
      constructorArguments: [],
    });
    console.log("TestExecutionCoordinator verified on Etherscan");
  } catch (error) {
    console.error("Error verifying contracts:", error);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
