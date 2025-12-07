export interface Item {
	id: string;
	user_id: string;
	title: string;
	description: string;
	category: string;
	condition: string;
	images: string[];
	specs?: Record<string, string>;
	location?: string;
	latitude?: number;
	longitude?: number;
	status: 'available' | 'traded' | 'removed' | 'draft' | 'pending';
	views: number;
	created_at: string; // Backend sends ISO string
	updated_at: string; // Backend sends ISO string
	// Computed fields (backend sends these flattened or nested)
	owner_id?: string;
	owner_name?: string;
	owner?: {
		id: string;
		name: string;
		avatar?: string;
		rating?: number;
	};
	distance?: number; // Distance from user in kilometers (computed client-side)
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
	specs?: Record<string, string>;
	location?: string;
	latitude?: number;
	longitude?: number;
	status?: 'available' | 'traded' | 'removed' | 'draft' | 'pending';
}

export interface UpdateItemData {
	title?: string;
	description?: string;
	category?: string;
	condition?: string;
	images?: string[];
	status?: Item['status'];
	location?: string;
	latitude?: number;
	longitude?: number;
	specs?: Record<string, string>;
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
