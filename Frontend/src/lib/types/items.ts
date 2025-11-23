export interface Item {
	id: string;
	userId: string;
	title: string;
	description: string;
	category: string;
	condition: string;
	images: string[];
	location?: string;
	status: 'available' | 'traded' | 'removed' | 'draft' | 'pending';
	views: number;
	createdAt: Date;
	updatedAt: Date;
	// Computed fields
	owner?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	offersCount?: number;
	postedAgo?: string;
}

export interface Category {
	id: string;
	name: string;
	description?: string;
	icon?: string;
	createdAt: Date;
}

export interface CreateItemData {
	title: string;
	description: string;
	category: string;
	condition: string;
	images: string[];
	location?: string;
}

export interface UpdateItemData {
	title?: string;
	description?: string;
	category?: string;
	condition?: string;
	images?: string[];
	status?: Item['status'];
	location?: string;
}

export interface ItemFilters {
	search?: string;
	category?: string;
	condition?: string;
	status?: Item['status'];
	userId?: string;
	limit?: number;
	offset?: number;
}
