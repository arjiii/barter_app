const db = require("../db");
const { writeTradeToBlockchain } = require("../services/blockchain");

exports.completeTrade = async (req, res) => {
    const { trade_id } = req.body;

    try {
        // --- STEP A: Fetch Trade Details & Emails ---
        // We join the trades table with the users table TWICE (once for buyer, once for seller)
        const tradeQuery = `
            SELECT 
                t.id, t.from_item_id, t.to_item_id,
                u1.email as seller_email, 
                u2.email as buyer_email
            FROM trades t
            JOIN users u1 ON t.from_user_id = u1.id
            JOIN users u2 ON t.to_user_id = u2.id
            WHERE t.id = $1
        `;

        const tradeResult = await db.query(tradeQuery, [trade_id]);

        if (tradeResult.rows.length === 0)
            return res.status(404).json({ error: "Trade not found" });

        const trade = tradeResult.rows[0];
        const itemDescription = `Trade of item ${trade.from_item_id} for ${trade.to_item_id}`;

        // --- STEP B: Update Status in DB ---
        await db.query(
            "UPDATE trades SET status = 'completed', updated_at = NOW() WHERE id = $1",
            [trade_id]
        );

        // --- STEP C: Write to Blockchain ---
        // Using the emails fetched in Step A
        const txHash = await writeTradeToBlockchain(
            trade.id,
            trade.buyer_email,
            trade.seller_email,
            itemDescription,
            0 // Amount is 0 for barter trades
        );

        // --- STEP D: Save Proof ---
        if (txHash) {
            await db.query(
                "UPDATE trades SET transaction_hash = $1 WHERE id = $2",
                [txHash, trade_id]
            );
        }

        res.json({ success: true, txHash });
    } catch (error) {
        console.error("Trade Error:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
};
