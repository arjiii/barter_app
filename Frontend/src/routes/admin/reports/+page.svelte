<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE_URL } from '$lib/config/api';

	let reports: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let filterStatus = $state('all');

	onMount(async () => {
		await loadReports();
	});

	async function loadReports() {
		isLoading = true;
		error = null;
		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/admin/user-reports`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				throw new Error('Failed to fetch user reports');
			}

			reports = await res.json();
		} catch (err: any) {
			error = err.message || 'Failed to fetch user reports';
			reports = [];
		} finally {
			isLoading = false;
		}
	}

	async function handleResolve(reportId: string) {
		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/admin/user-reports/${reportId}/resolve`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				throw new Error('Failed to resolve report');
			}

			// Update local state
			reports = reports.map((r) => (r.id === reportId ? { ...r, status: 'resolved' } : r));
		} catch (err: any) {
			alert('Failed to resolve report: ' + err.message);
		}
	}

	const filteredReports = $derived(
		filterStatus === 'all' ? reports : reports.filter((r) => r.status === filterStatus)
	);

	const stats = $derived({
		total: reports.length,
		pending: reports.filter((r) => r.status === 'pending').length,
		resolved: reports.filter((r) => r.status === 'resolved').length
	});
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<div class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-900">User Reports</h1>
				<p class="mt-2 text-sm text-gray-600">Manage user reports and moderation</p>
			</div>
			<button
				class="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all hover:bg-orange-600 hover:shadow-xl hover:shadow-orange-500/40"
				onclick={() => loadReports()}
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

		<!-- Stats Cards -->
		<div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-blue-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 w-fit rounded-lg bg-blue-100 p-2">
						<svg
							class="h-5 w-5 text-blue-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.total}</div>
					<div class="text-sm text-gray-600">Total Reports</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-yellow-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 w-fit rounded-lg bg-yellow-100 p-2">
						<svg
							class="h-5 w-5 text-yellow-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.pending}</div>
					<div class="text-sm text-gray-600">Pending</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-green-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 w-fit rounded-lg bg-green-100 p-2">
						<svg
							class="h-5 w-5 text-green-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.resolved}</div>
					<div class="text-sm text-gray-600">Resolved</div>
				</div>
			</div>
		</div>

		{#if error}
			<div class="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
		{/if}

		<!-- Filter -->
		<div class="mb-6">
			<select
				bind:value={filterStatus}
				class="rounded-lg border-0 px-3 py-2 text-sm font-medium ring-1 ring-gray-300 focus:ring-2 focus:ring-orange-500"
			>
				<option value="all">All Status</option>
				<option value="pending">Pending</option>
				<option value="resolved">Resolved</option>
			</select>
		</div>

		<!-- Table -->
		<div class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5">
			{#if isLoading}
				<div class="p-12 text-center">
					<div
						class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-orange-500 border-r-transparent"
					></div>
					<p class="mt-4 text-sm text-gray-500">Loading reports...</p>
				</div>
			{:else if filteredReports.length === 0}
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
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					<p class="mt-4 text-sm font-medium text-gray-900">No reports found</p>
					<p class="mt-1 text-sm text-gray-500">There are no user reports at this time</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Reporter</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Reported User</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Reason</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Description</th
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
							{#each filteredReports as report}
								<tr class="group transition-colors hover:bg-gray-50">
									<td class="px-6 py-4">
										<div class="text-sm font-medium text-gray-900">{report.reporter_name}</div>
										<div class="text-xs text-gray-500">{report.reporter_email}</div>
									</td>
									<td class="px-6 py-4">
										<div class="text-sm font-medium text-gray-900">{report.reported_user_name}</div>
										<div class="text-xs text-gray-500">{report.reported_user_email}</div>
									</td>
									<td class="px-6 py-4">
										<span
											class="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800"
										>
											{report.reason}
										</span>
									</td>
									<td class="px-6 py-4">
										<div class="max-w-xs truncate text-sm text-gray-600">{report.description}</div>
									</td>
									<td class="px-6 py-4">
										<span
											class={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
												report.status === 'resolved'
													? 'bg-green-100 text-green-800'
													: 'bg-yellow-100 text-yellow-800'
											}`}
										>
											<span
												class={`h-1.5 w-1.5 rounded-full ${
													report.status === 'resolved' ? 'bg-green-400' : 'bg-yellow-400'
												}`}
											></span>
											{report.status.charAt(0).toUpperCase() + report.status.slice(1)}
										</span>
									</td>
									<td class="px-6 py-4 text-sm text-gray-500">
										{new Date(report.created_at).toLocaleDateString()}
									</td>
									<td class="px-6 py-4 text-right">
										{#if report.status === 'pending'}
											<button
												onclick={() => handleResolve(report.id)}
												class="inline-flex items-center gap-1.5 rounded-lg bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-green-600 hover:shadow-lg hover:shadow-green-500/30"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M5 13l4 4L19 7"
													/>
												</svg>
												Resolve
											</button>
										{:else}
											<span class="text-xs text-gray-400">Resolved</span>
										{/if}
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
