<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { API_BASE_URL } from '$lib/config/api';

	let stats = $state({
		total_users: 0,
		total_items: 0,
		total_trades: 0,
		pending_approvals: 0
	});

	let recentActivity: any[] = $state([]);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const token = localStorage.getItem('bayanihan_token');
			if (!token) {
				await goto('/admin/login');
				return;
			}

			// Fetch stats
			const statsRes = await fetch(`${API_BASE_URL}/admin/stats`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (statsRes.ok) {
				stats = await statsRes.json();
			}

			// Fetch recent activity
			const activityRes = await fetch(`${API_BASE_URL}/admin/recent-activity`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (activityRes.ok) {
				recentActivity = await activityRes.json();
			}
		} catch (error) {
			console.error('Failed to load admin data:', error);
		} finally {
			isLoading = false;
		}
	});

	function getTimeAgo(timestamp: string) {
		const now = new Date();
		const then = new Date(timestamp);
		const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

		if (seconds < 60) return 'just now';
		if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
		return `${Math.floor(seconds / 86400)} days ago`;
	}

	function getActivityIcon(type: string) {
		if (type === 'user_registered') return 'user';
		if (type === 'item_listed') return 'item';
		if (type === 'trade_completed') return 'trade';
		return 'default';
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold tracking-tight text-gray-900">Admin Dashboard</h1>
			<p class="mt-2 text-sm text-gray-600">Manage your exchange platform</p>
		</div>

		{#if isLoading}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
				{#each Array(3) as _}
					<div class="h-40 animate-pulse rounded-2xl bg-white shadow"></div>
				{/each}
			</div>
		{:else}
			<!-- Stats Grid -->
			<div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
				<!-- Total Users -->
				<div
					class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
				>
					<div
						class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-blue-50 opacity-50"
					></div>
					<div class="relative">
						<div class="mb-4 flex items-center justify-between">
							<div class="rounded-xl bg-blue-100 p-3 text-blue-600">
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
									/>
								</svg>
							</div>
							<span class="text-xs font-medium text-green-600">Active</span>
						</div>
						<h3 class="text-3xl font-bold text-gray-900">{stats.total_users}</h3>
						<p class="mt-1 text-sm font-medium text-gray-500">Total Users</p>
					</div>
				</div>

				<!-- Total Items -->
				<div
					class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
				>
					<div
						class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-orange-50 opacity-50"
					></div>
					<div class="relative">
						<div class="mb-4 flex items-center justify-between">
							<div class="rounded-xl bg-orange-100 p-3 text-orange-600">
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
									/>
								</svg>
							</div>
							<span class="text-xs font-medium text-green-600">Listed</span>
						</div>
						<h3 class="text-3xl font-bold text-gray-900">{stats.total_items}</h3>
						<p class="mt-1 text-sm font-medium text-gray-500">Total Items</p>
					</div>
				</div>

				<!-- Total Trades -->
				<div
					class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
				>
					<div
						class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-green-50 opacity-50"
					></div>
					<div class="relative">
						<div class="mb-4 flex items-center justify-between">
							<div class="rounded-xl bg-green-100 p-3 text-green-600">
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
									/>
								</svg>
							</div>
							<span class="text-xs font-medium text-green-600">Completed</span>
						</div>
						<h3 class="text-3xl font-bold text-gray-900">{stats.total_trades}</h3>
						<p class="mt-1 text-sm font-medium text-gray-500">Total Trades</p>
					</div>
				</div>

				<!-- Pending Approvals -->
				<div
					class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
				>
					<div
						class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-yellow-50 opacity-50"
					></div>
					<div class="relative">
						<div class="mb-4 flex items-center justify-between">
							<div class="rounded-xl bg-yellow-100 p-3 text-yellow-600">
								<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</div>
							{#if stats.pending_approvals > 0}
								<span class="text-xs font-medium text-red-600">Needs Action</span>
							{:else}
								<span class="text-xs font-medium text-gray-400">None</span>
							{/if}
						</div>
						<h3 class="text-3xl font-bold text-gray-900">{stats.pending_approvals}</h3>
						<p class="mt-1 text-sm font-medium text-gray-500">Pending Approvals</p>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<!-- Recent Activity -->
				<div
					class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5 lg:col-span-2"
				>
					<div class="border-b border-gray-200 p-6">
						<div class="flex items-center justify-between">
							<div>
								<h2 class="text-lg font-bold text-gray-900">Recent Activity</h2>
								<p class="mt-1 text-sm text-gray-500">Latest platform activities</p>
							</div>
							<button class="text-sm font-medium text-orange-600 hover:text-orange-700">
								View All →
							</button>
						</div>
					</div>
					<div class="p-6">
						{#if recentActivity.length > 0}
							<div class="space-y-4">
								{#each recentActivity as activity}
									<div
										class="flex items-start gap-4 rounded-lg border border-gray-100 p-4 transition-all hover:border-gray-200 hover:bg-gray-50"
									>
										<div
											class={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${
												activity.type === 'user_registered'
													? 'bg-blue-100 text-blue-600'
													: activity.type === 'item_listed'
														? 'bg-orange-100 text-orange-600'
														: 'bg-green-100 text-green-600'
											}`}
										>
											{#if activity.type === 'user_registered'}
												<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
													/>
												</svg>
											{:else if activity.type === 'item_listed'}
												<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
													/>
												</svg>
											{:else}
												<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
													/>
												</svg>
											{/if}
										</div>
										<div class="min-w-0 flex-1">
											<p class="text-sm text-gray-900">{activity.description}</p>
											<p class="mt-1 text-xs text-gray-500">{getTimeAgo(activity.timestamp)}</p>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="py-12 text-center">
								<svg
									class="mx-auto h-12 w-12 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13 10V3L4 14h7v7l9-11h-7z"
									/>
								</svg>
								<p class="mt-4 text-sm text-gray-500">No recent activity</p>
							</div>
						{/if}
					</div>
				</div>

				<!-- Quick Actions -->
				<div class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5">
					<div class="border-b border-gray-200 p-6">
						<h2 class="text-lg font-bold text-gray-900">Quick Actions</h2>
						<p class="mt-1 text-sm text-gray-500">Common tasks</p>
					</div>
					<div class="p-6">
						<div class="space-y-3">
							<button
								onclick={() => goto('/admin/users')}
								class="group flex w-full items-center justify-between rounded-xl border border-gray-100 bg-gradient-to-r from-blue-50 to-transparent p-4 text-left transition-all hover:border-blue-200 hover:shadow-md"
							>
								<div class="flex items-center gap-3">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600 transition-transform group-hover:scale-110"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
											/>
										</svg>
									</div>
									<div>
										<p class="font-medium text-gray-900">Manage Users</p>
										<p class="text-xs text-gray-500">View and manage users</p>
									</div>
								</div>
								<svg
									class="h-5 w-5 text-gray-400 transition-transform group-hover:translate-x-1"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 5l7 7-7 7"
									/>
								</svg>
							</button>

							<button
								onclick={() => goto('/admin/items')}
								class="group flex w-full items-center justify-between rounded-xl border border-gray-100 bg-gradient-to-r from-orange-50 to-transparent p-4 text-left transition-all hover:border-orange-200 hover:shadow-md"
							>
								<div class="flex items-center gap-3">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100 text-orange-600 transition-transform group-hover:scale-110"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
											/>
										</svg>
									</div>
									<div>
										<p class="font-medium text-gray-900">Manage Items</p>
										<p class="text-xs text-gray-500">Review listed items</p>
									</div>
								</div>
								<svg
									class="h-5 w-5 text-gray-400 transition-transform group-hover:translate-x-1"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 5l7 7-7 7"
									/>
								</svg>
							</button>

							<button
								onclick={() => goto('/admin/trades')}
								class="group flex w-full items-center justify-between rounded-xl border border-gray-100 bg-gradient-to-r from-green-50 to-transparent p-4 text-left transition-all hover:border-green-200 hover:shadow-md"
							>
								<div class="flex items-center gap-3">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 text-green-600 transition-transform group-hover:scale-110"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
											/>
										</svg>
									</div>
									<div>
										<p class="font-medium text-gray-900">View Trades</p>
										<p class="text-xs text-gray-500">Monitor transactions</p>
									</div>
								</div>
								<svg
									class="h-5 w-5 text-gray-400 transition-transform group-hover:translate-x-1"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 5l7 7-7 7"
									/>
								</svg>
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
