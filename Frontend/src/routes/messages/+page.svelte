<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/authStore';
	import LoadingSpinner from '../components/LoadingSpinner.svelte';
	import ConversationsList from './components/ConversationsList.svelte';
	import ChatHeader from './components/ChatHeader.svelte';
	import MessageList from './components/MessageList.svelte';
	import MessageComposer from './components/MessageComposer.svelte';
	import { conversationsStore } from '$lib/stores/conversations';
	import { messagesStore } from '$lib/stores/messages';
	import type { User } from '$lib/types/auth';
	import type { Conversation } from '$lib/types/messages';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let composedMessage = $state('');
	const filteredConversations = conversationsStore.filtered;
	const typingIndicator = messagesStore.typingIndicator;
	const seenStore = messagesStore.lastMessageSeen;

	// Watch for ?trade=<id> query parameter and auto-select conversation
	$effect(() => {
		if (!isAuthenticated || !user) return;
		const tradeId = $page.url.searchParams.get('trade');
		if (!tradeId) {
			conversationsStore.setPendingTradeId(null);
			return;
		}
		conversationsStore.setPendingTradeId(tradeId);
		(async () => {
			const conversation = await conversationsStore.ensureConversation(tradeId);
			if (conversation) {
				await selectConversation(conversation);
			}
		})();
	});

	onMount(() => {
		const unsubscribe = authStore.subscribe(async (authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			if (!authState.isLoading && !authState.isAuthenticated) {
				goto('/sign-in-up');
				conversationsStore.reset();
				messagesStore.reset();
			} else if (authState.isAuthenticated && authState.user) {
				conversationsStore.setUser(authState.user.id);
			}
		});
		return () => unsubscribe();
	});

	onDestroy(() => {
		conversationsStore.reset();
		messagesStore.reset();
	});

	async function selectConversation(conversation: Conversation) {
		if (!user) return;
		conversationsStore.select(conversation);
		await messagesStore.bootstrap(conversation.tradeId, user.id);
		messagesStore.markMessagesRead();
	}

	async function sendMessage() {
		if (!user) return;
		const state = $conversationsStore;
		const conversation = state.selected;
		if (!conversation) return;
		const content = composedMessage.trim();
		if (!content) return;
		await messagesStore.send(content, conversation.otherUser.id, conversation.tradeId);
		conversationsStore.refresh();
		composedMessage = '';
	}
</script>

<div class="px-4 lg:px-8 py-6 h-full">
	{#if $conversationsStore.isBootstrapping}
		<LoadingSpinner size="large" message="Loading your messages..." />
	{:else if isAuthenticated}
		<div class="rounded-3xl bg-[#fff8f1] p-1 shadow-xl border border-[#f0dfcf] h-full min-h-[calc(100vh-11rem)] flex flex-col">
			{#if $conversationsStore.error}
				<div class="bg-yellow-100/10 border border-yellow-500/40 text-yellow-100 text-sm rounded-2xl mx-4 my-4 px-4 py-3 flex flex-wrap items-center justify-between gap-3">
					<div class="flex items-center gap-2">
						<svg class="h-5 w-5 text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span>{$conversationsStore.error}</span>
					</div>
					<div class="flex items-center gap-3">
						<button class="text-sm font-semibold text-red-300 hover:text-red-200 transition-colors" onclick={() => conversationsStore.refresh()}>
							Try again
						</button>
						<button class="text-sm text-gray-300 hover:text-white transition-colors" onclick={() => location.reload()}>
							Refresh
						</button>
					</div>
				</div>
			{/if}

			<div class="flex flex-col lg:flex-row flex-1 min-h-0 bg-[#fdf5ed] rounded-3xl overflow-hidden border border-[#f2e2d1]">
				<ConversationsList
					conversations={$filteredConversations}
					searchQuery={$conversationsStore.searchQuery}
					selectedTradeId={$conversationsStore.selected?.tradeId ?? null}
					on:select={(event) => selectConversation(event.detail)}
					on:search={(event) => conversationsStore.setSearch(event.detail)}
				/>

				<div class="flex-1 flex flex-col bg-gradient-to-b from-[#fff9f5] via-[#fff4eb] to-[#f5dcc6] min-h-0">
					{#if $conversationsStore.selected}
						<ChatHeader conversation={$conversationsStore.selected} typingText={$typingIndicator} />
						<MessageList
							messages={$messagesStore.items}
							currentUserId={user?.id ?? null}
							typingText={$typingIndicator}
							seenTimestamp={$seenStore}
							on:bottom={(event) => messagesStore.setAtBottom(event.detail)}
						/>
						<MessageComposer
							value={composedMessage}
							disabled={$messagesStore.isSending}
							on:input={(event) => (composedMessage = event.detail)}
							on:typing={() => messagesStore.notifyTyping()}
							on:send={sendMessage}
						/>
					{:else}
						<div class="flex-1 flex items-center justify-center text-center px-6">
							<div class="space-y-3">
								<svg class="mx-auto h-12 w-12 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
								</svg>
								<h3 class="text-white text-lg font-semibold">Select a conversation</h3>
								<p class="text-white/60 max-w-sm mx-auto">Choose a chat from the left to start messaging just like in Messenger.</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
