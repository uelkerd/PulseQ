const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  // Load contract addresses
  const addressesPath = path.join(__dirname, "..", "deployed_addresses.json");
  const addresses = JSON.parse(fs.readFileSync(addressesPath, "utf8"));

  // Get signers
  const [owner, requester, executor, verifier1, verifier2] =
    await ethers.getSigners();

  // Connect to contracts
  const TestExecutionCoordinator = await ethers.getContractFactory(
    "TestExecutionCoordinator"
  );
  const coordinator = await TestExecutionCoordinator.attach(
    addresses.testExecutionCoordinator
  );

  // Example: Create a test job
  console.log("Creating test job...");
  const testId = "test123";
  const testUrl = "https://example.com/test";
  const testPrice = ethers.utils.parseEther("0.1");

  const createTx = await coordinator
    .connect(requester)
    .createTestJob(testId, testUrl, { value: testPrice });
  await createTx.wait();
  console.log("Test job created:", testId);

  // Example: Accept test job
  console.log("Accepting test job...");
  const acceptTx = await coordinator.connect(executor).acceptTestJob(testId);
  await acceptTx.wait();
  console.log("Test job accepted");

  // Example: Complete test job
  console.log("Completing test job...");
  const resultUrl = "https://example.com/results";
  const completeTx = await coordinator
    .connect(executor)
    .completeTestJob(testId, resultUrl);
  await completeTx.wait();
  console.log("Test job completed");

  // Example: Add verifiers
  console.log("Adding verifiers...");
  const addVerifier1Tx = await coordinator
    .connect(owner)
    .addVerifier(verifier1.address);
  await addVerifier1Tx.wait();
  const addVerifier2Tx = await coordinator
    .connect(owner)
    .addVerifier(verifier2.address);
  await addVerifier2Tx.wait();
  console.log("Verifiers added");

  // Example: Create dispute
  console.log("Creating dispute...");
  const disputeTx = await coordinator.connect(requester).createDispute(testId);
  await disputeTx.wait();
  console.log("Dispute created");

  // Example: Vote on dispute
  console.log("Voting on dispute...");
  const vote1Tx = await coordinator
    .connect(verifier1)
    .voteOnDispute(testId, true);
  await vote1Tx.wait();
  const vote2Tx = await coordinator
    .connect(verifier2)
    .voteOnDispute(testId, true);
  await vote2Tx.wait();
  console.log("Votes cast");

  // Check final state
  const job = await coordinator.testJobs(testId);
  console.log("Final job state:", {
    status: job.status,
    requester: job.requester,
    executor: job.executor,
    price: ethers.utils.formatEther(job.price),
    resultUrl: job.resultUrl,
    disputeCount: job.disputeCount.toString(),
    disputeVotes: job.disputeVotes.toString(),
  });
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
