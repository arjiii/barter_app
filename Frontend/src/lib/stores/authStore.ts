import { writable } from 'svelte/store';
import type { User, AuthState } from '../types/auth';
import { authService } from '../services/authService';

// Create the auth store
function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		isAuthenticated: false,
		user: null,
		isLoading: false,
		error: null,
	});

	return {
		subscribe,
		
		/**
		 * Get current state synchronously
		 */
		get: () => {
			let currentState: AuthState;
			subscribe(state => currentState = state)();
			return currentState;
		},
		
		/**
		 * Set loading state
		 */
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, isLoading: loading }));
		},
		
		/**
		 * Set error message
		 */
		setError: (error: string | null) => {
			update(state => ({ ...state, error }));
		},
		
		/**
		 * Set user and authentication state
		 */
		setUser: (user: User | null) => {
			update(state => ({
				...state,
				user,
				isAuthenticated: !!user,
				error: null,
			}));
		},
		
		/**
		 * Clear authentication state
		 */
		clearAuth: () => {
			set({
				isAuthenticated: false,
				user: null,
				isLoading: false,
				error: null,
			});
		},
		
		/**
		 * Initialize auth state from stored token
		 */
		async initializeAuth(): Promise<void> {
			update(state => ({ ...state, isLoading: true }));
			
			try {
				const user = await authService.getCurrentUser();
				if (user) {
					update(state => ({
						...state,
						user,
						isAuthenticated: true,
						isLoading: false,
						error: null,
					}));
				} else {
					update(state => ({
						...state,
						isAuthenticated: false,
						user: null,
						isLoading: false,
						error: null,
					}));
				}
			} catch (error) {
				console.error('Auth initialization error:', error);
				update(state => ({
					...state,
					isAuthenticated: false,
					user: null,
					isLoading: false,
					error: 'Failed to initialize authentication',
				}));
			}
		},
	};
}

export const authStore = createAuthStore();
