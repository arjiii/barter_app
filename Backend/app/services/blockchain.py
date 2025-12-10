import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

from ..config import settings

# New Wallet Generated:
# Address: 0xC1373B50591d8E0235c77173857e57FC51f1B4A9
# Private Key: 0x50f5c887a832d3f1c74b15e4a30f40e4d95b63d3fd8663f9154784a329d89204

# Configuration
RPC_URL = settings.sepolia_rpc_url or os.getenv("SEPOLIA_RPC_URL") or os.getenv("BLOCKCHAIN_RPC_URL")
CONTRACT_ADDRESS = settings.contract_address or os.getenv("CONTRACT_ADDRESS") or os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS")
# Ensure PRIVATE_KEY is loaded correctly. If using the generated key, ensure it's in .env or hardcoded for testing (not recommended for prod).
PRIVATE_KEY = settings.backend_wallet_private_key or os.getenv("backend_WALLET_PRIVATE_KEY") or os.getenv("BLOCKCHAIN_PRIVATE_KEY")

# ABI from Smart Contract
# ABI from Smart Contract
CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "string",
                "name": "ratedUserEmail",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "rating",
                "type": "uint8",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "comment",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256",
            },
        ],
        "name": "RatingRecorded",
        "type": "event",
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_userEmail",
                "type": "string",
            },
            {
                "internalType": "uint8",
                "name": "_rating",
                "type": "uint8",
            },
            {
                "internalType": "string",
                "name": "_comment",
                "type": "string",
            },
        ],
        "name": "recordRating",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_tradeId",
                "type": "string",
            },
            {
                "internalType": "string",
                "name": "_buyer",
                "type": "string",
            },
            {
                "internalType": "string",
                "name": "_seller",
                "type": "string",
            },
            {
                "internalType": "string",
                "name": "_item",
                "type": "string",
            },
            {
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256",
            },
        ],
        "name": "recordTrade",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "string",
                "name": "tradeId",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "buyerEmail",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "sellerEmail",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "item",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256",
            },
        ],
        "name": "TradeRecorded",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

def get_web3_provider():
    if not RPC_URL:
        return None
    return Web3(Web3.HTTPProvider(RPC_URL))

def write_trade_to_blockchain(trade_id: str, buyer_email: str, seller_email: str, item_title: str, amount: int = 0):
    """
    Writes trade details to the blockchain.
    Returns the transaction hash as a hex string.
    """
    if not all([RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY]):
        print("Blockchain configuration missing. Skipping blockchain write.")
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
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
        
        # Call recordTrade
        tx = contract.functions.recordTrade(
            trade_id,
            buyer_email,
            seller_email,
            item_title,
            int(amount)
        ).build_transaction({
            'chainId': w3.eth.chain_id, 
            'gas': 2000000, 
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        hex_hash = w3.to_hex(tx_hash)
        print(f"Trade written to blockchain: {hex_hash}")
        return hex_hash

    except Exception as e:
        print(f"Blockchain Error/Trade: {e}")
        return None

def write_rating_to_blockchain(user_email: str, rating: int, comment: str):
    """
    Writes rating to the blockchain.
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
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
        
        # Call recordRating
        tx = contract.functions.recordRating(
            user_email,
            int(rating),
            comment
        ).build_transaction({
            'chainId': w3.eth.chain_id, 
            'gas': 2000000, 
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        hex_hash = w3.to_hex(tx_hash)
        print(f"Rating written to blockchain: {hex_hash}")
        return hex_hash

    except Exception as e:
        print(f"Blockchain Error/Rating: {e}")
        return None
