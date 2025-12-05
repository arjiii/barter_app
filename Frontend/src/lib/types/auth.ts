// Authentication Types for Bayanihan Exchange

export interface User {
	id: string;
	email: string;
	name: string;
	isVerified: boolean;
	role: 'user' | 'admin' | 'moderator';
	createdAt: Date;
	lastLoginAt?: Date;
	location?: string;
	latitude?: number;
	longitude?: number;
}

export interface AuthResponse {
	success: boolean;
	user?: User;
	token?: string;
	message?: string;
	errors?: string[];
}

export interface LoginCredentials {
	email: string;
	password: string;
	rememberMe?: boolean;
}

export interface SignUpCredentials {
	name: string;
	email: string;
	password: string;
	confirmPassword: string;
	location?: string;
	latitude?: number;
	longitude?: number;
	verificationMethod?: 'email' | 'admin';
}

export interface AuthState {
	isAuthenticated: boolean;
	user: User | null;
	isLoading: boolean;
	error: string | null;
}

export interface FormState {
	isSignUp: boolean;
	isLoading: boolean;
	errors: ValidationErrors;
}

export interface ValidationErrors {
	email?: string;
	password?: string;
	name?: string;
	confirmPassword?: string;
	general?: string;
}

export type AuthMode = 'signin' | 'signup';

export interface SocialLoginProvider {
	name: 'google' | 'apple' | 'facebook';
	icon: string;
	label: string;
}
