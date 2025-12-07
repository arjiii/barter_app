export interface Message {
	id: string;
	trade_id: string;
	sender_id: string;
	receiver_id: string;
	content: string;
	is_read: boolean;
	created_at: string;
}

export interface Conversation {
	trade_id: string;
	other_user: {
		id: string;
		name: string;
		avatar?: string;
		online?: boolean;
	};
	last_message?: string;
	last_message_time?: string;
	trade_item?: { title?: string };
	unread_count?: number;
}

export interface CreateMessageData {
	trade_id: string;
	receiver_id: string;
	content: string;
}

export interface MessageFilters {
	tradeId?: string;
	userId?: string;
	limit?: number;
	offset?: number;
}
