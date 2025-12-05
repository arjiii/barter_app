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
		await messagesStore.bootstrap(conversation.tradeId, user.id);
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
		await messagesStore.send(content, conversation.otherUser.id, conversation.tradeId);
		conversationsStore.refresh();
		composedMessage = '';
	}
</script>

<svelte:head>
	<title>Messages - Bayanihan Exchange</title>
	<meta name="description" content="Chat with other users about trade offers" />
</svelte:head>

<div class="h-[calc(100vh-4rem)] w-full overflow-hidden bg-[#fff9f5]">
	{#if $conversationsStore.isBootstrapping}
		<LoadingSpinner size="large" message="Loading your messages..." />
	{:else if isAuthenticated}
		<div class="flex h-full flex-col overflow-hidden bg-white">
			{#if $conversationsStore.error}
				<div
					class="mx-4 my-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
				>
					<div class="flex items-center gap-2">
						<svg class="h-5 w-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{$conversationsStore.error}</span>
					</div>
					<div class="flex items-center gap-3">
						<button
							class="font-semibold text-red-600 transition-colors hover:text-red-700"
							onclick={() => conversationsStore.refresh()}
						>
							Try again
						</button>
						<button
							class="text-gray-600 transition-colors hover:text-gray-700"
							onclick={() => location.reload()}
						>
							Refresh
						</button>
					</div>
				</div>
			{/if}

			<div class="flex min-h-0 flex-1 overflow-hidden">
				<!-- Conversations List - Responsive -->
				<div
					class="flex h-full w-full flex-col border-r border-[#f0dfcf] bg-gradient-to-b from-[#fff9f5] to-[#fef6ed] transition-transform duration-300 ease-in-out lg:w-80 xl:w-96 {showMobileSidebar ||
					!$conversationsStore.selected
						? 'translate-x-0'
						: '-translate-x-full lg:translate-x-0'} {$conversationsStore.selected
						? 'absolute inset-0 z-10 lg:relative'
						: ''}"
				>
					<ConversationsList
						conversations={$filteredConversations}
						searchQuery={$conversationsStore.searchQuery}
						selectedTradeId={$conversationsStore.selected?.tradeId ?? null}
						on:select={(event) => selectConversation(event.detail)}
						on:search={(event) => conversationsStore.setSearch(event.detail)}
					/>
				</div>

				<!-- Chat Area - Responsive -->
				<div
					class="flex flex-1 flex-col bg-gradient-to-b from-[#fff9f5] via-[#fff4eb] to-[#fef0e0] {showMobileSidebar &&
					$conversationsStore.selected
						? 'hidden lg:flex'
						: 'flex'}"
				>
					{#if $conversationsStore.selected}
						<!-- Mobile Back Button -->
						<div class="block border-b border-[#f0dfcf] bg-white/50 p-2 backdrop-blur-sm lg:hidden">
							<button
								onclick={goBackToList}
								class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-[#1c1816] transition-colors hover:bg-[#fef6ed]"
								aria-label="Back to conversations"
							>
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 19l-7-7 7-7"
									/>
								</svg>
								<span>Back</span>
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
						<div class="flex flex-1 items-center justify-center px-6 text-center">
							<div class="max-w-md space-y-4">
								<div
									class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-[#ff6d3f] to-[#ff8c5a]"
								>
									<svg
										class="h-10 w-10 text-white"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
										/>
									</svg>
								</div>
								<h3 class="text-xl font-semibold text-[#1c1816]">Select a conversation</h3>
								<p class="text-[#6c6b69]">
									Choose a chat from the list to start messaging with other members of the Bayanihan
									community.
								</p>
								<button
									onclick={() => goto('/discovery')}
									class="mx-auto inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[#ff6d3f] to-[#ff8c5a] px-6 py-3 font-semibold text-white shadow-lg transition-all hover:shadow-xl"
								>
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
										/>
									</svg>
									<span>Discover Items</span>
								</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Smooth transitions for mobile sidebar */
	@media (max-width: 1023px) {
		.translate-x-0 {
			transform: translateX(0);
		}
		.-translate-x-full {
			transform: translateX(-100%);
		}
	}

	/* Custom scrollbar */
	:global(.messages-container::-webkit-scrollbar) {
		width: 6px;
	}

	:global(.messages-container::-webkit-scrollbar-track) {
		background: transparent;
	}

	:global(.messages-container::-webkit-scrollbar-thumb) {
		background: rgba(255, 109, 63, 0.2);
		border-radius: 3px;
	}

	:global(.messages-container::-webkit-scrollbar-thumb:hover) {
		background: rgba(255, 109, 63, 0.3);
	}
</style>
