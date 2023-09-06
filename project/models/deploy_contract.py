import solcx as solcx
from web3 import Web3, HTTPProvider
import json
import os


with open("./project/contracts/authorisationContract.sol", "r") as file:
    simple_storage_file = file.read()

solcx.install_solc('0.6.0')
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

bytecode = compiled_sol["contracts"]["authorisationContract.sol"]["authorisationContract"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["authorisationContract.sol"]["authorisationContract"]["abi"]

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_addr = "0x2BF099F6429780635B173Bbd432dc555e0E45707"
private_key = "0xd2c99a4ec5bb02cef0d0e3092e49e228ba1f67c16893fcc0a8e3a972ed3e1197"

SimpleStorage = web3.eth.contract(abi=abi, bytecode=bytecode)
nonce = web3.eth.get_transaction_count(my_addr)

transaction = SimpleStorage.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": web3.eth.gas_price,
        "from": my_addr,
        "nonce": nonce
    }
)

signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash) 
contract_addr = tx_receipt.contractAddress
print(f"Contract is deployed to {contract_addr}")