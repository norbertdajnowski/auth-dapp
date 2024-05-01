import solcx as solcx
from web3 import Web3, HTTPProvider
import json
import os

solcx.install_solc('0.6.0')

class web3Connect:
    
    def __init__(self) -> None:
        self.web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        self.clientAddress = self.web3.eth.accounts[0]
          
    def deployContract(self):
        with open("./project/contracts/authorisationContract.sol", "r") as file:
            simple_storage_file = file.read()

        compiled_sol = solcx.compile_standard(
            {
                "language": "Solidity",
                "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                        }
                    }
                }
            },
            solc_version="0.6.0"
        )
        # Dump the compiled code to see the structure of the code
        with open("compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)

        bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["authorisationContract"]["evm"]["bytecode"]["object"]

        abi = compiled_sol["contracts"]["SimpleStorage.sol"]["authorisationContract"]["abi"]

        chain_id = 1337
        my_addr = "0x58AaB486F7f0d00cf493715331c21fdBf6A84578"
        private_key = "0x396683ff89e52910891b316c3662b83ae8d297ced201743ca68d8921756ee23b"

        SimpleStorage = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = self.web3.eth.get_transaction_count(my_addr)

        transaction = SimpleStorage.constructor().build_transaction(
            {
                "chainId": chain_id,
                "gasPrice": self.web3.eth.gas_price,
                "from": my_addr,
                "nonce": nonce
            }
        )

        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=private_key)

        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash) 
        contract_addr = tx_receipt.contractAddress
        
        contract = self.web3.eth.contract(contract_addr)

        print(f"Contract is deployed to {contract}")

        return contract, contract_addr, abi