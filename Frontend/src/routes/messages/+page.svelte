<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/authStore';
	import { messageService } from '$lib/services/messageService';
	import { API_BASE_URL } from '$lib/config/api';
	import { tradeService } from '$lib/services/tradeService';
	import { userService } from '$lib/services/userService';
	import LoadingSpinner from '../components/LoadingSpinner.svelte';
	import type { User } from '$lib/types/auth';
	import type { Conversation, Message } from '$lib/types/messages';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let isLoading = $state(true);
	let selectedConversation: Conversation | null = $state(null);
	let searchQuery = $state('');
	let conversations: Conversation[] = $state([]);
	let messages: Message[] = $state([]);
	let error: string | null = $state(null);
let pendingTradeId: string | null = $state(null);
let isRefreshingConversations = $state(false);
let pendingConversationRetryCount = $state(0);
let pendingRefetchInFlight = $state(false);
let activeSocket: WebSocket | null = null;
let socketReconnectAttempts = 0;
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

function getAvatar(name?: string, url?: string) {
	const fallbackName = name || 'User';
	return url || `https://ui-avatars.com/api/?name=${encodeURIComponent(fallbackName)}&background=ef4444&color=fff`;
}

function formatTimestamp(timestamp?: string) {
	if (!timestamp) return '';
	const date = new Date(timestamp);
	if (Number.isNaN(date.getTime())) return '';
	return date.toLocaleString();
}

	let filteredConversations = $derived(conversations.filter(conv => 
		conv.otherUser.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
		(conv.tradeItem?.title || '').toLowerCase().includes(searchQuery.toLowerCase())
	));

	async function loadConversations() {
		if (!user || isRefreshingConversations) return;
		try {
			isLoading = true;
			isRefreshingConversations = true;
			error = null;
			
			const timeoutPromise = new Promise((_, reject) =>
				setTimeout(() => reject(new Error('Request timeout')), 10000)
			);
			
			const convsPromise = messageService.getConversations(user.id);
			const convs = (await Promise.race([convsPromise, timeoutPromise])) as Conversation[];
			const byUser = new Map<string, Conversation>();
			for (const c of convs) {
				const key = c.otherUser.id;
				const existing = byUser.get(key);
				if (!existing) byUser.set(key, c);
				else {
					const exTime = new Date(existing.lastMessageTime || 0).getTime();
					const curTime = new Date(c.lastMessageTime || 0).getTime();
					if (curTime > exTime) byUser.set(key, c);
				}
			}
			const deduped = Array.from(byUser.values()).filter((conv) => conv.otherUser?.id && conv.otherUser.id !== user.id);
			conversations = deduped.sort((a, b) => {
				const aTime = new Date(a.lastMessageTime || 0).getTime();
				const bTime = new Date(b.lastMessageTime || 0).getTime();
				return bTime - aTime;
			});
			if (pendingTradeId) {
				const pending = conversations.find((c) => c.tradeId === pendingTradeId);
				if (pending) {
					selectConversation(pending);
					pendingTradeId = null;
					pendingConversationRetryCount = 0;
				}
			}
		} catch (err) {
			console.error('Error loading conversations:', err);
			error =
				(err as Error).message === 'Request timeout'
					? 'Request timed out. Please check your connection and try again.'
					: 'Failed to load conversations. Please ensure the API is running.';
			conversations = [];
		} finally {
			isLoading = false;
			isRefreshingConversations = false;
		}
	}

	function upsertIncomingMessage(incoming: Message) {
		const exists = messages.some((msg) => msg.id === incoming.id);
		if (exists) {
			messages = messages.map((msg) => (msg.id === incoming.id ? incoming : msg));
		} else {
			messages = [...messages, incoming].sort(
				(a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
			);
		}
	}

	async function loadMessages(tradeId: string) {
		if (!user) return;
		try {
			const msgs = await messageService.getMessages({ tradeId });
			messages = msgs;
		} catch (err) {
			console.error('Error loading messages:', err);
		}
	}

	function closeSocket() {
		if (activeSocket) {
			activeSocket.onopen = null;
			activeSocket.onclose = null;
			activeSocket.onmessage = null;
			activeSocket.onerror = null;
			activeSocket.close();
			activeSocket = null;
		}
	}

	function openSocket(tradeId: string) {
		if (!user) return;
		closeSocket();
		const wsUrl = `${WS_BASE_URL}/ws/trades/${tradeId}?user_id=${encodeURIComponent(user.id)}`;
		const socket = new WebSocket(wsUrl);
		activeSocket = socket;

		socket.onopen = () => {
			socketReconnectAttempts = 0;
		};

		socket.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				if (data?.type === 'message' && data?.message) {
					const incoming = data.message;
					if (incoming.tradeId !== tradeId) return;
					upsertIncomingMessage({
						id: incoming.id,
						tradeId: incoming.tradeId,
						senderId: incoming.senderId,
						receiverId: incoming.receiverId,
						content: incoming.content,
						isRead: incoming.isRead,
						createdAt: incoming.createdAt ? new Date(incoming.createdAt) : new Date()
					});
					loadConversations();
				}
			} catch (err) {
				console.warn('Failed to parse realtime message', err);
			}
		};

		socket.onclose = () => {
			if (selectedConversation?.tradeId === tradeId && socketReconnectAttempts < 5) {
				const delay = Math.min(1000 * 2 ** socketReconnectAttempts, 10000);
				socketReconnectAttempts += 1;
				setTimeout(() => openSocket(tradeId), delay);
			}
		};

		socket.onerror = () => {
			socket.close();
		};
	}

	// Watch for ?trade=<id> query parameter and auto-select conversation
	$effect(() => {
		if (!isAuthenticated || !user) return;

		const tradeId = $page.url.searchParams.get('trade');

		if (!tradeId) {
			pendingTradeId = null;
			pendingConversationRetryCount = 0;
			return;
		}

		pendingTradeId = tradeId;

		const tradeConversation = conversations.find((c) => c.tradeId === tradeId);

		if (tradeConversation) {
			if (!selectedConversation || selectedConversation.tradeId !== tradeId) {
				selectConversation(tradeConversation);
			}
		} else if (!isLoading && !pendingRefetchInFlight && pendingConversationRetryCount < 2) {
			pendingRefetchInFlight = true;
			pendingConversationRetryCount += 1;
			loadConversations().finally(() => {
				pendingRefetchInFlight = false;
				if (pendingConversationRetryCount >= 2 && pendingTradeId) {
					hydrateConversationFromTrade(pendingTradeId);
					pendingTradeId = null;
				}
			});
		}
	});

	onMount(() => {
		const unsubscribe = authStore.subscribe(async (authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			isLoading = authState.isLoading;
			if (!authState.isLoading && !authState.isAuthenticated) {
				goto('/sign-in-up');
				closeSocket();
			} else if (authState.isAuthenticated && authState.user) {
				await loadConversations();
			}
		});
		return () => unsubscribe();
	});

	onDestroy(() => {
		closeSocket();
	});

	async function selectConversation(conversation: Conversation) {
		selectedConversation = conversation;
		pendingTradeId = conversation.tradeId === pendingTradeId ? null : pendingTradeId;
		await loadMessages(conversation.tradeId);
		openSocket(conversation.tradeId);
	}

	async function sendMessage() {
		if (!selectedConversation || !user) return;
		const messageInput = document.querySelector('#messageInput') as HTMLInputElement;
		const content = messageInput?.value?.trim();
		if (!content) return;
		try {
			await messageService.createMessage(user.id, {
				tradeId: selectedConversation.tradeId,
				receiverId: selectedConversation.otherUser.id,
				content
			});
			messageInput.value = '';
			await loadMessages(selectedConversation.tradeId);
			await loadConversations();
		} catch (error) {
			console.error('Error sending message:', error);
		}
	}

	async function hydrateConversationFromTrade(tradeId: string) {
		if (!user) return;
		try {
			const trade = await tradeService.getTradeById(tradeId);
			if (!trade) {
				error = 'Conversation not found. The trade reference is missing.';
				return;
			}

			const otherUserId = trade.fromUserId === user.id ? trade.toUserId : trade.fromUserId;
			const otherUser = await userService.getUserById(otherUserId);
			if (!otherUser) {
				error = 'Unable to load the other member for this conversation.';
				return;
			}

			const syntheticConversation: Conversation = {
				tradeId: trade.id,
				otherUser: {
					id: otherUser.id,
					name: otherUser.name || 'User',
					avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name || 'User')}&background=ef4444&color=fff`,
					online: false
				},
				tradeItem: { title: trade.message || 'Direct chat' },
				lastMessage: '',
				lastMessageTime: trade.updatedAt ? trade.updatedAt.toISOString?.() ?? '' : '',
				unreadCount: 0
			};

			conversations = [syntheticConversation, ...conversations.filter((c) => c.tradeId !== trade.id)];
			pendingConversationRetryCount = 0;
			error = null;
			await selectConversation(syntheticConversation);
		} catch (err) {
			console.error('Failed to hydrate conversation from trade:', err);
			error = 'We could not open this chat because the conversation list failed to load.';
		}
	}
</script>

<div class="p-4 lg:p-6">
	<!-- Header removed per request -->

{#if isLoading}
		<LoadingSpinner size="large" message="Loading your messages..." />
	{:else if isAuthenticated}
		<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
			{#if error}
				<div class="bg-yellow-50 border-b border-yellow-200 px-4 py-3 text-sm text-yellow-900 flex items-center justify-between">
					<div class="flex items-center gap-2">
						<svg class="h-5 w-5 text-yellow-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span>{error}</span>
					</div>
					<div class="space-x-2">
						<button class="text-sm font-semibold text-red-600 hover:underline" onclick={() => { pendingConversationRetryCount = 0; loadConversations(); }}>
							Try again
						</button>
						<button class="text-sm text-gray-600 hover:underline" onclick={() => location.reload()}>
							Refresh
						</button>
					</div>
				</div>
			{/if}
			<div class="flex flex-col lg:flex-row h-[600px]">
				<!-- Conversations List -->
				<div class="w-full lg:w-1/3 border-b lg:border-b-0 lg:border-r border-gray-200 flex flex-col">
					<!-- Search -->
					<div class="p-4 border-b border-gray-200">
						<div class="relative">
							<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
								<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
								</svg>
							</div>
							<input
								type="text"
								bind:value={searchQuery}
								placeholder="Search conversations..."
								class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 text-sm transition-colors"
							/>
						</div>
					</div>

					<!-- Conversations -->
					<div class="flex-1 overflow-y-auto">
						{#each filteredConversations as conversation}
							<button
								onclick={() => selectConversation(conversation)}
								class="w-full p-4 text-left hover:bg-gray-50 border-b border-gray-100 transition-colors group
									{selectedConversation?.tradeId === conversation.tradeId ? 'bg-red-50 border-red-200' : ''}"
							>
								<div class="flex items-center space-x-3">
									<div class="relative">
										<img 
											src={getAvatar(conversation.otherUser.name, conversation.otherUser.avatar)} 
											alt={conversation.otherUser.name}
											class="w-12 h-12 rounded-full object-cover"
										/>
										{#if conversation.otherUser.online}
											<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-white rounded-full"></div>
										{/if}
									</div>
									<div class="flex-1 min-w-0">
										<div class="flex items-center justify-between mb-1">
											<h3 class="font-medium text-gray-900 truncate">{conversation.otherUser.name}</h3>
											<span class="text-xs text-gray-500">{formatTimestamp(conversation.lastMessageTime)}</span>
										</div>
										<p class="text-sm text-gray-600 truncate mb-1">{conversation.lastMessage}</p>
										<div class="flex items-center justify-between">
											<span class="text-xs text-gray-500">{conversation.tradeItem?.title}</span>
											{#if (conversation.unreadCount || 0) > 0}
												<span class="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
													{conversation.unreadCount}
												</span>
											{/if}
										</div>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</div>

				<!-- Chat Area -->
				<div class="flex-1 flex flex-col">
					{#if selectedConversation}
						<!-- Chat Header -->
						<div class="p-4 border-b border-gray-200 bg-gray-50">
							<div class="flex items-center space-x-3">
								<div class="relative">
									<img 
										src={getAvatar(selectedConversation.otherUser.name, selectedConversation.otherUser.avatar)} 
										alt={selectedConversation.otherUser.name}
										class="w-10 h-10 rounded-full object-cover"
									/>
									{#if selectedConversation.otherUser.online}
										<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-white rounded-full"></div>
									{/if}
								</div>
								<div class="flex-1 min-w-0">
									<h3 class="font-semibold text-gray-900 truncate">{selectedConversation.otherUser.name}</h3>
									<p class="text-sm text-gray-500 truncate">
										{selectedConversation.otherUser.online ? 'Online' : 'Offline'} • {selectedConversation.tradeItem?.title}
									</p>
								</div>
							</div>
						</div>

						<!-- Messages -->
						<div class="flex-1 overflow-y-auto p-4 space-y-4">
							{#each messages as message}
								<div class={"flex " + (message.senderId === user?.id ? 'justify-end' : 'justify-start')}>
									<div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg
										{(message.senderId === user?.id) 
											? 'bg-red-600 text-white' 
											: 'bg-gray-200 text-gray-900'}"
									>
										<p class="text-sm">{message.content}</p>
										<p class="text-xs mt-1 opacity-70">{new Date(message.createdAt).toLocaleString()}</p>
									</div>
								</div>
							{/each}
						</div>

						<!-- Message Input -->
						<div class="p-4 border-t border-gray-200 bg-gray-50">
							<div class="flex items-center space-x-3">
								<input
									id="messageInput"
									type="text"
									placeholder="Type a message..."
									class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
									onkeydown={(e) => e.key === 'Enter' && sendMessage()}
								/>
								<button
									onclick={sendMessage}
									class="bg-red-600 text-white px-4 py-3 rounded-xl hover:bg-red-700 transition-colors shadow-sm hover:shadow-md"
									aria-label="Send message"
								>
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
									</svg>
								</button>
							</div>
						</div>
					{:else}
						<!-- No conversation selected -->
						<div class="flex-1 flex items-center justify-center">
							<div class="text-center">
								<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
								</svg>
								<h3 class="mt-2 text-sm font-medium text-gray-900">No conversation selected</h3>
								<p class="mt-1 text-sm text-gray-500">Choose a conversation to start messaging</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Empty State removed per request -->
	{/if}
</div>
