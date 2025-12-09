import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Configuration
RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

# Minimal ABI for the write function - You might need to expand this based on your actual contract
# Assuming a function like: completeTrade(string tradeId, string buyerEmail, string sellerEmail, string item, string price)
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "tradeId", "type": "string"},
            {"internalType": "string", "name": "buyerEmail", "type": "string"},
            {"internalType": "string", "name": "sellerEmail", "type": "string"},
            {"internalType": "string", "name": "item", "type": "string"},
            {"internalType": "string", "name": "price", "type": "string"}
        ],
        "name": "completeTrade",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def get_web3_provider():
    if not RPC_URL:
        return None
    return Web3(Web3.HTTPProvider(RPC_URL))

def write_trade_to_blockchain(trade_id: str, buyer_email: str, seller_email: str, item_title: str, price: str = "0"):
    """
    Writes trade details to the blockchain.
    Returns the transaction hash as a hex string.
    """
    if not all([RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY]):
        print("Blockchain configuration missing. Skipping blockchain write.")
        # Return None or raising warning, depending on requirement. 
        # For now, let's return None so the flow doesn't break if not configured.
        return None

    w3 = get_web3_provider()
    if not w3 or not w3.is_connected():
        print("Failed to connect to blockchain network.")
        return None

    try:
        # Initialize contract
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        
        # Build transaction
        account = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Prepare transaction data
        # Note: 'price' in your screenshot was passed. Assuming it's a string or can be converted.
        tx = contract.functions.completeTrade(
            trade_id,
            buyer_email,
            seller_email,
            item_title,
            str(price)
        ).build_transaction({
            'chainId': w3.eth.chain_id,  # Or hardcode if specific
            'gas': 2000000, # Adjust as needed
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt? The prompt said "Fire and Forget or Wait". 
        # "10-15 seconds. You might want to run this in the background... OR show spinner".
        # Since we are in an async function in FastAPI, awaiting this might block the request if we wait for receipt.
        # But `send_raw_transaction` returns hash immediately. 
        # Waiting for receipt `w3.eth.wait_for_transaction_receipt(tx_hash)` takes time.
        # The user's code `await writeTradeToBlockchain` suggests they might want to wait or at least get the hash.
        # Returning the hash immediately is best for "Fire and Forget" style where user gets hash.
        
        return w3.to_hex(tx_hash)

    except Exception as e:
        print(f"Blockchain Error: {e}")
        return None
