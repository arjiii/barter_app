import { API_BASE_URL } from '../config/api';
import type { User } from '../types/auth';

class UserService {
  async getUserById(id: string): Promise<User | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/user/${id}`);
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
}

export const userService = new UserService();
export default userService;



