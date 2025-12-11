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

	async function handleSuspend(userId: string) {
		if (!confirm('Are you sure you want to suspend this user?')) return;
		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/admin/users/${userId}/suspend`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				throw new Error('Failed to suspend user');
			}

			// Update reports to reflect user status change
			reports = reports.map((r) =>
				r.reported_user_id === userId ? { ...r, reported_user_status: 'suspended' } : r
			);
			alert('User suspended successfully');
		} catch (err: any) {
			alert('Failed to suspend user: ' + err.message);
		}
	}

	const filteredReports = $derived(
		filterStatus === 'all' ? reports : reports.filter((r) => r.status === filterStatus)
	);
</script>

<div class="p-6">
	<h1 class="mb-6 text-2xl font-bold text-gray-800">User Reports</h1>

	<!-- Filters -->
	<div class="mb-6 flex gap-2">
		<button
			class="rounded-lg px-4 py-2 text-sm font-medium transition-colors {filterStatus === 'all'
				? 'bg-blue-600 text-white'
				: 'bg-white text-gray-600 hover:bg-gray-50'}"
			onclick={() => (filterStatus = 'all')}
		>
			All
		</button>
		<button
			class="rounded-lg px-4 py-2 text-sm font-medium transition-colors {filterStatus === 'pending'
				? 'bg-yellow-500 text-white'
				: 'bg-white text-gray-600 hover:bg-gray-50'}"
			onclick={() => (filterStatus = 'pending')}
		>
			Pending
		</button>
		<button
			class="rounded-lg px-4 py-2 text-sm font-medium transition-colors {filterStatus === 'resolved'
				? 'bg-green-600 text-white'
				: 'bg-white text-gray-600 hover:bg-gray-50'}"
			onclick={() => (filterStatus = 'resolved')}
		>
			Resolved
		</button>
	</div>

	<!-- Table -->
	<div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
		<table class="w-full text-left text-sm text-gray-500">
			<thead class="bg-gray-50 text-xs uppercase text-gray-700">
				<tr>
					<th class="px-6 py-3">Status</th>
					<th class="px-6 py-3">Reported User</th>
					<th class="px-6 py-3">Reason</th>
					<th class="px-6 py-3">Description</th>
					<th class="px-6 py-3">Reporter</th>
					<th class="px-6 py-3">Date</th>
					<th class="px-6 py-3 text-right">Actions</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-gray-200">
				{#each filteredReports as report (report.id)}
					<tr class="hover:bg-gray-50">
						<td class="px-6 py-4">
							<span
								class="inline-flex rounded-full px-2 py-1 text-xs font-semibold leading-5 {report.status ===
								'resolved'
									? 'bg-green-100 text-green-800'
									: 'bg-yellow-100 text-yellow-800'}"
							>
								{report.status}
							</span>
						</td>
						<td class="px-6 py-4">
							<div class="font-medium text-gray-900">{report.reported_user_name || 'Unknown'}</div>
							<div class="text-xs text-gray-500">{report.reported_user_email || 'No email'}</div>
						</td>
						<td class="px-6 py-4">
							<span class="font-medium capitalize text-gray-700">{report.reason}</span>
						</td>
						<td class="px-6 py-4">
							<p class="max-w-xs truncate" title={report.description}>{report.description}</p>
						</td>
						<td class="px-6 py-4">
							<div class="font-medium text-gray-900">{report.reporter_name || 'Anonymous'}</div>
						</td>
						<td class="px-6 py-4">
							{new Date(report.created_at).toLocaleDateString()}
						</td>
						<td class="px-6 py-4 text-right">
							<div class="flex flex-col items-end gap-2">
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
								{/if}

								{#if report.reported_user_status !== 'suspended'}
									<button
										onclick={() => handleSuspend(report.reported_user_id)}
										class="inline-flex items-center gap-1.5 rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/30"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
											/>
										</svg>
										Suspend
									</button>
								{:else}
									<span
										class="inline-flex items-center gap-1.5 rounded bg-red-100 px-2 py-1 text-xs font-medium text-red-800"
									>
										Suspended
									</span>
								{/if}

								<a
									href={`/user/${report.reported_user_id}`}
									target="_blank"
									class="inline-flex items-center gap-1.5 rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-700 transition-all hover:bg-gray-200"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
										/>
									</svg>
									View Profile
								</a>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
