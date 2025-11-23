export interface Trade {
	id: string;
	fromUserId: string;
	toUserId: string;
	fromItemId: string;
	toItemId: string;
	message: string;
	status: 'pending' | 'accepted' | 'rejected' | 'active' | 'completed' | 'cancelled';
	expiresAt?: Date;
	meetingLocation?: string;
	meetingTime?: Date;
	createdAt: Date;
	updatedAt: Date;
	// Computed fields
	fromUser?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	toUser?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	fromItem?: {
		id: string;
		title: string;
		image?: string;
	};
	toItem?: {
		id: string;
		title: string;
		image?: string;
	};
	createdAgo?: string;
	expiresIn?: string;
}

export interface CreateTradeData {
	toUserId: string;
	fromItemId: string;
	toItemId: string;
	message: string;
	expiresAt?: Date;
	meetingLocation?: string;
	meetingTime?: Date;
}

export interface UpdateTradeData {
	status?: Trade['status'];
	meetingLocation?: string;
	meetingTime?: Date;
	message?: string;
}

export interface TradeFilters {
	userId?: string;
	status?: Trade['status'];
	type?: 'sent' | 'received';
	limit?: number;
	offset?: number;
}
