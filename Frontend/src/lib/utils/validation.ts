import type { LoginCredentials, SignUpCredentials } from '../types/auth';

export interface ValidationErrors {
	email?: string;
	password?: string;
	name?: string;
	confirmPassword?: string;
}

/**
 * Validate email format
 */
export function validateEmail(email: string): string | null {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	
	if (!email.trim()) {
		return 'Email is required';
	}
	
	if (!emailRegex.test(email)) {
		return 'Please enter a valid email address';
	}
	
	return null;
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): string | null {
	if (!password) {
		return 'Password is required';
	}
	// No minimum length requirement - backend handles all password validation
	return null;
}

/**
 * Validate name
 */
export function validateName(name: string): string | null {
	if (!name.trim()) {
		return 'Full name is required';
	}
	
	if (name.trim().length < 2) {
		return 'Name must be at least 2 characters long';
	}
	
	return null;
}

/**
 * Validate login credentials
 */
export function validateLoginCredentials(credentials: LoginCredentials): ValidationErrors {
	const errors: ValidationErrors = {};
	
	const emailError = validateEmail(credentials.email);
	if (emailError) {
		errors.email = emailError;
	}
	
	const passwordError = validatePassword(credentials.password);
	if (passwordError) {
		errors.password = passwordError;
	}
	
	return errors;
}

/**
 * Validate sign up credentials
 */
export function validateSignUpCredentials(credentials: SignUpCredentials): ValidationErrors {
	const errors: ValidationErrors = {};
	
	const nameError = validateName(credentials.name);
	if (nameError) {
		errors.name = nameError;
	}
	
	const emailError = validateEmail(credentials.email);
	if (emailError) {
		errors.email = emailError;
	}
	
	const passwordError = validatePassword(credentials.password);
	if (passwordError) {
		errors.password = passwordError;
	}
	
	if (credentials.password !== credentials.confirmPassword) {
		errors.confirmPassword = 'Passwords do not match';
	}
	
	return errors;
}

/**
 * Check if validation errors exist
 */
export function hasValidationErrors(errors: ValidationErrors): boolean {
	return Object.keys(errors).length > 0;
}
