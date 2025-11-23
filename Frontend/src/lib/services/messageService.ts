import { v4 as uuidv4 } from 'uuid';
import type { Message, Conversation, CreateMessageData, MessageFilters } from '../types/messages';
import { api, API_BASE_URL } from '../config/api';

class MessageService {
	// Messages CRUD operations
	async createMessage(senderId: string, messageData: CreateMessageData): Promise<Message | null> {
		try {
			const created = await api.post<any>('/messages/', {
				trade_id: messageData.tradeId,
				sender_id: senderId,
				receiver_id: messageData.receiverId,
				content: messageData.content,
				is_read: false
			});
			return this.mapApiMessageToMessage(created);
		} catch (error) {
			console.error('Error creating message:', error);
			return null;
		}
	}

	async getMessageById(id: string): Promise<Message | null> { return null; }

	async getMessages(filters: MessageFilters): Promise<Message[]> {
		try {
			const msgs = await api.get<any[]>(`/messages/?trade_id=${encodeURIComponent(filters.tradeId)}`);
			return msgs.map(m => this.mapApiMessageToMessage(m));
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
				const name = c.otherUser?.name || 'User';
				const avatar = c.otherUser?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=ef4444&color=fff`;
				return {
					tradeId: c.tradeId,
					otherUser: { 
						id: c.otherUser?.id,
						name,
						avatar,
						online: c.otherUser?.online ?? false
					},
					tradeItem: { title: c.tradeItemTitle || c.tradeItem?.title || '' },
					lastMessage: c.lastMessage || '',
					lastMessageTime: c.lastMessageTime || '',
					unreadCount: c.unreadCount || 0
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

	private mapApiMessageToMessage(m: any): Message {
		return {
			id: m.id,
			tradeId: m.trade_id,
			senderId: m.sender_id,
			receiverId: m.receiver_id,
			content: m.content,
			isRead: !!m.is_read,
			createdAt: m.created_at ? new Date(m.created_at) : new Date()
		};
	}
}

export const messageService = new MessageService();