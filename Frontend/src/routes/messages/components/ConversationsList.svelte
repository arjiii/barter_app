<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { goto } from '$app/navigation';
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
			conversation.other_user.avatar ||
			`https://ui-avatars.com/api/?name=${encodeURIComponent(
				conversation.other_user.name || 'User'
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

<div class="flex h-full w-full flex-col bg-white">
	<div class="border-b border-gray-100 px-4 py-4">
		<div class="mb-4 flex items-center justify-between">
			<h2 class="text-xl font-bold text-gray-900">Messages</h2>
			<div class="flex items-center gap-2">
				<button
					class="rounded-full p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900"
					aria-label="New chat"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
				</button>
			</div>
		</div>

		<div class="relative">
			<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
				<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
					/>
				</svg>
			</div>
			<input
				type="text"
				value={searchQuery}
				placeholder="Search messages..."
				oninput={handleSearch}
				class="w-full rounded-xl border border-gray-200 bg-gray-50 py-2.5 pl-10 pr-4 text-sm text-gray-900 transition-all placeholder:text-gray-500 focus:border-red-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-500/20"
			/>
		</div>
	</div>

	<div class="flex-1 overflow-y-auto px-2 py-2">
		{#each conversations as conversation}
			<button
				onclick={() => handleSelect(conversation)}
				class={`group mb-1 flex w-full items-center gap-3 rounded-xl border border-transparent px-3 py-3 text-left transition-all ${
					selectedTradeId === conversation.trade_id
						? 'border-red-100 bg-red-50'
						: 'hover:bg-gray-50'
				}`}
			>
				<div
					class="relative cursor-pointer transition-transform hover:scale-105"
					role="button"
					tabindex="0"
					onclick={(e) => {
						e.stopPropagation();
						goto(`/user/${conversation.other_user.id}`);
					}}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.stopPropagation();
							goto(`/user/${conversation.other_user.id}`);
						}
					}}
				>
					<img
						src={getAvatar(conversation)}
						alt={conversation.other_user.name}
						class="h-12 w-12 rounded-full object-cover ring-2 ring-white"
					/>
					{#if conversation.other_user.online}
						<div
							class="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full border-2 border-white bg-green-500"
						></div>
					{:else}
						<div
							class="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full border-2 border-white bg-gray-300"
						></div>
					{/if}
				</div>
				<div class="min-w-0 flex-1">
					<div class="flex items-center justify-between gap-2">
						<h3
							class={`truncate font-semibold ${selectedTradeId === conversation.trade_id ? 'text-gray-900' : 'text-gray-700 group-hover:text-gray-900'}`}
						>
							{conversation.other_user.name}
						</h3>
						<span class="text-xs text-gray-400">{getTimestamp(conversation.last_message_time)}</span
						>
					</div>
					<p
						class={`truncate text-sm ${selectedTradeId === conversation.trade_id ? 'text-gray-600' : 'text-gray-500'}`}
					>
						{conversation.last_message}
					</p>
					<div class="mt-1 flex items-center justify-between text-xs">
						<span class="truncate text-gray-400">{conversation.trade_item?.title}</span>
						{#if (conversation.unread_count || 0) > 0}
							<span
								class="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-600 px-1.5 text-[10px] font-bold text-white shadow-sm"
							>
								{conversation.unread_count}
							</span>
						{/if}
					</div>
				</div>
			</button>
		{:else}
			<div class="flex flex-col items-center justify-center py-12 text-center">
				<div class="mb-3 rounded-full bg-gray-50 p-3">
					<svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
				</div>
				<p class="text-sm text-gray-500">No messages found</p>
			</div>
		{/each}
	</div>
</div>
