<script lang="ts">
  let theme = $state<'light'|'dark'>('light');
</script>

<div class="p-6">
  <h1 class="text-2xl font-bold mb-4">Settings</h1>
  <div class="bg-white border rounded-xl p-4">
    <label class="block mb-2 font-medium">Theme</label>
    <select bind:value={theme} class="px-3 py-2 border rounded-lg">
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  </div>
</div>


