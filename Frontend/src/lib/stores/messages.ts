import { derived, get, writable } from 'svelte/store';
import type { Message } from '$lib/types/messages';
import { messageService } from '$lib/services/messageService';
import { chatSocketManager } from '$lib/services/chatSocket';

interface MessagesState {
	tradeId: string | null;
	userId: string | null;
	items: Message[];
	isLoading: boolean;
	isSending: boolean;
	typingUsers: Record<string, number>;
	onlineUsers: Record<string, boolean>;
	pendingMessageMap: Record<string, string>;
	atBottom: boolean;
	lastSeenMessageId: string | null;
}

const initialState: MessagesState = {
	tradeId: null,
	userId: null,
	items: [],
	isLoading: false,
	isSending: false,
	typingUsers: {},
	onlineUsers: {},
	pendingMessageMap: {},
	atBottom: true,
	lastSeenMessageId: null
};

let typingTimer: ReturnType<typeof setTimeout> | null = null;

function createMessagesStore() {
	const store = writable<MessagesState>(initialState);
	const { subscribe, set, update } = store;

	async function loadMessages(tradeId: string, userId: string) {
		update((current) => ({ ...current, tradeId, userId, isLoading: true }));
		try {
			const data = await messageService.getMessages({ tradeId });
			update((current) => ({
				...current,
				items: data.sort(
					(a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
				),
				isLoading: false
			}));
		} catch (error) {
			console.error('Failed to load messages', error);
			update((current) => ({ ...current, isLoading: false }));
		}
	}

	function connectSocket(tradeId: string, userId: string) {
		chatSocketManager.connect(tradeId, userId, {
			onMessage: (incoming) => {
				const normalized: Message = {
					id: incoming.id,
					tradeId: incoming.tradeId,
					senderId: incoming.senderId,
					receiverId: incoming.receiverId,
					content: incoming.content,
					isRead: incoming.isRead,
					createdAt: incoming.createdAt ? new Date(incoming.createdAt) : new Date()
				};
				update((current) => {
					const pendingId = Object.entries(current.pendingMessageMap).find(
						([tempId, receiverId]) => receiverId === normalized.id
					)?.[0];
					let items = [...current.items];
					if (pendingId) {
						items = items.map((message) =>
							message.id === pendingId ? normalized : message
						);
						const { [pendingId]: _discard, ...rest } = current.pendingMessageMap;
						current.pendingMessageMap = rest;
					} else if (!items.some((msg) => msg.id === normalized.id)) {
						items = [...items, normalized];
					}
					items.sort(
						(a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
					);
					return { ...current, items };
				});
			},
			onTyping: ({ userId: typingUserId, isTyping }) => {
				update((current) => ({
					...current,
					typingUsers: {
						...current.typingUsers,
						[typingUserId]: isTyping ? Date.now() : 0
					}
				}));
			},
			onPresence: ({ userId: presenceUserId, online }) => {
				update((current) => ({
					...current,
					onlineUsers: { ...current.onlineUsers, [presenceUserId]: online }
				}));
			},
			onRead: ({ messageId, readerId }) => {
				update((current) => ({
					...current,
					items: current.items.map((message) =>
						message.id === messageId ? { ...message, isRead: true, readBy: readerId } : message
					)
				}));
			}
		});
	}

	async function sendMessage(content: string, receiverId: string, tradeId: string) {
		const tempId = crypto.randomUUID();
		const optimisticMessage: Message = {
			id: tempId,
			tradeId,
			senderId: get(store).userId!,
			receiverId,
			content,
			isRead: false,
			createdAt: new Date()
		};
		update((current) => ({
			...current,
			items: [...current.items, optimisticMessage],
			isSending: true,
			pendingMessageMap: { ...current.pendingMessageMap, [tempId]: '' }
		}));

		try {
			const saved = await messageService.createMessage(get(store).userId!, {
				tradeId,
				receiverId,
				content
			});
			update((current) => ({
				...current,
				items: current.items.map((message) =>
					message.id === tempId ? saved : message
				),
				isSending: false
			}));
		} catch (error) {
			console.error('Failed to send message', error);
			update((current) => ({
				...current,
				isSending: false,
				items: current.items.filter((message) => message.id !== tempId)
			}));
		}
	}

	function notifyTyping() {
		if (!get(store).tradeId || !get(store).userId) return;
		chatSocketManager.emitTyping(true);
		if (typingTimer) {
			clearTimeout(typingTimer);
		}
		typingTimer = setTimeout(() => chatSocketManager.emitTyping(false), 1500);
	}

	function markMessagesRead() {
		const state = get(store);
		if (!state.tradeId || !state.userId) return;
		const unread = state.items.filter(
			(message) => message.receiverId === state.userId && !message.isRead
		);
		if (!unread.length) return;
		chatSocketManager.emitRead(unread.map((m) => m.id));
		update((current) => ({
			...current,
			items: current.items.map((message) =>
				unread.some((u) => u.id === message.id) ? { ...message, isRead: true } : message
			),
			lastSeenMessageId: unread[unread.length - 1].id
		}));
	}

	const typingIndicator = derived(store, ($state) => {
		const active = Object.entries($state.typingUsers).filter(
			([, timestamp]) => timestamp && Date.now() - timestamp < 2000
		);
		return active.length ? 'User is typing…' : '';
	});

	const lastMessageSeen = derived(store, ($state) => {
		if (!$state.lastSeenMessageId) return null;
		const lastMessage = $state.items.find((msg) => msg.id === $state.lastSeenMessageId);
		return lastMessage ? lastMessage.createdAt : null;
	});

	return {
		subscribe,
		typingIndicator,
		lastMessageSeen,
		setAtBottom(value: boolean) {
			update((current) => ({ ...current, atBottom: value }));
			if (value) markMessagesRead();
		},
		reset() {
			set(initialState);
			chatSocketManager.disconnect();
		},
		async bootstrap(tradeId: string, userId: string) {
			await loadMessages(tradeId, userId);
			connectSocket(tradeId, userId);
		},
		async send(content: string, receiverId: string, tradeId: string) {
			await sendMessage(content, receiverId, tradeId);
		},
		notifyTyping,
		markMessagesRead
	};
}

export const messagesStore = createMessagesStore();

