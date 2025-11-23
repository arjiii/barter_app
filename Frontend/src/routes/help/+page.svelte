<script lang="ts">
  const faqs = [
    { q: 'How do I post an item?', a: 'Go to My Items and click “Post New Item”. Fill the form and submit.' },
    { q: 'How do trades work?', a: 'Send a trade offer from an item page. The other user can accept or reject.' },
    { q: 'I forgot my password', a: 'Use your sign-in method or contact support below.' }
  ];
  let name = '';
  let email = '';
  let message = '';
  function submit() {
    alert('Thanks! We received your message.');
    name = email = message = '';
  }
</script>

<div class="p-6 max-w-4xl mx-auto">
  <h1 class="text-2xl font-bold mb-4">Help & Support</h1>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="bg-white rounded-xl border p-6">
      <h2 class="font-semibold text-lg mb-3">FAQs</h2>
      <ul class="space-y-3">
        {#each faqs as f}
          <li>
            <div class="font-medium">{f.q}</div>
            <div class="text-sm text-gray-600">{f.a}</div>
          </li>
        {/each}
      </ul>
    </div>
    <div class="bg-white rounded-xl border p-6">
      <h2 class="font-semibold text-lg mb-3">Contact us</h2>
      <div class="space-y-3">
        <input class="w-full px-4 py-2 border rounded-lg" placeholder="Name" bind:value={name} />
        <input class="w-full px-4 py-2 border rounded-lg" placeholder="Email" bind:value={email} />
        <textarea class="w-full px-4 py-2 border rounded-lg" rows="5" placeholder="How can we help?" bind:value={message}></textarea>
        <button class="bg-red-600 text-white px-4 py-2 rounded-lg" on:click={submit}>Send</button>
      </div>
    </div>
  </div>
</div>






















