// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TestResultVerifier {
    struct TestResult {
        string result;
        uint256 timestamp;
        address storedBy;
    }
    
    mapping(string => TestResult) private testResults;
    
    event TestResultStored(string indexed testId, string result, uint256 timestamp, address storedBy);
    
    function storeTestResult(string memory testId, string memory result, uint256 timestamp) public {
        require(bytes(testId).length > 0, "Test ID cannot be empty");
        require(bytes(result).length > 0, "Result cannot be empty");
        
        testResults[testId] = TestResult({
            result: result,
            timestamp: timestamp,
            storedBy: msg.sender
        });
        
        emit TestResultStored(testId, result, timestamp, msg.sender);
    }
    
    function getTestResult(string memory testId) public view returns (string memory) {
        require(bytes(testId).length > 0, "Test ID cannot be empty");
        require(bytes(testResults[testId].result).length > 0, "Test result not found");
        
        return testResults[testId].result;
    }
    
    function getTestResultDetails(string memory testId) public view returns (
        string memory result,
        uint256 timestamp,
        address storedBy
    ) {
        require(bytes(testId).length > 0, "Test ID cannot be empty");
        require(bytes(testResults[testId].result).length > 0, "Test result not found");
        
        TestResult memory testResult = testResults[testId];
        return (
            testResult.result,
            testResult.timestamp,
            testResult.storedBy
        );
    }
} 