<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { onMount } from 'svelte';

	let isLoading = $state(true);

	onMount(() => {
		authStore.initializeAuth();
		const authState = authStore.get();

		if (!authState.isAuthenticated || !authState.user || authState.user.role !== 'admin') {
			goto('/discovery');
		} else {
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
		}
	];
</script>

{#if isLoading}
	<div class="flex min-h-screen items-center justify-center bg-gray-100">
		<div class="h-12 w-12 animate-spin rounded-full border-b-2 border-[#1f1b17]"></div>
	</div>
{:else}
	<div class="flex min-h-screen bg-gray-100 font-['Inter',sans-serif]">
		<!-- Sidebar -->
		<aside class="hidden w-64 flex-shrink-0 bg-[#1f1b17] text-white md:block">
			<div class="p-6">
				<h1 class="text-xl font-bold tracking-tight">Admin Panel</h1>
				<p class="mt-1 text-xs text-gray-400">Bayanihan Exchange</p>
			</div>

			<nav class="mt-6 space-y-2 px-4">
				{#each links as link}
					<a
						href={link.href}
						class={`flex items-center rounded-xl px-4 py-3 transition-colors ${$page.url.pathname === link.href ? 'bg-[#ff6d3f] text-white' : 'text-gray-400 hover:bg-white/10 hover:text-white'}`}
					>
						<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={link.icon}
							></path>
						</svg>
						{link.label}
					</a>
				{/each}
			</nav>

			<div class="absolute bottom-0 w-64 border-t border-white/10 p-4">
				<button
					onclick={() => goto('/discovery')}
					class="flex w-full items-center px-4 py-3 text-gray-400 transition-colors hover:text-white"
				>
					<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
						></path>
					</svg>
					Exit Admin
				</button>
			</div>
		</aside>

		<!-- Mobile Header -->
		<div
			class="fixed left-0 right-0 top-0 z-50 flex items-center justify-between bg-[#1f1b17] px-4 py-3 text-white md:hidden"
		>
			<span class="font-bold">Admin Panel</span>
			<!-- Mobile menu button could go here -->
		</div>

		<!-- Main Content -->
		<main class="mt-12 flex-1 overflow-y-auto p-8 md:mt-0">
			<slot />
		</main>
	</div>
{/if}
