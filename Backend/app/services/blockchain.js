// src/services/blockchain.js
const { ethers } = require("ethers");
require("dotenv").config();

const contractABI = [
    /* PASTE THE COPIED ABI ARRAY HERE */
    [
        {
            inputs: [],
            stateMutability: "nonpayable",
            type: "constructor",
        },
        {
            anonymous: false,
            inputs: [
                {
                    indexed: true,
                    internalType: "string",
                    name: "ratedUserEmail",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "uint8",
                    name: "rating",
                    type: "uint8",
                },
                {
                    indexed: false,
                    internalType: "string",
                    name: "comment",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "uint256",
                    name: "timestamp",
                    type: "uint256",
                },
            ],
            name: "RatingRecorded",
            type: "event",
        },
        {
            inputs: [
                {
                    internalType: "string",
                    name: "_userEmail",
                    type: "string",
                },
                {
                    internalType: "uint8",
                    name: "_rating",
                    type: "uint8",
                },
                {
                    internalType: "string",
                    name: "_comment",
                    type: "string",
                },
            ],
            name: "recordRating",
            outputs: [],
            stateMutability: "nonpayable",
            type: "function",
        },
        {
            inputs: [
                {
                    internalType: "string",
                    name: "_tradeId",
                    type: "string",
                },
                {
                    internalType: "string",
                    name: "_buyer",
                    type: "string",
                },
                {
                    internalType: "string",
                    name: "_seller",
                    type: "string",
                },
                {
                    internalType: "string",
                    name: "_item",
                    type: "string",
                },
                {
                    internalType: "uint256",
                    name: "_amount",
                    type: "uint256",
                },
            ],
            name: "recordTrade",
            outputs: [],
            stateMutability: "nonpayable",
            type: "function",
        },
        {
            anonymous: false,
            inputs: [
                {
                    indexed: true,
                    internalType: "string",
                    name: "tradeId",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "string",
                    name: "buyerEmail",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "string",
                    name: "sellerEmail",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "string",
                    name: "item",
                    type: "string",
                },
                {
                    indexed: false,
                    internalType: "uint256",
                    name: "amount",
                    type: "uint256",
                },
                {
                    indexed: false,
                    internalType: "uint256",
                    name: "timestamp",
                    type: "uint256",
                },
            ],
            name: "TradeRecorded",
            type: "event",
        },
        {
            inputs: [],
            name: "owner",
            outputs: [
                {
                    internalType: "address",
                    name: "",
                    type: "address",
                },
            ],
            stateMutability: "view",
            type: "function",
        },
    ],
];

// 1. Connect to Sepolia
const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL);

// 2. Create a Wallet instance from your Private Key
const wallet = new ethers.Wallet(
    process.env.backend_WALLET_PRIVATE_KEY,
    provider
);

// 3. Connect to your Contract
const bayanihanContract = new ethers.Contract(
    process.env.CONTRACT_ADDRESS,
    contractABI,
    wallet
);

async function writeTradeToBlockchain(
    tradeId,
    buyerEmail,
    sellerEmail,
    item,
    amount
) {
    try {
        console.log(`Writing trade ${tradeId} to blockchain...`);

        // This sends a real transaction and pays GAS
        const tx = await bayanihanContract.recordTrade(
            tradeId,
            buyerEmail,
            sellerEmail,
            item,
            amount
        );

        // Wait for it to be mined (optional, but good for confirmation)
        const receipt = await tx.wait();

        console.log(`Transaction Confirmed: ${receipt.hash}`);
        return receipt.hash; // Return this to save in your Aiven DB
    } catch (error) {
        console.error("Blockchain Error:", error);
        return null;
    }
}

async function writeRatingToBlockchain(userEmail, rating, comment) {
    try {
        const tx = await bayanihanContract.recordRating(
            userEmail,
            rating,
            comment
        );
        const receipt = await tx.wait();
        return receipt.hash;
    } catch (error) {
        console.error("Blockchain Error:", error);
        return null;
    }
}

module.exports = { writeTradeToBlockchain, writeRatingToBlockchain };
