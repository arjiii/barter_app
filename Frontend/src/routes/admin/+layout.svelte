<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { onMount } from 'svelte';

	let isLoading = $state(true);

	let { children } = $props();

	let isLoginPage = $derived($page.url.pathname === '/admin/login');

	onMount(() => {
		if (isLoginPage) {
			isLoading = false;
			return;
		}

		authStore.initializeAuth();
		const authState = authStore.get();

		if (!authState.isAuthenticated || !authState.user || authState.user.role !== 'admin') {
			goto('/admin/login');
			isLoading = false;
		}
	});

	const links = [
		{
			href: '/admin',
			label: 'Dashboard',
			icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z'
		},
		{
			href: '/admin/users',
			label: 'Users',
			icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z'
		},
		{
			href: '/admin/items',
			label: 'Items',
			icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
		},
		{
			href: '/admin/trades',
			label: 'Trades',
			icon: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4'
		},
		{
			href: '/admin/requests',
			label: 'Support Requests',
			icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		{
			href: '/admin/reports',
			label: 'User Reports',
			icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z'
		}
	];
</script>

{#if isLoginPage}
	{@render children()}
{:else if isLoading}
	<div class="flex min-h-screen items-center justify-center bg-gray-100">
		<div class="h-12 w-12 animate-spin rounded-full border-b-2 border-[#1f1b17]"></div>
	</div>
{:else}
	<div class="flex h-screen overflow-hidden bg-gray-50 font-['Inter',sans-serif]">
		<!-- Sidebar -->
		<aside class="hidden w-72 flex-shrink-0 bg-[#1f1b17] text-white md:block">
			<div class="flex h-full flex-col">
				<div class="p-6">
					<div class="flex items-center space-x-3">
						<div
							class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#ff6d3f] to-[#ff8f6b] shadow-lg"
						>
							<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
								></path>
							</svg>
						</div>
						<div>
							<h1 class="text-lg font-bold tracking-tight">Admin Panel</h1>
							<p class="text-xs text-gray-400">Bayanihan Exchange</p>
						</div>
					</div>
				</div>

				<nav class="flex-1 space-y-1 overflow-y-auto px-4 py-4">
					{#each links as link}
						<a
							href={link.href}
							class={`group flex items-center rounded-xl px-4 py-3.5 text-sm font-medium transition-all duration-200 ${
								$page.url.pathname === link.href
									? 'bg-white/10 text-white shadow-sm ring-1 ring-white/10'
									: 'text-gray-400 hover:bg-white/5 hover:text-white'
							}`}
						>
							<svg
								class={`mr-3 h-5 w-5 transition-colors ${
									$page.url.pathname === link.href
										? 'text-[#ff6d3f]'
										: 'text-gray-500 group-hover:text-gray-300'
								}`}
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={link.icon}
								></path>
							</svg>
							{link.label}
						</a>
					{/each}
				</nav>

				<div class="border-t border-white/10 p-4">
					<button
						onclick={() => goto('/discovery')}
						class="flex w-full items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-gray-300 transition-all hover:bg-white/10 hover:text-white"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							></path>
						</svg>
						Exit to App
					</button>
				</div>
			</div>
		</aside>

		<!-- Main Content Wrapper -->
		<div class="flex flex-1 flex-col overflow-hidden">
			<!-- Mobile Header -->
			<div
				class="flex items-center justify-between bg-[#1f1b17] px-4 py-3 text-white shadow-md md:hidden"
			>
				<div class="flex items-center space-x-2">
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#ff6d3f]">
						<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
							></path>
						</svg>
					</div>
					<span class="font-bold">Admin Panel</span>
				</div>
				<!-- Mobile menu button could go here -->
			</div>

			<!-- Main Content -->
			<main class="flex-1 overflow-y-auto p-8">
				{@render children()}
			</main>
		</div>
	</div>
{/if}
