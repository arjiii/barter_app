export interface Message {
	id: string;
	tradeId: string;
	senderId: string;
	receiverId: string;
	content: string;
	isRead: boolean;
	createdAt: Date;
}

export interface Conversation {
	tradeId: string;
	otherUser: {
		id: string;
		name: string;
		avatar?: string;
		online?: boolean;
	};
	lastMessage?: string;
	lastMessageTime?: string;
	tradeItem?: { title?: string };
	unreadCount?: number;
}

export interface CreateMessageData {
	tradeId: string;
	receiverId: string;
	content: string;
}

export interface MessageFilters {
	tradeId?: string;
	userId?: string;
	limit?: number;
	offset?: number;
}
