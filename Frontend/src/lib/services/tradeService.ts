import type { Trade, CreateTradeData, UpdateTradeData, TradeFilters } from '../types/trades';
import { api, API_BASE_URL } from '../config/api';

/**
 * Check if token is a UUID (offline mode) or JWT (backend mode)
 */
function isUuidToken(token: string): boolean {
	// UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
	const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
	return uuidRegex.test(token);
}

function getAuthHeaders(): Record<string, string> {
	const token = localStorage.getItem('bayanihan_token');
	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};

	// Only include Authorization header for JWT tokens (not UUID tokens from offline mode)
	if (token && !isUuidToken(token)) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	return headers;
}

class TradeService {
	// Trades CRUD operations
	async createTrade(tradeData: CreateTradeData): Promise<Trade | null> {
		try {
			const created = await api.post<Trade>('/trades/', tradeData);
			return created;
		} catch (error) {
			console.error('Error creating trade:', error);
			return null;
		}
	}

	async getTradeById(id: string): Promise<Trade | null> {
		try {
			const trade = await api.get<Trade>(`/trades/${id}`);
			return trade;
		} catch (error) {
			console.error('Error getting trade:', error);
			return null;
		}
	}

	async getTrades(filters: TradeFilters = {}): Promise<Trade[]> {
		try {
			const params = new URLSearchParams();
			if (filters.userId) params.set('user_id', filters.userId);
			const trades = await api.get<Trade[]>(`/trades/?${params.toString()}`);

			// Client-side filtering if needed (backend handles user_id)
			if (filters.status) return trades.filter((t) => t.status === filters.status);

			return trades;
		} catch (error) {
			console.error('Error getting trades:', error);
			return [];
		}
	}

	async updateTrade(id: string, updates: UpdateTradeData): Promise<Trade | null> {
		try {
			const updated = await fetch(`${API_BASE_URL}/trades/${id}`, {
				method: 'PATCH',
				headers: getAuthHeaders(),
				body: JSON.stringify(updates)
			});
			if (!updated.ok) {
				throw new Error(`HTTP ${updated.status}`);
			}
			const data = await updated.json();
			return data;
		} catch (error) {
			console.error('Error updating trade:', error);
			return null;
		}
	}

	async deleteTrade(id: string): Promise<boolean> {
		try {
			const response = await fetch(`${API_BASE_URL}/trades/${id}`, {
				method: 'DELETE',
				headers: getAuthHeaders()
			});
			return response.ok;
		} catch (error) {
			console.error('Error deleting trade:', error);
			return false;
		}
	}

	async acceptTrade(tradeId: string): Promise<boolean> {
		try {
			// Accepting a trade automatically moves it to 'active' status
			const updated = await this.updateTrade(tradeId, { status: 'active' });
			return updated !== null;
		} catch (error) {
			console.error('Error accepting trade:', error);
			return false;
		}
	}

	async rejectTrade(tradeId: string): Promise<boolean> {
		try {
			const updated = await this.updateTrade(tradeId, { status: 'rejected' });
			return updated !== null;
		} catch (error) {
			console.error('Error rejecting trade:', error);
			return false;
		}
	}

	async completeTrade(tradeId: string): Promise<boolean> {
		try {
			const updated = await this.updateTrade(tradeId, { status: 'completed' });
			return updated !== null;
		} catch (error) {
			console.error('Error completing trade:', error);
			return false;
		}
	}

	// ⭐ New: Rate Trade function
	async rateTrade(
		tradeId: string,
		rateeUserId: string,
		score: number,
		feedback?: string
	): Promise<boolean> {
		try {
			const res = await fetch(`${API_BASE_URL}/trades/${tradeId}/ratings`, {
				method: 'POST',
				headers: getAuthHeaders(),
				body: JSON.stringify({
					ratee_user_id: rateeUserId,
					score,
					feedback
				})
			});
			return res.ok;
		} catch (e) {
			console.error('Error rating trade:', e);
			return false;
		}
	}

	async getUserRatings(userId: string): Promise<any[]> {
		try {
			const ratings = await api.get<any[]>(`/trades/ratings/user/${userId}`);
			return ratings;
		} catch (error) {
			console.error('Error getting user ratings:', error);
			return [];
		}
	}

	async checkUserRated(tradeId: string, userId: string): Promise<boolean> {
		try {
			const ratings = await api.get<any[]>(`/trades/${tradeId}/ratings`);
			return ratings.some(r => r.rater_user_id === userId);
		} catch (error) {
			console.error('Error checking if user rated:', error);
			return false;
		}
	}
}

export const tradeService = new TradeService();
