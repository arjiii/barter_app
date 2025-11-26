<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/authStore';
	import { authService } from '$lib/services/authService';
import { navigationConfig } from '$lib/config/navigation';
import { notificationStore } from '$lib/stores/notificationStore';
	import type { NavigationState, NavItem, UserMenu } from '$lib/types/navigation';
	import type { User } from '$lib/types/auth';

	let { children } = $props();
	
	let user: User | null = $state(null);
	let isLoading = $state(true);
	let isAuthenticated = $state(false);

	// Navigation state
	let navState: NavigationState = {
		isOpen: true, // Sidebar open by default on desktop
		mobileMenuOpen: false,
		userMenuOpen: false
	};

	// Sidebar state
	let sidebarOpen = $state(true);
	let isMobile = $state(false);
	// Translate classes for sidebar (toggle both on mobile and desktop)
	let sidebarTranslate = $derived(sidebarOpen ? 'translate-x-0' : '-translate-x-full');

	// Current page
	let currentPath = $derived($page.url.pathname);

let notificationsOpen = $state(false);
let notifications = $derived($state.snapshot(notificationStore));

	/**
	 * Handle navigation item click
	 */
	function handleNavClick(item: NavItem): void {
		if (item.requiresAuth && !isAuthenticated) {
			goto('/sign-in-up');
			return;
		}
		
		// Handle sign out action
		if (item.id === 'signout') {
			handleSignOut();
			return;
		}
		
		if (item.href) {
			goto(item.href);
		}
		
		// Close mobile menu
		navState.mobileMenuOpen = false;
	}

	/**
	 * Handle user menu action
	 */
	function handleUserMenuAction(item: UserMenu): void {
		if (item.action) {
			item.action();
		} else if (item.href) {
			goto(item.href);
		}
		
		navState.userMenuOpen = false;
	}

	/**
	 * Handle sign out
	 */
	async function handleSignOut(): Promise<void> {
		try {
			await authService.signOut();
			authStore.clearAuth();
			await goto('/sign-in-up');
		} catch (error) {
			console.error('Sign out error:', error);
		}
	}

	/**
	 * Toggle sidebar
	 */
	function toggleSidebar(): void {
		sidebarOpen = !sidebarOpen;
		navState.isOpen = sidebarOpen;
	}

	/**
	 * Toggle mobile menu
	 */
	function toggleMobileMenu(): void {
		navState.mobileMenuOpen = !navState.mobileMenuOpen;
	}

	/**
	 * Toggle user menu
	 */
	function toggleUserMenu(): void {
		navState.userMenuOpen = !navState.userMenuOpen;
	}

	/**
	 * Close all menus
	 */
	function closeAllMenus(): void {
		navState.mobileMenuOpen = false;
		navState.userMenuOpen = false;
	}

	/**
	 * Check if mobile
	 */
	function checkMobile(): void {
		isMobile = window.innerWidth < 1024; // lg breakpoint
		if (isMobile) {
			sidebarOpen = false;
			navState.isOpen = false;
		} else {
			sidebarOpen = true;
			navState.isOpen = true;
		}
	}

	// Update user menu actions
	let userMenuItems = $derived(navigationConfig.user.map(item => ({
		...item,
		action: item.id === 'signout' ? handleSignOut : undefined
	})));

	onMount(() => {
		// Subscribe to auth store
		const unsubscribe = authStore.subscribe((authState) => {
			user = authState.user;
			isLoading = authState.isLoading;
			isAuthenticated = authState.isAuthenticated;
		});

		// Initialize auth state
		authStore.initializeAuth();

		// Check initial screen size
		checkMobile();

		// Handle window resize
		const handleResize = () => {
			checkMobile();
		};

		// Close menus when clicking outside
		const handleClickOutside = (event: MouseEvent) => {
			const target = event.target as HTMLElement;
			if (!target.closest('.user-menu') && !target.closest('.mobile-menu') && !target.closest('.sidebar') && !target.closest('.notif-btn') && !target.closest('.notif-panel')) {
				closeAllMenus();
				notificationsOpen = false;
			}
		};

		window.addEventListener('resize', handleResize);
		document.addEventListener('click', handleClickOutside);

		// Cleanup
		return () => {
			unsubscribe();
			window.removeEventListener('resize', handleResize);
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<!-- Sidebar Navigation -->
<div class="flex h-screen bg-[var(--canvas)] text-[var(--text-muted)]">
	<!-- Sidebar -->
	<div class={`sidebar inset-y-0 left-0 z-50 bg-[color:var(--surface-1)] border-r border-[color:var(--border-soft)] shadow-xl transform transition-all duration-300 ease-in-out fixed lg:static ${sidebarOpen ? 'w-72 translate-x-0 pointer-events-auto' : 'w-0 -translate-x-full pointer-events-none'} overflow-hidden`}>
		<!-- Sidebar Header -->
		<div class="flex items-center justify-between min-h-16 px-6 py-2 border-b border-[color:var(--border-soft)] bg-gradient-to-r from-[color:var(--surface-3)] to-[color:var(--surface-2)]">
			<button 
				onclick={() => goto('/')}
				class="flex items-center space-x-3 hover:opacity-90 transition-opacity overflow-hidden text-[var(--text-primary)]"
			>
				<div class="w-10 h-10 bg-white bg-opacity-60 rounded-lg flex items-center justify-center backdrop-blur-sm flex-shrink-0">
					<svg class="h-6 w-6 text-[var(--accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
					</svg>
				</div>
				<div class="hidden lg:block leading-tight">
					<h1 class="text-xl font-bold text-[var(--text-primary)]">Bayanihan Exchange</h1>
					<p class="text-xs text-[var(--text-muted)] mt-0.5">Community Barter App</p>
				</div>
			</button>
			
			<!-- Close button for mobile -->
			<button
				onclick={toggleSidebar}
				class="lg:hidden p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-white hover:bg-opacity-60 transition-colors"
				aria-label="Close sidebar"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
				</svg>
			</button>
		</div>

		<!-- User Profile Section (Top) -->
		{#if isAuthenticated && user}
			<div class="px-4 py-4 border-b border-[color:var(--border-soft)]">
				<div class="flex items-center space-x-3 p-3 rounded-2xl bg-white/80 backdrop-blur">
					<div class="w-12 h-12 bg-gradient-to-r from-[color:var(--accent)] to-[color:var(--accent-strong)] rounded-full flex items-center justify-center shadow-md shadow-[color:var(--accent)]/30 text-white">
						<span class="text-base font-semibold">
							{user.name.charAt(0).toUpperCase()}
						</span>
					</div>
					<div class="flex-1 min-w-0">
						<p class="text-sm font-semibold text-[var(--text-primary)] truncate">{user.name}</p>
						<div class="flex items-center space-x-1">
							<div class="w-2 h-2 bg-green-500 rounded-full"></div>
							<p class="text-xs text-[var(--text-muted)]">Online</p>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Navigation Menu -->
		<nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
			{#each navigationConfig.main as item}
				{#if item.divider}
					<div class="border-t border-gray-200 my-3"></div>
				{:else}
					<button
						onclick={() => handleNavClick(item)}
						class="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group
							{currentPath === item.href 
								? 'bg-[color:var(--surface-2)] text-[var(--text-primary)] border border-[color:var(--border-soft)] shadow-sm' 
								: item.id === 'signout'
									? 'text-[var(--danger)] hover:bg-[color:var(--surface-2)] font-semibold'
									: 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[color:var(--surface-2)]'}"
					>
						<svg class="h-5 w-5 transition-colors
							{currentPath === item.href 
								? 'text-[var(--accent)]' 
								: item.id === 'signout'
									? 'text-[var(--danger)]'
									: 'text-[var(--text-muted)] group-hover:text-[var(--text-primary)]'}" 
							fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon}></path>
						</svg>
						<span class="flex-1 text-left">{item.label}</span>
						{#if item.badge !== undefined && item.badge > 0}
							<span class="bg-[color:var(--accent)] text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center font-semibold">
								{item.badge}
							</span>
						{/if}
					</button>
				{/if}
			{/each}
		</nav>

		<!-- Auth Section (for non-authenticated users) -->
		{#if !isAuthenticated && !isLoading}
			<div class="border-t border-[color:var(--border-soft)] p-6">
				<div class="space-y-3">
					<button
						onclick={() => goto('/sign-in-up')}
						class="w-full text-[var(--text-muted)] hover:text-[var(--text-primary)] px-4 py-2.5 rounded-lg text-sm font-medium transition-colors hover:bg-[color:var(--surface-2)] border border-[color:var(--border-soft)]"
					>
						Sign In
					</button>
					<button
						onclick={() => goto('/sign-in-up')}
						class="w-full btn-primary text-center"
					>
						Sign Up
					</button>
				</div>
			</div>
		{/if}
	</div>

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col overflow-hidden bg-[var(--canvas)]">
		<!-- Top Bar -->
		<header class="bg-[color:var(--surface-1)] border-b border-[color:var(--border-soft)] h-16 flex items-center justify-between px-4 lg:px-6 shadow-sm">
			<!-- Toggle Button -->
			<button
				onclick={toggleSidebar}
				class="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[color:var(--surface-2)] transition-colors"
				aria-label="Toggle sidebar"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
				</svg>
			</button>

			<!-- Page Title -->
			<div class="flex-1 text-center lg:text-left">
				<h2 class="text-lg font-semibold text-[var(--text-primary)]">
					{#if currentPath === '/discovery'}
						Discovery
					{:else if currentPath === '/user-dashboard'}
						Dashboard
					{:else if currentPath === '/my-items'}
						My Items
					{:else if currentPath === '/trades'}
						Trades
					{:else if currentPath === '/messages'}
						Messages
					{:else}
						Bayanihan Exchange
					{/if}
				</h2>
			</div>

			<!-- Right side actions -->
			<div class="flex items-center space-x-2 relative">
				<!-- Search button for mobile -->
				<button class="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[color:var(--surface-2)] transition-colors lg:hidden">
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
					</svg>
				</button>
				
				<!-- Notifications -->
				<div class="relative">
					<button class="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[color:var(--surface-2)] transition-colors relative notif-btn" onclick={() => notificationsOpen = !notificationsOpen} aria-label="Notifications">
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 7h5l-5-5v5z"></path>
						</svg>
						<span class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
					</button>
					{#if notificationsOpen}
						<div class="notif-panel absolute right-0 mt-2 w-80 bg-[color:var(--surface-1)] border border-[color:var(--border-soft)] rounded-2xl shadow-2xl overflow-hidden z-50">
							<div class="px-4 py-3 border-b border-[color:var(--border-soft)] bg-[color:var(--surface-2)] font-semibold text-[var(--text-primary)]">Notifications</div>
							<ul class="max-h-80 overflow-auto divide-y divide-[color:var(--border-soft)]">
								{#each notifications as n}
									<li class="px-4 py-3 hover:bg-[color:var(--surface-2)] transition-colors">
										<p class="text-sm text-[var(--text-primary)]">{n.title}</p>
										<p class="text-xs text-[var(--text-muted)] mt-0.5">{n.time}</p>
									</li>
								{/each}
							</ul>
							<div class="px-4 py-2 bg-[color:var(--surface-2)] text-right">
								<button class="text-sm text-[var(--accent)] hover:text-[var(--accent-strong)] font-medium" onclick={() => notificationsOpen = false}>Close</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</header>

		<!-- Page Content will be inserted here -->
		<main class="flex-1 overflow-auto px-4 lg:px-8 py-6 bg-[var(--canvas)]">
			{@render children?.()}
		</main>
	</div>
</div>

<!-- Mobile Overlay -->
{#if sidebarOpen && isMobile}
	<div 
		class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
		onclick={toggleSidebar}
		role="button"
		tabindex="0"
		aria-label="Close sidebar"
	></div>
{/if}
