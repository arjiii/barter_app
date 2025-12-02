<script lang="ts">
	import { onMount } from 'svelte';
	import { adminService } from '$lib/services/adminService';

	let stats = $state({
		users: 0,
		items: 0,
		trades: 0
	});
	let isLoading = $state(true);

	onMount(async () => {
		try {
			stats = await adminService.getStats();
		} catch (error) {
			console.error('Failed to load stats:', error);
		} finally {
			isLoading = false;
		}
	});
</script>

<div class="mx-auto max-w-7xl">
	<h2 class="mb-8 text-2xl font-bold text-gray-900">Dashboard Overview</h2>

	{#if isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
			{#each Array(3) as _}
				<div
					class="h-32 animate-pulse rounded-2xl border border-gray-100 bg-white p-6 shadow-sm"
				></div>
			{/each}
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
			<!-- Users Card -->
			<div class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
				<div class="mb-4 flex items-center justify-between">
					<div class="rounded-xl bg-blue-50 p-3 text-blue-600">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
							></path>
						</svg>
					</div>
					<span class="text-sm font-medium text-gray-500">Total Users</span>
				</div>
				<div class="flex items-baseline">
					<h3 class="text-3xl font-bold text-gray-900">{stats.users}</h3>
				</div>
			</div>

			<!-- Items Card -->
			<div class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
				<div class="mb-4 flex items-center justify-between">
					<div class="rounded-xl bg-orange-50 p-3 text-orange-600">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
							></path>
						</svg>
					</div>
					<span class="text-sm font-medium text-gray-500">Total Items</span>
				</div>
				<div class="flex items-baseline">
					<h3 class="text-3xl font-bold text-gray-900">{stats.items}</h3>
				</div>
			</div>

			<!-- Trades Card -->
			<div class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
				<div class="mb-4 flex items-center justify-between">
					<div class="rounded-xl bg-green-50 p-3 text-green-600">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
							></path>
						</svg>
					</div>
					<span class="text-sm font-medium text-gray-500">Total Trades</span>
				</div>
				<div class="flex items-baseline">
					<h3 class="text-3xl font-bold text-gray-900">{stats.trades}</h3>
				</div>
			</div>
		</div>
	{/if}
</div>
