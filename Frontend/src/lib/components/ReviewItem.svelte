<script>
  export let review; // Passed in from parent

  const ratingValue = review?.score ?? review?.rating ?? 0;
  const commentText = review?.feedback ?? review?.comment ?? '';
  const createdAt = review?.created_at ? new Date(review.created_at) : null;
</script>

<div class="review-item">
  <div class="header">
    <span class="stars">{"⭐".repeat(ratingValue)}</span>
    {#if createdAt}
      <span class="date">{createdAt.toLocaleDateString()}</span>
    {/if}
  </div>

  {#if commentText}
    <p class="comment">"{commentText}"</p>
  {/if}

  {#if review.transaction_hash}
    <div class="verification">
      <span class="icon">🔗</span>
      <span class="text">Verified Immutable</span>
      <a
        href={`https://sepolia.etherscan.io/tx/${review.transaction_hash}`}
        target="_blank"
        rel="noopener noreferrer"
        class="etherscan-link"
      >
        (Check Etherscan)
      </a>
    </div>
  {/if}
</div>

<style>
  .review-item {
    border-bottom: 1px solid #eee;
    padding: 1rem 0;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  .stars {
    font-size: 1rem;
  }
  .date {
    font-size: 0.9rem;
    color: #666;
  }
  .comment {
    color: #444;
    margin: 0;
  }
  .verification {
    font-size: 0.8rem;
    color: #666;
    margin-top: 5px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .etherscan-link {
    color: #6366f1; /* Indigo color */
    text-decoration: none;
  }
  .etherscan-link:hover {
    text-decoration: underline;
  }
</style>

