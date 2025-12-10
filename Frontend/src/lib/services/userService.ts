import { API_BASE_URL } from '../config/api';
import type { User } from '../types/auth';

class UserService {
  async getUserById(id: string): Promise<User | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/supabase-auth/user/${id}`);
      if (!res.ok) return null;
      const data = await res.json();
      const user: User = {
        id: data.id,
        name: data.name,
        email: data.email,
        isVerified: true,
        role: 'user',
        createdAt: new Date(),
      };
      return user;
    } catch (e) {
      console.error('getUserById error:', e);
      return null;
    }
  }

  async reportUser(reportedUserId: string, reason: string, description: string): Promise<void> {
    const token = localStorage.getItem('bayanihan_token');
    if (!token) throw new Error('You must be logged in to report a user');

    const res = await fetch(`${API_BASE_URL}/reports/user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        reported_user_id: reportedUserId,
        reason,
        description
      })
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to report user');
    }
  }
}

export const userService = new UserService();
export default userService;



