import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { API_BASE_URL } from '../config/api';
import type {
    User,
    AuthResponse,
    LoginCredentials,
    SignUpCredentials
} from '../types/auth';

// Browser-compatible database using localStorage
class BrowserDatabase {
    private getUsers(): User[] {
        const users = localStorage.getItem('bayanihan_users');
        return users ? JSON.parse(users) : [];
    }

    private saveUsers(users: User[]): void {
        localStorage.setItem('bayanihan_users', JSON.stringify(users));
    }

    private getSessions(): Array<{ userId: string; token: string; expiresAt: string }> {
        const sessions = localStorage.getItem('bayanihan_sessions');
        return sessions ? JSON.parse(sessions) : [];
    }

    private saveSessions(sessions: Array<{ userId: string; token: string; expiresAt: string }>): void {
        localStorage.setItem('bayanihan_sessions', JSON.stringify(sessions));
    }

    public createUser(userData: {
        name: string;
        email: string;
        passwordHash: string;
        role?: string;
    }): User | null {
        try {
            const users = this.getUsers();

            // Check if user already exists
            if (users.find(u => u.email === userData.email)) {
                return null;
            }

            const newUser: User = {
                id: uuidv4(),
                email: userData.email,
                name: userData.name,
                isVerified: false,
                role: (userData.role as 'user' | 'admin' | 'moderator') || 'user',
                createdAt: new Date(),
                lastLoginAt: undefined
            };

            // Store password hash separately
            const userWithHash = { ...newUser, passwordHash: userData.passwordHash };
            users.push(userWithHash);
            this.saveUsers(users);

            return newUser;
        } catch (error) {
            console.error('Error creating user:', error);
            return null;
        }
    }

    public getUserByEmail(email: string): User | null {
        try {
            const users = this.getUsers();
            const user = users.find(u => u.email === email);
            return user || null;
        } catch (error) {
            console.error('Error getting user by email:', error);
            return null;
        }
    }

    public getUserById(id: string): User | null {
        try {
            const users = this.getUsers();
            const user = users.find(u => u.id === id);
            return user || null;
        } catch (error) {
            console.error('Error getting user by id:', error);
            return null;
        }
    }

    public getUserPasswordHash(email: string): string | null {
        try {
            const users = this.getUsers();
            const user = users.find(u => u.email === email);
            return (user as User & { passwordHash?: string })?.passwordHash || null;
        } catch (error) {
            console.error('Error getting password hash:', error);
            return null;
        }
    }

    public updateUserLastLogin(userId: string): void {
        try {
            const users = this.getUsers();
            const userIndex = users.findIndex(u => u.id === userId);
            if (userIndex !== -1) {
                users[userIndex].lastLoginAt = new Date();
                this.saveUsers(users);
            }
        } catch (error) {
            console.error('Error updating last login:', error);
        }
    }

    public createSession(userId: string, token: string, expiresAt: Date): void {
        try {
            const sessions = this.getSessions();
            sessions.push({
                userId,
                token,
                expiresAt: expiresAt.toISOString()
            });
            this.saveSessions(sessions);
        } catch (error) {
            console.error('Error creating session:', error);
        }
    }

    public getSessionByToken(token: string): { userId: string; expiresAt: Date } | null {
        try {
            const sessions = this.getSessions();
            const session = sessions.find(s => s.token === token);

            if (!session) return null;

            return {
                userId: session.userId,
                expiresAt: new Date(session.expiresAt)
            };
        } catch (error) {
            console.error('Error getting session:', error);
            return null;
        }
    }

    public deleteSession(token: string): void {
        try {
            const sessions = this.getSessions();
            const filteredSessions = sessions.filter(s => s.token !== token);
            this.saveSessions(filteredSessions);
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    }
}

const database = new BrowserDatabase();

class AuthService {
    /**
     * Sign in user with email and password
     */
    async signIn(credentials: LoginCredentials): Promise<AuthResponse> {
        try {
            // Backend login (OAuth2 password form)
            const res = await fetch(`${API_BASE_URL}/supabase-auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ username: credentials.email, password: credentials.password })
            });
            if (!res.ok) {
                // Fallback to local storage auth if backend rejects
                const localUser = database.getUserByEmail(credentials.email) as (User & { passwordHash?: string }) | null;
                if (localUser && localUser.passwordHash && (await bcrypt.compare(credentials.password, localUser.passwordHash))) {
                    const token = uuidv4();
                    const expiresAt = new Date();
                    expiresAt.setDate(expiresAt.getDate() + 7);
                    database.createSession(localUser.id, token, expiresAt);
                    localStorage.setItem('bayanihan_token', token);
                    database.updateUserLastLogin(localUser.id);
                    return { success: true, user: localUser, token, message: 'Login successful (offline mode)' };
                }
                return { success: false, message: 'Invalid email or password', errors: ['Invalid credentials'] };
            }
            const data = await res.json();
            const { user: apiUser, token } = data;

            // Store the token in localStorage
            localStorage.setItem('bayanihan_token', token);

            const user = {
                id: apiUser.id,
                email: apiUser.email,
                name: apiUser.name,
                isVerified: apiUser.is_verified ?? true,
                role: apiUser.role || 'user',
                createdAt: new Date(),
                lastLoginAt: new Date(),
                location: apiUser.location || undefined,
                latitude: apiUser.latitude,
                longitude: apiUser.longitude
            };

            if (!user) {
                return {
                    success: false,
                    message: 'Invalid email or password',
                    errors: ['Invalid credentials'],
                };
            }


            return {
                success: true,
                user,
                token,
                message: 'Login successful',
            };
        } catch (error) {
            console.error('Sign in error:', error);
            // Network error: attempt local fallback
            const localUser = database.getUserByEmail(credentials.email) as (User & { passwordHash?: string }) | null;
            if (localUser && localUser.passwordHash && (await bcrypt.compare(credentials.password, localUser.passwordHash))) {
                const token = uuidv4();
                const expiresAt = new Date();
                expiresAt.setDate(expiresAt.getDate() + 7);
                database.createSession(localUser.id, token, expiresAt);
                localStorage.setItem('bayanihan_token', token);
                database.updateUserLastLogin(localUser.id);
                return { success: true, user: localUser, token, message: 'Login successful (offline mode)' };
            }
            return { success: false, message: 'An error occurred during login', errors: ['Login failed'] };
        }
    }

    async updateProfile(name: string, location?: string, latitude?: number, longitude?: number): Promise<User | null> {
        try {
            const token = this.getToken();
            if (!token || this.isUuidToken(token)) return null; // UUID tokens are for offline mode only
            const res = await fetch(`${API_BASE_URL}/supabase-auth/profile`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify({
                    name,
                    location: location || '',
                    latitude,
                    longitude
                })
            });
            if (!res.ok) return null;
            const apiUser = await res.json();
            const user: User = {
                id: apiUser.id,
                email: apiUser.email,
                name: apiUser.name,
                isVerified: true,
                role: 'user',
                createdAt: new Date(),
                lastLoginAt: new Date(),
                location: apiUser.location || undefined,
                latitude: apiUser.latitude,
                longitude: apiUser.longitude
            };
            return user;
        } catch (e) {
            console.error('Update profile error:', e);
            return null;
        }
    }

    async changePassword(oldPassword: string, newPassword: string): Promise<boolean> {
        try {
            const token = this.getToken();
            if (!token || this.isUuidToken(token)) return false; // UUID tokens are for offline mode only
            const res = await fetch(`${API_BASE_URL}/supabase-auth/change-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
            });
            return res.ok;
        } catch (e) {
            console.error('Change password error:', e);
            return false;
        }
    }

    /**
     * Request password reset - sends email with reset link
     */
    async requestPasswordReset(email: string): Promise<{ success: boolean; message: string }> {
        try {
            const res = await fetch(`${API_BASE_URL}/supabase-auth/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            return { success: res.ok, message: data.message || 'Password reset email sent' };
        } catch (e) {
            console.error('Request password reset error:', e);
            return { success: false, message: 'Failed to send password reset email' };
        }
    }

    /**
     * Reset password using token from email
     */
    async resetPassword(token: string, newPassword: string): Promise<{ success: boolean; message: string }> {
        try {
            const res = await fetch(`${API_BASE_URL}/supabase-auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password: newPassword })
            });
            const data = await res.json();
            if (!res.ok) {
                return { success: false, message: data.detail || data.message || 'Password reset failed' };
            }
            return { success: true, message: data.message || 'Password reset successfully' };
        } catch (e) {
            console.error('Reset password error:', e);
            return { success: false, message: 'Failed to reset password' };
        }
    }

    /**
     * Verify email using OTP
     */
    async verifyEmail(email: string, otp: string): Promise<{ success: boolean; message: string; token?: string; user?: User }> {
        try {
            const res = await fetch(`${API_BASE_URL}/supabase-auth/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp })
            });
            const data = await res.json();
            if (!res.ok) {
                return { success: false, message: data.detail || data.message || 'Email verification failed' };
            }

            if (data.token && data.user) {
                localStorage.setItem('bayanihan_token', data.token);
                const user = {
                    id: data.user.id,
                    email: data.user.email,
                    name: data.user.name,
                    isVerified: true,
                    role: data.user.role || 'user',
                    createdAt: new Date(),
                    location: data.user.location || undefined,
                    latitude: data.user.latitude,
                    longitude: data.user.longitude
                };
                return { success: true, message: data.message || 'Email verified successfully', token: data.token, user };
            }

            return { success: true, message: data.message || 'Email verified successfully' };
        } catch (e) {
            console.error('Verify email error:', e);
            return { success: false, message: 'Failed to verify email' };
        }
    }

    /**
     * Resend verification email
     */
    async resendVerificationEmail(email: string): Promise<{ success: boolean; message: string }> {
        try {
            const res = await fetch(`${API_BASE_URL}/supabase-auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            return { success: res.ok, message: data.message || 'Verification email sent' };
        } catch (e) {
            console.error('Resend verification email error:', e);
            return { success: false, message: 'Failed to send verification email' };
        }
    }
    /**
     * Sign up new user
     */
    async signUp(credentials: SignUpCredentials): Promise<AuthResponse> {
        try {
            const res = await fetch(`${API_BASE_URL}/supabase-auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: credentials.name,
                    email: credentials.email,
                    password: credentials.password,
                    location: credentials.location,
                    latitude: credentials.latitude,
                    longitude: credentials.longitude,
                    verification_method: credentials.verificationMethod || 'email'
                })
            });
            if (!res.ok) {
                // Try to extract error message from backend
                let errorMessage = 'Registration failed';
                try {
                    const errorData = await res.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch {
                    try {
                        const errorText = await res.text();
                        // Try to parse as JSON if it looks like JSON
                        if (errorText.trim().startsWith('{')) {
                            const errorData = JSON.parse(errorText);
                            errorMessage = errorData.detail || errorData.message || errorMessage;
                        } else {
                            errorMessage = errorText || errorMessage;
                        }
                    } catch {
                        // Use default error message
                    }
                }

                // For validation errors (400), return the error message directly
                if (res.status === 400) {
                    return { success: false, message: errorMessage, errors: [errorMessage] };
                }

                // For other errors, try local fallback
                const saltRounds = 12;
                const passwordHash = await bcrypt.hash(credentials.password, saltRounds);
                const user = database.createUser({ name: credentials.name, email: credentials.email, passwordHash, role: 'user' });
                if (!user) {
                    return { success: false, message: errorMessage, errors: [errorMessage] };
                }
                const token = uuidv4();
                const expiresAt = new Date();
                expiresAt.setDate(expiresAt.getDate() + 7);
                database.createSession(user.id, token, expiresAt);
                localStorage.setItem('bayanihan_token', token);
                return { success: true, user, token, message: 'Registration successful (offline mode)' };
            }

            const data = await res.json();

            // If backend returns token (legacy or immediate login), use it
            if (data.token && data.user) {
                const { user: apiUser, token } = data;
                const user = {
                    id: apiUser.id,
                    email: apiUser.email,
                    name: apiUser.name,
                    isVerified: true,
                    role: 'user' as const,
                    createdAt: new Date(),
                    location: apiUser.location || undefined
                };
                localStorage.setItem('bayanihan_token', token);

                return {
                    success: true,
                    user,
                    token,
                    message: 'Registration successful',
                };
            }

            // New flow: No token yet, just success message
            return {
                success: true,
                message: data.message || 'Verification code sent',
            };

        } catch (error) {
            console.error('Sign up error:', error);
            // Network error: create local account as fallback
            const saltRounds = 12;
            const passwordHash = await bcrypt.hash(credentials.password, saltRounds);
            const user = database.createUser({ name: credentials.name, email: credentials.email, passwordHash, role: 'user' });
            if (!user) {
                return { success: false, message: 'An error occurred during registration', errors: ['Registration failed'] };
            }
            const token = uuidv4();
            const expiresAt = new Date();
            expiresAt.setDate(expiresAt.getDate() + 7);
            database.createSession(user.id, token, expiresAt);
            localStorage.setItem('bayanihan_token', token);
            return { success: true, user, token, message: 'Registration successful (offline mode)' };
        }
    }

    /**
     * Check if token is a UUID (offline mode) or JWT (backend mode)
     */
    isUuidToken(token: string): boolean {
        // UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        return uuidRegex.test(token);
    }

    /**
     * Get current user from token
     */
    async getCurrentUser(): Promise<User | null> {
        try {
            const token = localStorage.getItem('bayanihan_token');
            if (!token) return null;

            // If token is a UUID (offline mode), only check local session
            if (this.isUuidToken(token)) {
                const session = database.getSessionByToken(token);
                if (!session || session.expiresAt < new Date()) {
                    localStorage.removeItem('bayanihan_token');
                    return null;
                }
                const user = database.getUserById(session.userId);
                return user;
            }

            // Token is a JWT, try backend first
            const res = await fetch(`${API_BASE_URL}/supabase-auth/me`, { headers: { Authorization: `Bearer ${token}` } });
            if (!res.ok) {
                // JWT token is invalid/expired, clear it
                localStorage.removeItem('bayanihan_token');
                return null;
            }
            const apiUser = await res.json();
            return {
                id: apiUser.id,
                email: apiUser.email,
                name: apiUser.name,
                isVerified: apiUser.is_verified ?? true,
                role: apiUser.role || 'user',
                createdAt: new Date(),
                location: apiUser.location || undefined,
                latitude: apiUser.latitude,
                longitude: apiUser.longitude
            };
        } catch (error) {
            console.error('Get current user error:', error);
            // On network error, if token is UUID, try local session
            const token = localStorage.getItem('bayanihan_token');
            if (token && this.isUuidToken(token)) {
                const session = database.getSessionByToken(token);
                if (session && session.expiresAt >= new Date()) {
                    const user = database.getUserById(session.userId);
                    return user;
                }
            }
            return null;
        }
    }

    /**
     * Create a test user for development
     */
    async createTestUser(): Promise<AuthResponse> {
        try {
            const testUser = {
                name: 'Test User',
                email: 'test@example.com',
                password: 'password123'
            };

            // Try to create user in backend first
            try {
                const res = await fetch(`${API_BASE_URL}/supabase-auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testUser)
                });

                if (res.ok) {
                    const data = await res.json();
                    const { user: apiUser, token } = data;
                    const user = {
                        id: apiUser.id,
                        email: apiUser.email,
                        name: apiUser.name,
                        isVerified: apiUser.is_verified ?? true,
                        role: apiUser.role || 'user',
                        createdAt: new Date(),
                        lastLoginAt: new Date()
                    };

                    localStorage.setItem('bayanihan_token', token);

                    return {
                        success: true,
                        user,
                        token,
                        message: 'Test user created successfully',
                    };
                } else {
                    // User might already exist, try to login
                    const loginRes = await fetch(`${API_BASE_URL}/supabase-auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: new URLSearchParams({ username: testUser.email, password: testUser.password })
                    });

                    if (loginRes.ok) {
                        const data = await loginRes.json();
                        const { user: apiUser, token } = data;
                        const user = {
                            id: apiUser.id,
                            email: apiUser.email,
                            name: apiUser.name,
                            isVerified: apiUser.is_verified ?? true,
                            role: apiUser.role || 'user',
                            createdAt: new Date(),
                            lastLoginAt: new Date()
                        };

                        localStorage.setItem('bayanihan_token', token);

                        return {
                            success: true,
                            user,
                            token,
                            message: 'Test user login successful',
                        };
                    }
                }
            } catch (backendError) {
                console.warn('Backend auth failed, falling back to local storage:', backendError);
            }

            // Fallback to local storage if backend fails
            const existingUser = database.getUserByEmail(testUser.email);
            if (existingUser) {
                // Create session for existing user
                const token = uuidv4();
                const expiresAt = new Date();
                expiresAt.setDate(expiresAt.getDate() + 7);

                database.createSession(existingUser.id, token, expiresAt);
                localStorage.setItem('bayanihan_token', token);

                return {
                    success: true,
                    user: existingUser,
                    token,
                    message: 'Test user login successful',
                };
            }

            // Create new test user in local storage
            const saltRounds = 12;
            const passwordHash = await bcrypt.hash(testUser.password, saltRounds);

            const user = database.createUser({
                name: testUser.name,
                email: testUser.email,
                passwordHash,
                role: 'user'
            });

            if (!user) {
                return {
                    success: false,
                    message: 'Failed to create test user',
                    errors: ['Test user creation failed'],
                };
            }

            // Create session token
            const token = uuidv4();
            const expiresAt = new Date();
            expiresAt.setDate(expiresAt.getDate() + 7);

            database.createSession(user.id, token, expiresAt);
            localStorage.setItem('bayanihan_token', token);

            return {
                success: true,
                user,
                token,
                message: 'Test user created successfully',
            };
        } catch (error) {
            console.error('Create test user error:', error);
            return {
                success: false,
                message: 'An error occurred creating test user',
                errors: ['Test user creation failed'],
            };
        }
    }

    /**
     * Sign out user
     */
    async signOut(): Promise<void> {
        try {
            const token = localStorage.getItem('bayanihan_token');
        } catch (error) {
            console.error('Sign out error:', error);
        } finally {
            // Always clear local storage
            localStorage.removeItem('bayanihan_token');
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        return !!localStorage.getItem('bayanihan_token');
    }

    /**
     * Get stored token
     */
    getToken(): string | null {
        return localStorage.getItem('bayanihan_token');
    }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
