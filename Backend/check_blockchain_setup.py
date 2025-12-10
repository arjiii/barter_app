import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Load env vars
load_dotenv()

print("--- Blockchain Configuration Check ---")

# 1. Check Env Vars
rpc_url = os.getenv("SEPOLIA_RPC_URL") or os.getenv("BLOCKCHAIN_RPC_URL")
contract_address = os.getenv("CONTRACT_ADDRESS") or os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS")
private_key = os.getenv("backend_WALLET_PRIVATE_KEY") or os.getenv("BLOCKCHAIN_PRIVATE_KEY")

print(f"RPC URL Found: {'YES' if rpc_url else 'NO'} ({rpc_url[:15]}...)" if rpc_url else "RPC URL Found: NO")
print(f"Contract Address Found: {'YES' if contract_address else 'NO'} ({contract_address})")
print(f"Private Key Found: {'YES' if private_key else 'NO'}")

if not all([rpc_url, contract_address, private_key]):
    print("\n[ERROR] Missing configuration. Please check your .env file.")
    sys.exit(1)

# 2. Check Connection
print("\n--- Connecting to Network ---")
try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if w3.is_connected():
        print("[SUCCESS] Connected to Blockchain!")
        print(f"Chain ID: {w3.eth.chain_id}")
        print(f"Latest Block: {w3.eth.block_number}")
    else:
        print("[ERROR] Could not connect to RPC URL.")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)

# 3. Check Wallet
print("\n--- Checking Wallet ---")
try:
    account = w3.eth.account.from_key(private_key)
    print(f"Wallet Address: {account.address}")
    
    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    print(f"Balance: {balance_eth} ETH")
    
    if balance_eth == 0:
        print("[WARNING] Wallet has 0 ETH. You cannot send transactions!")
    else:
        print("[SUCCESS] Wallet is funded.")
        
    nonce = w3.eth.get_transaction_count(account.address)
    print(f"Current Nonce: {nonce}")
    
except Exception as e:
    print(f"[ERROR] Invalid Private Key or Wallet Error: {e}")
    sys.exit(1)

# 4. Check Contract
print("\n--- Checking Contract ---")
if w3.eth.get_code(contract_address) == b'\x00' or w3.eth.get_code(contract_address) == b'0x': # Some nodes return different empty vals
    # Double check emptiness
    code = w3.eth.get_code(contract_address)
    if len(code) <= 2: # '0x'
        print(f"[ERROR] No contract code found at {contract_address}. Are you on the right network?")
    else:
        print("[SUCCESS] Contract code found.")
else:
    print("[SUCCESS] Contract code found.")

print("\n---------------------------")
print("Blockchain setup appears to be configured correctly!")
