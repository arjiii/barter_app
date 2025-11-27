<script lang="ts">
	import type { Conversation } from '$lib/types/messages';

	export let conversation: Conversation | null = null;
	export let typingText = '';
</script>

{#if conversation}
	<div class="px-6 py-4 border-b border-[#f2d8bf] bg-[#fff7f0]/60 backdrop-blur">
		<div class="flex items-center justify-between gap-3">
			<div class="flex items-center gap-3 min-w-0">
				<div class="relative">
					<img
						src={conversation.otherUser.avatar}
						alt={conversation.otherUser.name}
						class="w-12 h-12 rounded-full object-cover"
					/>
					<div
						class={`absolute bottom-0 right-0 w-3.5 h-3.5 border-2 border-[#fff7f0] rounded-full ${
							conversation.otherUser.online ? 'bg-green-400' : 'bg-gray-300'
						}`}
					></div>
				</div>
				<div class="min-w-0">
					<h3 class="text-[#2f1f16] font-semibold leading-tight truncate">{conversation.otherUser.name}</h3>
					<p class="text-sm text-[#7d5b45] truncate">
						{#if typingText}
							{typingText}
						{:else}
							{conversation.otherUser.online ? 'Active now' : 'Offline'} • {conversation.tradeItem?.title}
						{/if}
					</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<button class="p-2 rounded-full bg-white/70 hover:bg-white transition-colors shadow-sm" aria-label="Start call">
					<svg class="h-5 w-5 text-[#4c3527]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V7a2 2 0 012-2z" />
					</svg>
				</button>
				<button class="p-2 rounded-full bg-white/70 hover:bg-white transition-colors shadow-sm" aria-label="Start video">
					<svg class="h-5 w-5 text-[#4c3527]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h8a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2z" />
					</svg>
				</button>
				<button class="p-2 rounded-full bg-white/70 hover:bg-white transition-colors shadow-sm" aria-label="Conversation details">
					<svg class="h-5 w-5 text-[#4c3527]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</button>
			</div>
		</div>
	</div>
{/if}

