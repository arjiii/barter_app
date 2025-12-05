<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE_URL } from '$lib/config/api';

	let requests: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);

	onMount(async () => {
		await loadRequests();
	});

	async function loadRequests() {
		isLoading = true;
		error = null;
		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/admin/support-requests`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				throw new Error('Failed to fetch support requests');
			}

			requests = await res.json();
		} catch (err: any) {
			error = err.message || 'Failed to fetch support requests';
			requests = [];
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<div class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-900">Support Requests</h1>
				<p class="mt-2 text-sm text-gray-600">Manage user support requests</p>
			</div>
			<button
				class="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all hover:bg-orange-600 hover:shadow-xl hover:shadow-orange-500/40"
				onclick={() => loadRequests()}
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
					/>
				</svg>
				Refresh
			</button>
		</div>

		{#if error}
			<div class="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
		{/if}

		<div class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5">
			{#if isLoading}
				<div class="p-12 text-center">
					<div
						class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-orange-500 border-r-transparent"
					></div>
					<p class="mt-4 text-sm text-gray-500">Loading support requests...</p>
				</div>
			{:else if requests.length === 0}
				<div class="p-12 text-center">
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
							d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
						/>
					</svg>
					<p class="mt-4 text-sm font-medium text-gray-900">No support requests yet</p>
					<p class="mt-1 text-sm text-gray-500">Support requests will appear here</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Subject</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>User</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Type</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Status</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Date</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-right text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Actions</th
								>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each requests as request}
								<tr class="hover:bg-gray-50">
									<td class="px-6 py-4">
										<div class="text-sm font-medium text-gray-900">{request.subject}</div>
										{#if request.message}
											<div class="text-xs text-gray-500">{request.message.slice(0, 50)}...</div>
										{/if}
									</td>
									<td class="px-6 py-4">
										<div class="text-sm text-gray-900">{request.user_name}</div>
									</td>
									<td class="px-6 py-4">
										<span
											class="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800"
										>
											{request.type}
										</span>
									</td>
									<td class="px-6 py-4">
										<span
											class={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
												request.status === 'resolved'
													? 'bg-green-100 text-green-800'
													: request.status === 'rejected'
														? 'bg-red-100 text-red-800'
														: 'bg-yellow-100 text-yellow-800'
											}`}
										>
											{request.status.charAt(0).toUpperCase() + request.status.slice(1)}
										</span>
									</td>
									<td class="px-6 py-4 text-sm text-gray-500">
										{new Date(request.created_at).toLocaleDateString()}
									</td>
									<td class="px-6 py-4 text-right">
										<button class="text-sm font-medium text-orange-600 hover:text-orange-700">
											View
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
</div>
