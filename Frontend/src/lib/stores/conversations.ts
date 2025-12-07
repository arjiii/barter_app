import { derived, get, writable } from 'svelte/store';
import { messageService } from '$lib/services/messageService';
import { tradeService } from '$lib/services/tradeService';
import { userService } from '$lib/services/userService';
import type { Conversation } from '$lib/types/messages';

interface ConversationsState {
	userId: string | null;
	items: Conversation[];
	selected: Conversation | null;
	isBootstrapping: boolean;
	isRefreshing: boolean;
	searchQuery: string;
	error: string | null;
	pendingTradeId: string | null;
}

const initialState: ConversationsState = {
	userId: null,
	items: [],
	selected: null,
	isBootstrapping: true,
	isRefreshing: false,
	searchQuery: '',
	error: null,
	pendingTradeId: null
};

function dedupeConversations(conversations: Conversation[], userId: string | null) {
	const byUser = new Map<string, Conversation>();
	for (const convo of conversations) {
		const key = convo.other_user.id;
		const existing = byUser.get(key);
		if (!existing) {
			byUser.set(key, convo);
			continue;
		}
		const existingTime = new Date(existing.last_message_time || 0).getTime();
		const currentTime = new Date(convo.last_message_time || 0).getTime();
		if (currentTime > existingTime) {
			byUser.set(key, convo);
		}
	}
	return Array.from(byUser.values()).filter((c) => c.other_user?.id && c.other_user.id !== userId);
}

function sortConversations(conversations: Conversation[]) {
	return [...conversations].sort((a, b) => {
		const aTime = new Date(a.last_message_time || 0).getTime();
		const bTime = new Date(b.last_message_time || 0).getTime();
		return bTime - aTime;
	});
}

function createConversationsStore() {
	const store = writable<ConversationsState>(initialState);
	const { subscribe, set, update } = store;

	async function refreshConversations() {
		const state = get({ subscribe });
		if (!state.userId || state.isRefreshing) return;

		update((current) => ({ ...current, isRefreshing: true, error: null }));
		try {
			const fetched = await messageService.getConversations(state.userId);
			const normalized = sortConversations(dedupeConversations(fetched, state.userId));
			update((current) => ({
				...current,
				items: normalized,
				isRefreshing: false,
				isBootstrapping: false
			}));
		} catch (error) {
			console.error('Failed to load conversations', error);
			update((current) => ({
				...current,
				error: 'Failed to load conversations. Please try again.',
				items: [],
				isRefreshing: false,
				isBootstrapping: false
			}));
		}
	}

	async function hydrateConversationFromTrade(tradeId: string) {
		const state = get({ subscribe });
		if (!state.userId) return null;
		try {
			const trade = await tradeService.getTradeById(tradeId);
			if (!trade) return null;
			const otherUserId = trade.from_user_id === state.userId ? trade.to_user_id : trade.from_user_id;
			const otherUser = await userService.getUserById(otherUserId);
			if (!otherUser) return null;
			const synthetic: Conversation = {
				trade_id: trade.id,
				other_user: {
					id: otherUser.id,
					name: otherUser.name || 'User',
					avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(otherUser.name || 'User')}&background=ef4444&color=fff`,
					online: false
				},
				trade_item: { title: trade.message || 'Direct chat' },
				last_message: '',
				last_message_time: trade.updated_at ? trade.updated_at : '',
				unread_count: 0
			};
			update((current) => ({
				...current,
				items: sortConversations([synthetic, ...current.items.filter((c) => c.trade_id !== synthetic.trade_id)])
			}));
			return synthetic;
		} catch (error) {
			console.error('Failed to hydrate conversation', error);
			return null;
		}
	}

	const filtered = derived(store, ($state) => {
		const query = $state.searchQuery.toLowerCase();
		if (!query) return $state.items;
		return $state.items.filter(
			(conv) =>
				conv.other_user.name.toLowerCase().includes(query) ||
				(conv.trade_item?.title || '').toLowerCase().includes(query)
		);
	});

	return {
		subscribe,
		filtered,
		reset: () => set(initialState),
		setUser(userId: string | null) {
			set({ ...initialState, userId, isBootstrapping: Boolean(userId) });
			if (userId) refreshConversations();
		},
		refresh: refreshConversations,
		setSearch(query: string) {
			update((current) => ({ ...current, searchQuery: query }));
		},
		select(conversation: Conversation | null) {
			if (!conversation) {
				update((current) => ({ ...current, selected: null }));
				return;
			}
			update((current) => ({
				...current,
				selected: conversation,
				items: current.items.map((c) =>
					c.trade_id === conversation.trade_id ? { ...c, unread_count: 0 } : c
				)
			}));
		},
		setPendingTradeId(tradeId: string | null) {
			update((current) => ({ ...current, pendingTradeId: tradeId }));
		},
		getPendingTradeId() {
			return get({ subscribe }).pendingTradeId;
		},
		async ensureConversation(tradeId: string) {
			const state = get({ subscribe });
			const existing = state.items.find((c) => c.trade_id === tradeId);
			if (existing) return existing;
			return hydrateConversationFromTrade(tradeId);
		},
		updateFromSocket(conversation: Conversation) {
			update((current) => {
				const existing = current.items.find((c) => c.trade_id === conversation.trade_id);
				let items = current.items;
				if (existing) {
					items = current.items.map((c) =>
						c.trade_id === conversation.trade_id ? { ...existing, ...conversation } : c
					);
				} else {
					items = [conversation, ...current.items];
				}
				return {
					...current,
					items: sortConversations(items)
				};
			});
		}
	};
}

export const conversationsStore = createConversationsStore();

