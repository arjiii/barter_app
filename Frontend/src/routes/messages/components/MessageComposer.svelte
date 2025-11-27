<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let value = '';
	export let disabled = false;

	const dispatch = createEventDispatcher<{
		send: void;
		input: string;
		typing: void;
	}>();

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		dispatch('input', target.value);
		dispatch('typing');
	}

	function handleSend() {
		dispatch('send');
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSend();
		} else {
			dispatch('typing');
		}
	}
</script>

<div class="px-6 py-4 border-t border-[#f2d8bf] bg-[#fff7f0]/70 backdrop-blur">
	<div class="flex items-center gap-3">
		<div class="flex gap-2">
			<button class="p-3 rounded-full bg-white/70 hover:bg-white shadow-sm" aria-label="Add attachment">
				<svg class="h-5 w-5 text-[#4c3527]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15a4 4 0 01-4 4H7a4 4 0 01-4-4V7a4 4 0 014-4h7l5 5v7z" />
				</svg>
			</button>
			<button class="p-3 rounded-full bg-white/70 hover:bg-white shadow-sm" aria-label="Add emoji">
				<svg class="h-5 w-5 text-[#4c3527]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10h.01M15 10h.01M8 15a4 4 0 008 0" />
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21a9 9 0 100-18 9 9 0 000 18z" />
				</svg>
			</button>
		</div>
		<input
			type="text"
			placeholder="Aa"
			value={value}
			on:input={handleInput}
			on:keydown={handleKeydown}
			class="flex-1 px-4 py-3 rounded-full bg-white border border-[#edd2bb] text-[#3c2d23] placeholder:text-[#a98366] focus:border-[#d9b695] focus:outline-none focus:ring-2 focus:ring-[#ffa97a]/40 transition-all"
		/>
		<button
			type="button"
			on:click={handleSend}
			class="p-3 rounded-full bg-[#ff914d] hover:bg-[#ff7c2d] text-white transition-colors shadow-lg shadow-[#ff914d]/40 disabled:opacity-50"
			disabled={disabled}
			aria-label="Send message"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
			</svg>
		</button>
	</div>
</div>

