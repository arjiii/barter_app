import type { Item, Category, CreateItemData, UpdateItemData, ItemFilters } from '../types/items';
import { api, API_BASE_URL } from '../config/api';

class ItemService {
	// Items CRUD operations
	async createItem(itemData: CreateItemData): Promise<Item | null> {
		try {
			const created = await api.post<Item>('/items/', itemData);
			return created;
		} catch (error: any) {
			console.error('Error creating item:', error);
			return null;
		}
	}

	async getItemById(id: string): Promise<Item | null> {
		try {
			const item = await api.get<Item>(`/items/${id}`);
			return item;
		} catch (error: any) {
			console.error('Error getting item by ID:', error);
			return null;
		}
	}

	async getItems(filters: ItemFilters = {}): Promise<Item[]> {
		try {
			const params = new URLSearchParams();
			if (filters.userId) params.set('user_id', filters.userId);
			if (filters.status) params.set('status', filters.status);
			if (filters.category) params.set('category', filters.category);
			if (filters.limit) params.set('limit', filters.limit.toString());
			if (filters.offset) params.set('offset', filters.offset.toString());

			const items = await api.get<Item[]>(`/items/?${params.toString()}`);
			return items;
		} catch (error: any) {
			console.error('Error getting items:', error);
			return [];
		}
	}

	async updateItem(id: string, updates: UpdateItemData): Promise<Item | null> {
		try {
			const updated = await api.patch<Item>(`/items/${id}`, updates);
			return updated;
		} catch (error: any) {
			console.error('Error updating item:', error);
			return null;
		}
	}

	async deleteItem(id: string): Promise<boolean> {
		try {
			const token = localStorage.getItem('bayanihan_token');
			const headers: Record<string, string> = {
				'Content-Type': 'application/json'
			};

			if (token) {
				headers['Authorization'] = `Bearer ${token}`;
			}

			const response = await fetch(`${API_BASE_URL}/items/${id}`, {
				method: 'DELETE',
				headers
			});
			return response.ok;
		} catch (error: any) {
			console.error('Error deleting item:', error);
			return false;
		}
	}

	async getCategories(): Promise<Category[]> {
		try {
			const categories = await api.get<any[]>(`/categories/`);
			return categories.map(cat => ({
				id: cat.id,
				name: cat.name,
				description: cat.description,
				icon: cat.icon,
				createdAt: cat.created_at ? new Date(cat.created_at) : new Date()
			}));
		} catch (error: any) {
			console.error('Error getting categories:', error);
			return [];
		}
	}

	async createCategory(categoryData: { name: string; description?: string; icon?: string }): Promise<Category | null> {
		try {
			const created = await api.post<any>(`/categories/`, categoryData);
			return {
				id: created.id,
				name: created.name,
				description: created.description,
				icon: created.icon,
				createdAt: created.created_at ? new Date(created.created_at) : new Date()
			};
		} catch (error: any) {
			console.error('Error creating category:', error);
			return null;
		}
	}

	formatPostedAgo(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMs / 3600000);
		const diffDays = Math.floor(diffMs / 86400000);
		const diffWeeks = Math.floor(diffDays / 7);
		const diffMonths = Math.floor(diffDays / 30);
		const diffYears = Math.floor(diffDays / 365);

		if (diffMins < 1) return 'Just now';
		if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
		if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
		if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
		if (diffWeeks < 4) return `${diffWeeks} week${diffWeeks > 1 ? 's' : ''} ago`;
		if (diffMonths < 12) return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
		return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
	}
}

export const itemService = new ItemService();