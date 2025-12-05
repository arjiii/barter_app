import { API_BASE_URL } from '../config/api';

class SupportService {
    private getHeaders() {
        const token = localStorage.getItem('bayanihan_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    async createRequest(data: { type: string; subject: string; message: string }) {
        const response = await fetch(`${API_BASE_URL}/support/requests`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to create support request');
        return response.json();
    }

    async getRequests() {
        const response = await fetch(`${API_BASE_URL}/support/requests`, {
            headers: this.getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch support requests');
        return response.json();
    }
}

export const supportService = new SupportService();
