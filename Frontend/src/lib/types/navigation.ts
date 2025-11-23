// Navigation Types for Bayanihan Exchange

export interface NavItem {
	id: string;
	label: string;
	href?: string;
	icon: string;
	badge?: number;
	children?: NavItem[];
	requiresAuth?: boolean;
	roles?: string[];
	divider?: boolean;
}

export interface UserMenu {
	id: string;
	label: string;
	href?: string;
	icon: string;
	action?: () => void;
	divider?: boolean;
}

export interface NavigationState {
	isOpen: boolean;
	mobileMenuOpen: boolean;
	userMenuOpen: boolean;
}

export type NavSection = 'main' | 'user' | 'footer';

export interface NavConfig {
	main: NavItem[];
	user: UserMenu[];
	footer: NavItem[];
}
