import json
import os
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()


class TestResultVerifier:
    def __init__(self):
        # Initialize Web3 connection (using Infura for Ethereum)
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("INFURA_URL")))
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")

        # Load contract ABI
        with open("src/blockchain/contracts/TestResultVerifier.json", "r") as f:
            contract_abi = json.load(f)

        self.contract = self.w3.eth.contract(
            address=self.contract_address, abi=contract_abi
        )

    def store_test_result(self, test_id: str, result: Dict[str, Any]) -> str:
        """
        Store test result on the blockchain and return transaction hash.

        Args:
            test_id: Unique identifier for the test
            result: Dictionary containing test result data

        Returns:
            str: Transaction hash
        """
        # Prepare transaction
        nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)

        # Create transaction
        transaction = self.contract.functions.storeTestResult(
            test_id, json.dumps(result), int(datetime.now().timestamp())
        ).build_transaction(
            {
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "from": self.w3.eth.default_account,
            }
        )

        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()

    def verify_test_result(self, test_id: str) -> Dict[str, Any]:
        """
        Retrieve and verify test result from blockchain.

        Args:
            test_id: Unique identifier for the test

        Returns:
            Dict[str, Any]: Verified test result data
        """
        result = self.contract.functions.getTestResult(test_id).call()
        return json.loads(result)

    def get_test_result_history(self, test_id: str) -> list:
        """
        Get history of all test results for a specific test.

        Args:
            test_id: Unique identifier for the test

        Returns:
            list: List of historical test results
        """
        events = self.contract.events.TestResultStored.get_logs(
            argument_filters={"testId": test_id}
        )
        return [json.loads(event["args"]["result"]) for event in events]
