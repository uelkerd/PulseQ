// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TestExecutionCoordinator is ReentrancyGuard, Ownable {
    struct TestJob {
        string testId;
        string testScript;
        uint256 reward;
        address requester;
        bool isCompleted;
        address executor;
        uint256 completionTime;
        string resultHash;
        bool isDisputed;
        uint256 disputeEndTime;
        address[] verifiers;
        mapping(address => bool) verifierVotes;
    }
    
    struct Dispute {
        string testId;
        address disputer;
        string reason;
        uint256 timestamp;
        bool isResolved;
    }
    
    mapping(string => TestJob) public testJobs;
    mapping(string => Dispute) public disputes;
    mapping(address => uint256) public executorReputation;
    mapping(address => uint256) public verifierReputation;
    mapping(address => uint256) public lastActionTime;
    mapping(address => uint256) public actionCount;
    
    uint256 public constant DISPUTE_PERIOD = 7 days;
    uint256 public constant MIN_VERIFIERS = 3;
    uint256 public constant VERIFIER_REWARD = 0.0001 ether;
    uint256 public constant ACTION_COOLDOWN = 1 minutes;
    uint256 public constant MAX_ACTIONS_PER_PERIOD = 10;
    
    bool private locked;
    
    event TestJobCreated(string indexed testId, address requester, uint256 reward);
    event TestJobAccepted(string indexed testId, address executor);
    event TestJobCompleted(string indexed testId, address executor, bool success, string resultHash);
    event ReputationUpdated(address executor, uint256 newReputation);
    event DisputeCreated(string indexed testId, address disputer, string reason);
    event DisputeResolved(string indexed testId, bool upheld);
    event VerifierAdded(string indexed testId, address verifier);
    event VerifierVoted(string indexed testId, address verifier, bool vote);
    event RateLimitExceeded(address user);
    
    modifier rateLimited() {
        require(block.timestamp >= lastActionTime[msg.sender] + ACTION_COOLDOWN, "Action too frequent");
        require(actionCount[msg.sender] < MAX_ACTIONS_PER_PERIOD, "Too many actions");
        _;
        lastActionTime[msg.sender] = block.timestamp;
        actionCount[msg.sender]++;
    }
    
    modifier noReentrancy() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    function createTestJob(
        string memory testId,
        string memory testScript,
        uint256 reward
    ) public payable rateLimited noReentrancy {
        require(msg.value >= reward, "Insufficient payment");
        require(bytes(testId).length > 0, "Test ID cannot be empty");
        require(testJobs[testId].requester == address(0), "Test ID already exists");
        
        testJobs[testId] = TestJob({
            testId: testId,
            testScript: testScript,
            reward: reward,
            requester: msg.sender,
            isCompleted: false,
            executor: address(0),
            completionTime: 0,
            resultHash: "",
            isDisputed: false,
            disputeEndTime: 0
        });
        
        emit TestJobCreated(testId, msg.sender, reward);
    }
    
    function acceptTestJob(string memory testId) public rateLimited {
        require(!testJobs[testId].isCompleted, "Job already completed");
        require(testJobs[testId].executor == address(0), "Job already accepted");
        require(msg.sender != testJobs[testId].requester, "Requester cannot be executor");
        
        testJobs[testId].executor = msg.sender;
        emit TestJobAccepted(testId, msg.sender);
    }
    
    function completeTestJob(
        string memory testId,
        bool success,
        string memory resultHash
    ) public rateLimited noReentrancy {
        require(testJobs[testId].executor == msg.sender, "Not the executor");
        require(!testJobs[testId].isCompleted, "Job already completed");
        require(bytes(resultHash).length > 0, "Result hash required");
        
        TestJob storage job = testJobs[testId];
        job.isCompleted = true;
        job.completionTime = block.timestamp;
        job.resultHash = resultHash;
        
        if (success) {
            (bool sent, ) = payable(msg.sender).call{value: job.reward}("");
            require(sent, "Failed to send reward");
            executorReputation[msg.sender] += 1;
            emit ReputationUpdated(msg.sender, executorReputation[msg.sender]);
        }
        
        emit TestJobCompleted(testId, msg.sender, success, resultHash);
    }
    
    function createDispute(
        string memory testId,
        string memory reason
    ) public rateLimited {
        require(testJobs[testId].isCompleted, "Job not completed");
        require(!testJobs[testId].isDisputed, "Dispute already exists");
        require(msg.sender != testJobs[testId].executor, "Executor cannot dispute");
        require(bytes(reason).length > 0, "Reason required");
        
        testJobs[testId].isDisputed = true;
        testJobs[testId].disputeEndTime = block.timestamp + DISPUTE_PERIOD;
        
        disputes[testId] = Dispute({
            testId: testId,
            disputer: msg.sender,
            reason: reason,
            timestamp: block.timestamp,
            isResolved: false
        });
        
        emit DisputeCreated(testId, msg.sender, reason);
    }
    
    function addVerifier(string memory testId) public rateLimited {
        require(testJobs[testId].isDisputed, "No active dispute");
        require(block.timestamp < testJobs[testId].disputeEndTime, "Dispute period ended");
        require(verifierReputation[msg.sender] > 0, "Not a verified verifier");
        require(msg.sender != testJobs[testId].executor, "Executor cannot be verifier");
        require(msg.sender != testJobs[testId].requester, "Requester cannot be verifier");
        
        TestJob storage job = testJobs[testId];
        require(job.verifiers.length < MIN_VERIFIERS, "Enough verifiers");
        
        // Check if already a verifier
        for (uint256 i = 0; i < job.verifiers.length; i++) {
            require(job.verifiers[i] != msg.sender, "Already a verifier");
        }
        
        job.verifiers.push(msg.sender);
        emit VerifierAdded(testId, msg.sender);
    }
    
    function voteOnDispute(
        string memory testId,
        bool upholdDispute
    ) public rateLimited noReentrancy {
        require(testJobs[testId].isDisputed, "No active dispute");
        require(block.timestamp < testJobs[testId].disputeEndTime, "Dispute period ended");
        
        TestJob storage job = testJobs[testId];
        require(job.verifierVotes[msg.sender] == false, "Already voted");
        
        // Verify sender is a verifier
        bool isVerifier = false;
        for (uint256 i = 0; i < job.verifiers.length; i++) {
            if (job.verifiers[i] == msg.sender) {
                isVerifier = true;
                break;
            }
        }
        require(isVerifier, "Not a verifier");
        
        job.verifierVotes[msg.sender] = true;
        emit VerifierVoted(testId, msg.sender, upholdDispute);
        
        // Check if we have enough votes
        if (job.verifiers.length >= MIN_VERIFIERS) {
            uint256 upholdCount = 0;
            for (uint256 i = 0; i < job.verifiers.length; i++) {
                if (job.verifierVotes[job.verifiers[i]]) {
                    upholdCount++;
                }
            }
            
            if (upholdCount > job.verifiers.length / 2) {
                // Dispute upheld
                (bool sent, ) = payable(job.requester).call{value: job.reward}("");
                require(sent, "Failed to send reward");
                executorReputation[job.executor] = executorReputation[job.executor] > 0 ? 
                    executorReputation[job.executor] - 1 : 0;
            }
            
            disputes[testId].isResolved = true;
            emit DisputeResolved(testId, upholdCount > job.verifiers.length / 2);
        }
    }
    
    function resetActionCount(address user) public onlyOwner {
        actionCount[user] = 0;
    }
    
    function setVerifierReputation(address verifier, uint256 reputation) public onlyOwner {
        verifierReputation[verifier] = reputation;
    }
    
    function getExecutorReputation(address executor) public view returns (uint256) {
        return executorReputation[executor];
    }
    
    function getVerifierReputation(address verifier) public view returns (uint256) {
        return verifierReputation[verifier];
    }
    
    function getTestJob(string memory testId) public view returns (
        string memory testScript,
        uint256 reward,
        address requester,
        bool isCompleted,
        address executor,
        uint256 completionTime,
        string memory resultHash,
        bool isDisputed,
        uint256 disputeEndTime
    ) {
        TestJob memory job = testJobs[testId];
        return (
            job.testScript,
            job.reward,
            job.requester,
            job.isCompleted,
            job.executor,
            job.completionTime,
            job.resultHash,
            job.isDisputed,
            job.disputeEndTime
        );
    }
    
    function getDispute(string memory testId) public view returns (
        address disputer,
        string memory reason,
        uint256 timestamp,
        bool isResolved
    ) {
        Dispute memory dispute = disputes[testId];
        return (
            dispute.disputer,
            dispute.reason,
            dispute.timestamp,
            dispute.isResolved
        );
    }
} 