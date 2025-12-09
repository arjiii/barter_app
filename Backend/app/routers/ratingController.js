const db = require("../db"); // Your database connection
const { writeRatingToBlockchain } = require("../services/blockchain");

exports.submitRating = async (req, res) => {
    // 1. Get IDs from frontend
    const { from_user_id, to_user_id, trade_id, rating, comment } = req.body;

    try {
        // --- STEP A: Fetch the Email (Required for Blockchain) ---
        // We need the email of the person being rated (to_user_id)
        const userResult = await db.query(
            "SELECT email FROM users WHERE id = $1",
            [to_user_id]
        );

        if (userResult.rows.length === 0) {
            return res.status(404).json({ error: "User not found" });
        }

        const ratedUserEmail = userResult.rows[0].email;

        // --- STEP B: Save to Aiven DB (Web2) ---
        // Note: Using your table name 'user_ratings'
        const insertResult = await db.query(
            `INSERT INTO user_ratings 
            (id, from_user_id, to_user_id, trade_id, rating, comment, created_at) 
            VALUES (UUID(), $1, $2, $3, $4, $5, NOW()) 
            RETURNING id`,
            [from_user_id, to_user_id, trade_id, rating, comment]
        );

        const newRatingId = insertResult.rows[0].id;

        // --- STEP C: Save to Blockchain (Web3) ---
        // Use the EMAIL we fetched in Step A
        console.log(`Writing rating for ${ratedUserEmail} to blockchain...`);
        const txHash = await writeRatingToBlockchain(
            ratedUserEmail,
            rating,
            comment
        );

        // --- STEP D: Update DB with Proof ---
        if (txHash) {
            await db.query(
                "UPDATE user_ratings SET transaction_hash = $1 WHERE id = $2",
                [txHash, newRatingId]
            );
        }

        res.status(201).json({
            success: true,
            message: "Rating submitted and verified on-chain!",
            txHash,
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Server error handling rating" });
    }
};
