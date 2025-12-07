<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Conversation } from '$lib/types/messages';

	export let conversation: Conversation | null = null;
	export let typingText = '';
</script>

{#if conversation}
	<div class="border-b border-gray-100 bg-white px-4 py-3 lg:px-6 lg:py-4">
		<div class="flex items-center justify-between gap-3">
			<div
				class="flex min-w-0 cursor-pointer items-center gap-3 transition-opacity hover:opacity-80"
				role="button"
				tabindex="0"
				onclick={() => goto(`/user/${conversation.other_user.id}`)}
				onkeydown={(e) => {
					if (e.key === 'Enter' || e.key === ' ') {
						goto(`/user/${conversation.other_user.id}`);
					}
				}}
			>
				<div class="relative">
					<img
						src={conversation.other_user.avatar}
						alt={conversation.other_user.name}
						class="h-10 w-10 rounded-full object-cover ring-2 ring-white lg:h-12 lg:w-12"
					/>
					<div
						class={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white ${
							conversation.other_user.online ? 'bg-green-500' : 'bg-gray-300'
						}`}
					></div>
				</div>
				<div class="min-w-0">
					<h3 class="truncate font-bold text-gray-900">
						{conversation.other_user.name}
					</h3>
					<p class="truncate text-xs text-gray-500 lg:text-sm">
						{#if typingText}
							<span class="font-medium text-red-600">{typingText}</span>
						{:else}
							{conversation.other_user.online ? 'Active now' : 'Offline'} • {conversation.trade_item
								?.title}
						{/if}
					</p>
				</div>
			</div>
			<div class="flex items-center gap-1 lg:gap-2">
				<button
					class="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
					aria-label="Start call"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 5h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V7a2 2 0 012-2z"
						/>
					</svg>
				</button>
				<button
					class="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
					aria-label="Start video"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 6h8a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2z"
						/>
					</svg>
				</button>
				<button
					class="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
					aria-label="Conversation details"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</button>
			</div>
		</div>
	</div>
{/if}
