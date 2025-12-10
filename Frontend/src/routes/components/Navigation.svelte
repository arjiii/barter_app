<script lang="ts">
	import { onMount } from 'svelte';
	import { goto, invalidateAll } from '$app/navigation';
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
	let notifications = $derived($notificationStore);

	/**
	 * Handle navigation item click
	 */
	async function handleNavClick(item: NavItem): Promise<void> {
		if (item.requiresAuth && !isAuthenticated) {
			await goto('/sign-in-up');
			return;
		}

		// Handle sign out action
		if (item.id === 'signout') {
			handleSignOut();
			return;
		}

		if (item.href) {
			// Invalidate all data to force fresh fetch
			await invalidateAll();
			await goto(item.href, { replaceState: false, invalidateAll: true });
		}

		// Close mobile menu
		navState.mobileMenuOpen = false;
	}

	/**
	 * Handle user menu action
	 */
	async function handleUserMenuAction(item: UserMenu): Promise<void> {
		if (item.action) {
			item.action();
		} else if (item.href) {
			await invalidateAll();
			await goto(item.href, { replaceState: false, invalidateAll: true });
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
	let userMenuItems = $derived(
		navigationConfig.user.map((item) => ({
			...item,
			action: item.id === 'signout' ? handleSignOut : undefined
		}))
	);

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
			if (
				!target.closest('.user-menu') &&
				!target.closest('.mobile-menu') &&
				!target.closest('.sidebar') &&
				!target.closest('.notif-btn') &&
				!target.closest('.notif-panel')
			) {
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
	<div
		class={`sidebar fixed inset-y-0 left-0 z-50 transform border-r border-[color:var(--border-soft)] bg-[color:var(--surface-1)] shadow-xl transition-all duration-300 ease-in-out lg:static ${sidebarOpen ? 'pointer-events-auto w-72 translate-x-0' : 'pointer-events-none w-0 -translate-x-full'} overflow-hidden`}
	>
		<!-- Sidebar Header -->
		<div
			class="flex min-h-16 items-center justify-between border-b border-[color:var(--border-soft)] bg-gradient-to-r from-[color:var(--surface-3)] to-[color:var(--surface-2)] px-6 py-2"
		>
			<button
				onclick={() => goto('/')}
				class="flex items-center space-x-3 overflow-hidden text-[var(--text-primary)] transition-opacity hover:opacity-90"
			>
				<div
					class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white bg-opacity-60 backdrop-blur-sm"
				>
					<svg
						class="h-6 w-6 text-[var(--accent)]"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
						></path>
					</svg>
				</div>
				<div class="hidden leading-tight lg:block">
					<h1 class="text-xl font-bold text-[var(--text-primary)]">Bayanihan Exchange</h1>
					<p class="mt-0.5 text-xs text-[var(--text-muted)]">Community Barter App</p>
				</div>
			</button>

			<!-- Close button for mobile -->
			<button
				onclick={toggleSidebar}
				class="rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-white hover:bg-opacity-60 hover:text-[var(--text-primary)] lg:hidden"
				aria-label="Close sidebar"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					></path>
				</svg>
			</button>
		</div>

		<!-- User Profile Section (Top) -->
		{#if isAuthenticated && user}
			<div class="border-b border-[color:var(--border-soft)] px-4 py-4">
				<button
					onclick={() => user?.id && goto(`/user/${user.id}`)}
					class="flex w-full items-center space-x-3 rounded-2xl bg-white/80 p-3 text-left backdrop-blur transition-all hover:bg-white hover:shadow-sm"
				>
					<div
						class="shadow-[color:var(--accent)]/30 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[color:var(--accent)] to-[color:var(--accent-strong)] text-white shadow-md"
					>
						<span class="text-base font-semibold">
							{user.name.charAt(0).toUpperCase()}
						</span>
					</div>
					<div class="min-w-0 flex-1">
						<p class="truncate text-sm font-semibold text-[var(--text-primary)]">{user.name}</p>
						<div class="flex items-center space-x-1">
							<div class="h-2 w-2 rounded-full bg-green-500"></div>
							<p class="text-xs text-[var(--text-muted)]">View Profile</p>
						</div>
					</div>
				</button>
			</div>
		{/if}

		<!-- Navigation Menu -->
		<nav class="flex-1 space-y-1 overflow-y-auto px-4 py-6">
			{#each navigationConfig.main as item}
				{#if item.divider}
					<div class="my-3 border-t border-gray-200"></div>
				{:else}
					<button
						onclick={() => handleNavClick(item)}
						class="group flex w-full items-center space-x-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200
							{currentPath === item.href
							? 'border border-[color:var(--border-soft)] bg-[color:var(--surface-2)] text-[var(--text-primary)] shadow-sm'
							: item.id === 'signout'
								? 'font-semibold text-[var(--danger)] hover:bg-[color:var(--surface-2)]'
								: 'text-[var(--text-muted)] hover:bg-[color:var(--surface-2)] hover:text-[var(--text-primary)]'}"
					>
						<svg
							class="h-5 w-5 transition-colors
							{currentPath === item.href
								? 'text-[var(--accent)]'
								: item.id === 'signout'
									? 'text-[var(--danger)]'
									: 'text-[var(--text-muted)] group-hover:text-[var(--text-primary)]'}"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon}
							></path>
						</svg>
						<span class="flex-1 text-left">{item.label}</span>
						{#if item.badge !== undefined && item.badge > 0}
							<span
								class="min-w-[20px] rounded-full bg-[color:var(--accent)] px-2 py-1 text-center text-xs font-semibold text-white"
							>
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
						class="w-full rounded-lg border border-[color:var(--border-soft)] px-4 py-2.5 text-sm font-medium text-[var(--text-muted)] transition-colors hover:bg-[color:var(--surface-2)] hover:text-[var(--text-primary)]"
					>
						Sign In
					</button>
					<button onclick={() => goto('/sign-in-up')} class="btn-primary w-full text-center">
						Sign Up
					</button>
				</div>
			</div>
		{/if}
	</div>

	<!-- Main Content Area -->
	<div class="flex flex-1 flex-col overflow-hidden bg-[var(--canvas)]">
		<!-- Top Bar -->
		<header
			class="flex h-16 items-center justify-between border-b border-[color:var(--border-soft)] bg-[color:var(--surface-1)] px-4 shadow-sm lg:px-6"
		>
			<!-- Toggle Button -->
			<button
				onclick={toggleSidebar}
				class="rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-[color:var(--surface-2)] hover:text-[var(--text-primary)]"
				aria-label="Toggle sidebar"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h16M4 18h16"
					></path>
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
			<div class="relative flex items-center space-x-2">
				<!-- Search button for mobile -->
				<button
					class="rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-[color:var(--surface-2)] hover:text-[var(--text-primary)] lg:hidden"
					aria-label="Search"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						></path>
					</svg>
				</button>

				<!-- Notifications -->
				<div class="relative">
					<button
						class="notif-btn relative rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-[color:var(--surface-2)] hover:text-[var(--text-primary)]"
						onclick={() => (notificationsOpen = !notificationsOpen)}
						aria-label="Notifications"
					>
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 7h5l-5-5v5z"
							></path>
						</svg>
						<span class="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-red-500"></span>
					</button>
					{#if notificationsOpen}
						<div
							class="notif-panel absolute right-0 z-50 mt-2 w-80 overflow-hidden rounded-2xl border border-[color:var(--border-soft)] bg-[color:var(--surface-1)] shadow-2xl"
						>
							<div
								class="border-b border-[color:var(--border-soft)] bg-[color:var(--surface-2)] px-4 py-3 font-semibold text-[var(--text-primary)]"
							>
								Notifications
							</div>
							<ul class="max-h-80 divide-y divide-[color:var(--border-soft)] overflow-auto">
								{#each notifications as n}
									<li class="px-4 py-3 transition-colors hover:bg-[color:var(--surface-2)]">
										<p class="text-sm text-[var(--text-primary)]">{n.title}</p>
										<p class="mt-0.5 text-xs text-[var(--text-muted)]">{n.time}</p>
									</li>
								{/each}
							</ul>
							<div class="bg-[color:var(--surface-2)] px-4 py-2 text-right">
								<button
									class="text-sm font-medium text-[var(--accent)] hover:text-[var(--accent-strong)]"
									onclick={() => (notificationsOpen = false)}>Close</button
								>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</header>

		<!-- Page Content will be inserted here -->
		<main class="flex-1 overflow-auto bg-[var(--canvas)] px-4 py-6 lg:px-8">
			{@render children?.()}
		</main>
	</div>
</div>

<!-- Mobile Overlay -->
{#if sidebarOpen && isMobile}
	<div
		class="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity duration-300 lg:hidden"
		onclick={toggleSidebar}
		role="button"
		tabindex="0"
		aria-label="Close sidebar"
		onkeydown={(e) => e.key === 'Escape' && toggleSidebar()}
	></div>
{/if}
