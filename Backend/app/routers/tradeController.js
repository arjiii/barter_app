const db = require("../db"); // your existing Aiven DB connection
const { writeTradeToBlockchain } = require("../services/blockchain");

exports.completeTrade = async (req, res) => {
    const { tradeId, buyer, seller, item, price } = req.body;

    // 1. Normal Web2 logic (Save to Aiven)
    await db.query("UPDATE trades SET status = $1 WHERE id = $2", [
        "COMPLETED",
        tradeId,
    ]);

    // 2. Web3 logic (Fire and Forget or Wait)
    // Note: This takes 10-15 seconds. You might want to run this in the background
    // so the user doesn't wait, OR show a "Processing on Blockchain" spinner.
    const txHash = await writeTradeToBlockchain(
        tradeId,
        buyer.email,
        seller.email,
        item,
        price
    );

    // 3. Save the Hash back to DB so you can show the user later
    if (txHash) {
        await db.query(
            "UPDATE trades SET transaction_hash = $1 WHERE id = $2",
            [txHash, tradeId]
        );
    }

    res.json({
        success: true,
        message: "Trade completed and verified on chain!",
        txHash,
    });
};
