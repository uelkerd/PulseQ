from web3 import Web3
from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import hashlib

load_dotenv()

class TestExecutionCoordinator:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('INFURA_URL')))
        self.contract_address = os.getenv('COORDINATOR_CONTRACT_ADDRESS')
        self.private_key = os.getenv('PRIVATE_KEY')
        
        with open('src/blockchain/contracts/TestExecutionCoordinator.json', 'r') as f:
            contract_abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=contract_abi
        )
        self.w3.eth.default_account = self.w3.eth.account.from_key(self.private_key).address

    def create_test_job(self, test_id: str, test_script: str, reward: int) -> str:
        """
        Create a new test job on the blockchain.
        
        Args:
            test_id: Unique identifier for the test
            test_script: The test script to be executed
            reward: Amount of ETH to reward the executor (in wei)
            
        Returns:
            str: Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.createTestJob(
            test_id,
            test_script,
            reward
        ).build_transaction({
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'value': reward,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def accept_test_job(self, test_id: str) -> str:
        """
        Accept a test job for execution.
        
        Args:
            test_id: Unique identifier for the test
            
        Returns:
            str: Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.acceptTestJob(
            test_id
        ).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def complete_test_job(self, test_id: str, success: bool, result_data: Dict[str, Any]) -> str:
        """
        Mark a test job as completed with result verification.
        
        Args:
            test_id: Unique identifier for the test
            success: Whether the test execution was successful
            result_data: Dictionary containing test result data
            
        Returns:
            str: Transaction hash
        """
        # Generate result hash
        result_json = json.dumps(result_data, sort_keys=True)
        result_hash = hashlib.sha256(result_json.encode()).hexdigest()
        
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.completeTestJob(
            test_id,
            success,
            result_hash
        ).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def create_dispute(self, test_id: str, reason: str) -> str:
        """
        Create a dispute for a completed test job.
        
        Args:
            test_id: Unique identifier for the test
            reason: Reason for the dispute
            
        Returns:
            str: Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.createDispute(
            test_id,
            reason
        ).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def add_verifier(self, test_id: str) -> str:
        """
        Add a verifier to a disputed test job.
        
        Args:
            test_id: Unique identifier for the test
            
        Returns:
            str: Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.addVerifier(
            test_id
        ).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def vote_on_dispute(self, test_id: str, uphold_dispute: bool) -> str:
        """
        Vote on a disputed test job.
        
        Args:
            test_id: Unique identifier for the test
            uphold_dispute: Whether to uphold the dispute
            
        Returns:
            str: Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
        
        transaction = self.contract.functions.voteOnDispute(
            test_id,
            uphold_dispute
        ).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'from': self.w3.eth.default_account
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()

    def get_test_job(self, test_id: str) -> Dict[str, Any]:
        """
        Get details of a test job.
        
        Args:
            test_id: Unique identifier for the test
            
        Returns:
            Dict[str, Any]: Test job details
        """
        result = self.contract.functions.getTestJob(test_id).call()
        return {
            'test_script': result[0],
            'reward': result[1],
            'requester': result[2],
            'is_completed': result[3],
            'executor': result[4],
            'completion_time': result[5],
            'result_hash': result[6],
            'is_disputed': result[7],
            'dispute_end_time': result[8]
        }

    def get_dispute(self, test_id: str) -> Dict[str, Any]:
        """
        Get details of a dispute.
        
        Args:
            test_id: Unique identifier for the test
            
        Returns:
            Dict[str, Any]: Dispute details
        """
        result = self.contract.functions.getDispute(test_id).call()
        return {
            'disputer': result[0],
            'reason': result[1],
            'timestamp': result[2],
            'is_resolved': result[3]
        }

    def get_executor_reputation(self, executor_address: str) -> int:
        """
        Get the reputation score of an executor.
        
        Args:
            executor_address: Ethereum address of the executor
            
        Returns:
            int: Reputation score
        """
        return self.contract.functions.getExecutorReputation(
            self.w3.to_checksum_address(executor_address)
        ).call()

    def get_verifier_reputation(self, verifier_address: str) -> int:
        """
        Get the reputation score of a verifier.
        
        Args:
            verifier_address: Ethereum address of the verifier
            
        Returns:
            int: Reputation score
        """
        return self.contract.functions.getVerifierReputation(
            self.w3.to_checksum_address(verifier_address)
        ).call() 