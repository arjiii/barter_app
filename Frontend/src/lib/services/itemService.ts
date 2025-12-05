import { v4 as uuidv4 } from 'uuid';
import type { Item, Category, CreateItemData, UpdateItemData, ItemFilters } from '../types/items';
import { api, API_BASE_URL } from '../config/api';

class ItemService {
	// Items CRUD operations
	async createItem(userId: string, itemData: CreateItemData): Promise<Item | null> {
		try {
			console.log('Creating item with userId:', userId, 'itemData:', itemData);

			const payload = {
				user_id: userId,
				title: itemData.title,
				description: itemData.description,
				category: itemData.category,
				condition: itemData.condition,
				images: itemData.images,
				specs: itemData.specs,
				location: itemData.location,
				status: 'available'
			};

			console.log('Sending payload to API:', payload);

			// Check if we have a token
			const token = localStorage.getItem('bayanihan_token');
			console.log('Token for API call:', token ? 'Present' : 'Missing');

			if (!token) {
				throw new Error('No authentication token found');
			}

			const created = await api.post<any>('/items/', payload);
			console.log('API response:', created);

			return this.mapApiItemToItem(created);
		} catch (error: any) {
			console.error('Error creating item:', error);
			console.error('Error details:', {
				message: error.message,
				stack: error.stack,
				name: error.name
			});
			return null;
		}
	}

	async getItemById(id: string): Promise<Item | null> {
		try {
			const item = await api.get<any>(`/items/${id}`);
			return this.mapApiItemToItem(item);
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
			const items = await api.get<any[]>(`/items/?${params.toString()}`);
			let mapped = items.map(i => this.mapApiItemToItem(i));
			if (filters.search) {
				const searchTerm = filters.search.toLowerCase();
				mapped = mapped.filter(item => item.title.toLowerCase().includes(searchTerm) || item.description.toLowerCase().includes(searchTerm));
			}
			return mapped;
		} catch (error: any) {
			console.error('Error getting items:', error);
			return [];
		}
	}

	async updateItem(id: string, updates: UpdateItemData): Promise<Item | null> {
		try {
			const updated = await api.patch<any>(`/items/${id}`, {
				...updates,
				location: updates.location
			});
			return this.mapApiItemToItem(updated);
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

			// Only include Authorization header for JWT tokens (not UUID tokens from offline mode)
			if (token) {
				const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
				if (!uuidRegex.test(token)) {
					headers['Authorization'] = `Bearer ${token}`;
				}
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

	private formatPostedAgo(date: Date): string {
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

	private mapApiItemToItem(apiItem: any): Item {
		let images: string[] = [];
		try {
			if (Array.isArray(apiItem.images)) images = apiItem.images;
			else if (typeof apiItem.images === 'string' && apiItem.images.trim()) images = JSON.parse(apiItem.images);
		} catch { }
		const createdAt = apiItem.created_at ? new Date(apiItem.created_at) : new Date();
		return {
			id: apiItem.id,
			userId: apiItem.user_id,
			title: apiItem.title,
			description: apiItem.description ?? '',
			category: apiItem.category ?? '',
			condition: apiItem.condition ?? '',
			images,
			specs: apiItem.specs || {},
			location: apiItem.location || undefined,
			status: apiItem.status,
			views: apiItem.views ?? 0,
			createdAt,
			updatedAt: apiItem.updated_at ? new Date(apiItem.updated_at) : new Date(),
			postedAgo: this.formatPostedAgo(createdAt),
			offersCount: apiItem.offers_count ?? apiItem.offersCount ?? 0,
			owner: (apiItem.owner && apiItem.owner.id)
				? apiItem.owner
				: (apiItem.owner_name && apiItem.owner_id)
					? { id: apiItem.owner_id, name: apiItem.owner_name }
					: undefined,
			latitude: apiItem.latitude,
			longitude: apiItem.longitude
		};
	}
}

export const itemService = new ItemService();