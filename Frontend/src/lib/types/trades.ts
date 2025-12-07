export interface Trade {
	id: string;
	from_user_id: string;
	to_user_id: string;
	from_item_id: string;
	to_item_id: string;
	message: string;
	status: 'pending' | 'accepted' | 'rejected' | 'active' | 'completed' | 'cancelled';
	expires_at?: string;
	meeting_location?: string;
	meeting_time?: string;
	created_at: string;
	updated_at: string;
	// Computed fields
	from_user?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	to_user?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	from_item?: {
		id: string;
		title: string;
		image?: string;
	};
	to_item?: {
		id: string;
		title: string;
		image?: string;
	};
}

export interface CreateTradeData {
	to_user_id: string;
	from_item_id: string;
	to_item_id: string;
	message: string;
	expires_at?: string;
	meeting_location?: string;
	meeting_time?: string;
}

export interface UpdateTradeData {
	status?: Trade['status'];
	meeting_location?: string;
	meeting_time?: string;
	message?: string;
}

export interface TradeFilters {
	userId?: string;
	status?: Trade['status'];
	type?: 'sent' | 'received';
	limit?: number;
	offset?: number;
}
