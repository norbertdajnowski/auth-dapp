import solcx as solcx
from web3 import Web3, HTTPProvider
import json
import os


with open("./project/contracts/SimpleStorage.sol", "r") as file:
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

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_addr = "0xb6524F0647C859131C63aBE2E466E8522a031F65"
private_key = "0x3419afbc423174741452bdefc4b269044f5aa0654eea680edefe3051721ea7f7"

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