from web3 import Web3

w3 = Web3()
account = w3.eth.account.create()

print("--- New Ethereum Account Generated ---")
print(f"Address: {account.address}")
print(f"Private Key: {account.key.hex()}")
print("--------------------------------------")
print("IMPORTANT: Save these credentials safely. Add the Private Key to your .env file.")
print("You will need to fund this address with Sepolia ETH to use it.")
