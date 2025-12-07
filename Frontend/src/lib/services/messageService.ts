import type { Message, Conversation, CreateMessageData, MessageFilters } from '../types/messages';
import { api, API_BASE_URL } from '../config/api';

class MessageService {
	// Messages CRUD operations
	async createMessage(messageData: CreateMessageData): Promise<Message> {
		try {
			const created = await api.post<Message>('/messages/', messageData);
			return created;
		} catch (error) {
			console.error('Error creating message:', error);
			throw error;
		}
	}

	async getMessageById(id: string): Promise<Message | null> { return null; }

	async getMessages(filters: MessageFilters): Promise<Message[]> {
		try {
			if (!filters.tradeId) return [];
			const msgs = await api.get<Message[]>(`/messages/?trade_id=${encodeURIComponent(filters.tradeId)}`);
			return msgs;
		} catch (error) {
			console.error('Error getting messages:', error);
			return [];
		}
	}

	async getConversations(userId: string): Promise<Conversation[]> {
		try {
			const res = await fetch(`${API_BASE_URL}/messages/conversations?user_id=${encodeURIComponent(userId)}`);
			if (!res.ok) return [];
			const data = await res.json();
			return data.map((c: any) => {
				const name = c.other_user?.name || 'User';
				const avatar = c.other_user?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=ef4444&color=fff`;
				return {
					trade_id: c.trade_id,
					other_user: {
						id: c.other_user?.id,
						name,
						avatar,
						online: c.other_user?.online ?? false
					},
					trade_item: { title: c.trade_item_title || c.trade_item?.title || '' },
					last_message: c.last_message || '',
					last_message_time: c.last_message_time || '',
					unread_count: c.unread_count || 0
				};
			});
		} catch (error) {
			console.error('Error getting conversations:', error);
			return [];
		}
	}

	async updateMessage(id: string, updates: Partial<Message>): Promise<Message | null> { return null; }
	async deleteMessage(id: string): Promise<boolean> { return true; }
	async markAsRead(messageId: string): Promise<boolean> { return true; }
}

export const messageService = new MessageService();