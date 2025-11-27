<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Conversation } from '$lib/types/messages';

	export let conversations: Conversation[] = [];
	export let searchQuery = '';
	export let selectedTradeId: string | null = null;

	const dispatch = createEventDispatcher<{
		select: Conversation;
		search: string;
	}>();

	function handleSelect(conversation: Conversation) {
		dispatch('select', conversation);
	}

	function handleSearch(event: Event) {
		const target = event.target as HTMLInputElement;
		dispatch('search', target.value);
	}

	function getAvatar(conversation: Conversation) {
		return (
			conversation.otherUser.avatar ||
			`https://ui-avatars.com/api/?name=${encodeURIComponent(
				conversation.otherUser.name || 'User'
			)}&background=ef4444&color=fff`
		);
	}

	function getTimestamp(value?: string) {
		if (!value) return '';
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return '';
		return date.toLocaleString();
	}
</script>

<div class="w-full lg:w-1/3 xl:w-96 bg-[#f1e4d8] border-[#f2d8bf] border-r flex flex-col min-h-0">
	<div class="px-5 pt-5 pb-4">
		<div class="flex items-center justify-between text-[#3b2a1f] mb-4">
			<div>
				<p class="text-xs uppercase tracking-[0.2em] text-[#a8876d]">Messenger</p>
				<h2 class="text-2xl font-semibold mt-1 text-[#3b2a1f]">Chats</h2>
			</div>
			<div class="flex items-center gap-2">
				<button class="p-2 rounded-full bg-white/60 hover:bg-white transition-colors shadow-sm" aria-label="New chat">
					<svg class="h-5 w-5 text-[#573721]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
				</button>
				<button class="p-2 rounded-full bg-white/60 hover:bg-white transition-colors shadow-sm" aria-label="Options">
					<svg class="h-5 w-5 text-[#573721]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 12h.01M12 12h.01M18 12h.01" />
					</svg>
				</button>
			</div>
		</div>

		<div class="relative">
			<div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
				<svg class="h-5 w-5 text-[#b08b6d]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
				</svg>
			</div>
			<input
				type="text"
				value={searchQuery}
				placeholder="Search Messenger"
				oninput={handleSearch}
				class="w-full pl-10 pr-4 py-2.5 bg-[#fff9f4] border border-[#e5d2c0] rounded-full text-sm text-[#473428] placeholder:text-[#ad8c71] focus:border-[#d9b695] focus:outline-none focus:ring-2 focus:ring-[#ffb88c]/40 transition-all"
			/>
		</div>
	</div>

	<div class="flex-1 overflow-y-auto thin-scrollbar px-2 pb-6 space-y-1 min-h-0">
		{#each conversations as conversation}
			<button
				onclick={() => handleSelect(conversation)}
				class={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-left transition-all border border-transparent ${
					selectedTradeId === conversation.tradeId
						? 'bg-white border-[#f0d7c0] shadow-inner'
						: 'hover:bg-white/60'
				}`}
			>
				<div class="relative">
					<img
						src={getAvatar(conversation)}
						alt={conversation.otherUser.name}
						class="w-12 h-12 rounded-full object-cover"
					/>
					{#if conversation.otherUser.online}
						<div class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-400 border-2 border-[#f1e4d8] rounded-full"></div>
					{:else}
						<div class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-gray-300 border-2 border-[#f1e4d8] rounded-full"></div>
					{/if}
				</div>
				<div class="flex-1 min-w-0">
					<div class="flex items-center justify-between gap-2">
						<h3 class="font-semibold text-[#2f1f16] truncate">{conversation.otherUser.name}</h3>
						<span class="text-[11px] uppercase tracking-wide text-[#a07c61]">{getTimestamp(conversation.lastMessageTime)}</span>
					</div>
					<p class="text-sm text-[#5a4031] truncate">{conversation.lastMessage}</p>
					<div class="flex items-center justify-between text-xs text-[#a07c61] mt-1">
						<span class="truncate">{conversation.tradeItem?.title}</span>
						{#if (conversation.unreadCount || 0) > 0}
							<span class="bg-[#f9735b] text-white text-[10px] font-semibold rounded-full px-2 py-0.5">
								{conversation.unreadCount}
							</span>
						{/if}
					</div>
				</div>
			</button>
		{:else}
			<p class="text-center text-sm text-[#7d685a] py-8">No conversations yet</p>
		{/each}
	</div>
</div>

