import { API_BASE_URL } from '../config/api';
import { authStore } from '../stores/authStore';

class AdminService {
    private getHeaders() {
        const token = localStorage.getItem('bayanihan_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    async getStats() {
        const response = await fetch(`${API_BASE_URL}/admin/stats`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch stats');
        return response.json();
    }

    async getUsers(skip = 0, limit = 20) {
        const response = await fetch(`${API_BASE_URL}/admin/users?skip=${skip}&limit=${limit}`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch users');
        return response.json();
    }

    async deleteUser(userId: string) {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to delete user');
        return response.json();
    }

    async verifyUser(userId: string) {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/verify`, {
            method: 'PUT',
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to verify user');
        return response.json();
    }

    async updateUserRole(userId: string, role: string) {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/role`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ role })
        });
        if (!response.ok) throw new Error('Failed to update user role');
        return response.json();
    }

    async createUser(userData: any) {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create user');
        }
        return response.json();
    }

    async resetUserPassword(userId: string, password: string) {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/password`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ password })
        });
        if (!response.ok) throw new Error('Failed to reset user password');
        return response.json();
    }

    async getSupportRequests() {
        const response = await fetch(`${API_BASE_URL}/admin/requests`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch support requests');
        return response.json();
    }

    async updateRequestStatus(requestId: string, status: string) {
        const response = await fetch(`${API_BASE_URL}/admin/requests/${requestId}/status?status=${status}`, {
            method: 'PUT',
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to update request status');
        return response.json();
    }

    async getItems(skip = 0, limit = 20) {
        const response = await fetch(`${API_BASE_URL}/admin/items?skip=${skip}&limit=${limit}`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch items');
        return response.json();
    }

    async deleteItem(itemId: string) {
        const response = await fetch(`${API_BASE_URL}/admin/items/${itemId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to delete item');
        return response.json();
    }

    async getTrades(skip = 0, limit = 20) {
        const response = await fetch(`${API_BASE_URL}/admin/trades?skip=${skip}&limit=${limit}`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch trades');
        return response.json();
    }

    async deleteTrade(tradeId: string) {
        const response = await fetch(`${API_BASE_URL}/admin/trades/${tradeId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to delete trade');
        return response.json();
    }

    async updateItemStatus(itemId: string, status: string) {
        const response = await fetch(`${API_BASE_URL}/admin/items/${itemId}/status`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error('Failed to update item status');
        return response.json();
    }

    async updateTradeStatus(tradeId: string, status: string) {
        const response = await fetch(`${API_BASE_URL}/admin/trades/${tradeId}/status`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error('Failed to update trade status');
        return response.json();
    }
}

export const adminService = new AdminService();
