import { API_BASE_URL } from '../utils/config';
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
}

export const adminService = new AdminService();
