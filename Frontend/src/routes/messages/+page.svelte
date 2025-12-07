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
	let showMobileSidebar = $state(true); // Show conversations list on mobile by default

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
		await messagesStore.bootstrap(conversation.trade_id, user.id);
		messagesStore.markMessagesRead();

		// On mobile, hide sidebar when conversation is selected
		if (window.innerWidth < 1024) {
			showMobileSidebar = false;
		}
	}

	function goBackToList() {
		conversationsStore.select(null);
		showMobileSidebar = true;
	}

	async function sendMessage() {
		if (!user) return;
		const state = $conversationsStore;
		const conversation = state.selected;
		if (!conversation) return;
		const content = composedMessage.trim();
		if (!content) return;
		await messagesStore.send(content, conversation.other_user.id, conversation.trade_id);
		conversationsStore.refresh();
		composedMessage = '';
	}
</script>

<svelte:head>
	<title>Messages - Bayanihan Exchange</title>
	<meta name="description" content="Chat with other users about trade offers" />
</svelte:head>

<div class="h-[calc(100vh-4rem)] w-full overflow-hidden bg-white">
	{#if $conversationsStore.isBootstrapping}
		<LoadingSpinner size="large" message="Loading your messages..." />
	{:else if isAuthenticated}
		<div class="flex h-full overflow-hidden">
			{#if $conversationsStore.error}
				<div
					class="absolute left-1/2 top-4 z-50 -translate-x-1/2 rounded-full bg-red-50 px-4 py-2 text-sm text-red-600 shadow-lg ring-1 ring-red-100"
				>
					<div class="flex items-center gap-2">
						<span>{$conversationsStore.error}</span>
						<button
							class="font-semibold underline hover:no-underline"
							onclick={() => conversationsStore.refresh()}
						>
							Retry
						</button>
					</div>
				</div>
			{/if}

			<!-- Conversations List - Responsive -->
			<div
				class="flex h-full w-full flex-col border-r border-gray-100 bg-white transition-all duration-300 lg:w-80 xl:w-96
				{showMobileSidebar && !$conversationsStore.selected ? 'flex' : 'hidden lg:flex'}"
			>
				<ConversationsList
					conversations={$filteredConversations}
					searchQuery={$conversationsStore.searchQuery}
					selectedTradeId={$conversationsStore.selected?.trade_id ?? null}
					on:select={(event) => selectConversation(event.detail)}
					on:search={(event) => conversationsStore.setSearch(event.detail)}
				/>
			</div>

			<!-- Chat Area - Responsive -->
			<div
				class="flex h-full flex-1 flex-col bg-white
				{!showMobileSidebar || $conversationsStore.selected ? 'flex' : 'hidden lg:flex'}"
			>
				{#if $conversationsStore.selected}
					<!-- Mobile Back Button Header -->
					<div class="flex items-center border-b border-gray-100 p-2 lg:hidden">
						<button
							onclick={goBackToList}
							class="flex items-center gap-2 rounded-lg px-3 py-2 text-gray-600 transition-colors hover:bg-gray-50"
						>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 19l-7-7 7-7"
								/>
							</svg>
							<span class="font-medium">Back</span>
						</button>
					</div>

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
					<!-- Empty State -->
					<div class="flex flex-1 items-center justify-center bg-gray-50/50 px-6 text-center">
						<div class="max-w-md space-y-6">
							<div
								class="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-red-50"
							>
								<svg
									class="h-12 w-12 text-red-500"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1.5"
										d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
									/>
								</svg>
							</div>
							<div>
								<h3 class="text-xl font-semibold text-gray-900">Your Messages</h3>
								<p class="mt-2 text-gray-500">
									Select a conversation to start chatting or discover new items to trade.
								</p>
							</div>
							<button
								onclick={() => goto('/discovery')}
								class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 font-medium text-white shadow-sm transition-all hover:bg-red-700 hover:shadow-md"
							>
								Browse Items
							</button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
