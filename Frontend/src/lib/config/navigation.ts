import type { NavConfig } from '../types/navigation';

export const navigationConfig: NavConfig = {
	main: [
		{
			id: 'discovery',
			label: 'Discovery',
			href: '/discovery',
			icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
			requiresAuth: false
		},
		{
			// Dashboard removed per request
			id: 'my-items',
			label: 'My Items',
			href: '/my-items',
			icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
			requiresAuth: true
		},
		{
			id: 'trades',
			label: 'Trades',
			href: '/trades',
			icon: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4',
			requiresAuth: true,
			badge: 0
		},
		{
			id: 'messages',
			label: 'Messages',
			href: '/messages',
			icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
			requiresAuth: true,
			badge: 0
		},
		{
			id: 'profile',
			label: 'My Profile',
			href: '/profile',
			icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
			requiresAuth: true
		},
		{
			id: 'settings',
			label: 'Settings',
			href: '/settings',
			icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
			requiresAuth: true
		},
		{
			id: 'divider',
			label: '',
			icon: '',
			divider: true
		},
		{
			id: 'help',
			label: 'Help & Support',
			href: '/help',
			icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
			requiresAuth: false
		},
		{
			id: 'signout',
			label: 'Sign Out',
			href: '#',
			icon: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1',
			requiresAuth: true
		}
	],
	user: [],
	footer: [
		{
			id: 'about',
			label: 'About',
			href: '/about',
			icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
			requiresAuth: false
		},
		{
			id: 'privacy',
			label: 'Privacy',
			href: '/privacy',
			icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
			requiresAuth: false
		},
		{
			id: 'terms',
			label: 'Terms',
			href: '/terms',
			icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
			requiresAuth: false
		}
	]
};
