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

<div class="border-t border-gray-100 bg-white px-4 py-3 lg:px-6 lg:py-4">
	<div class="flex items-end gap-2 lg:gap-3">
		<div class="flex gap-1 lg:gap-2">
			<button
				class="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
				aria-label="Add attachment"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 4v16m8-8H4"
					/>
				</svg>
			</button>
			<button
				class="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
				aria-label="Add emoji"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
			</button>
		</div>
		<div class="relative flex-1">
			<textarea
				placeholder="Type a message..."
				{value}
				on:input={handleInput}
				on:keydown={handleKeydown}
				rows="1"
				class="max-h-32 min-h-[44px] w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-500 focus:border-red-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-red-500"
				style="min-height: 44px;"
			></textarea>
		</div>
		<button
			type="button"
			on:click={handleSend}
			class="flex h-11 w-11 items-center justify-center rounded-full bg-red-600 text-white shadow-sm transition-all hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
			disabled={disabled || !value.trim()}
			aria-label="Send message"
		>
			<svg class="h-5 w-5 translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
				/>
			</svg>
		</button>
	</div>
</div>
