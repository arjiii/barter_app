<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/authStore';
	import { goto } from '$app/navigation';
	import { API_BASE_URL } from '$lib/config/api';

	let users: any[] = [];
	let isLoading = true;
	let error: string | null = null;
	let searchQuery = '';
	let filterStatus = 'all';

	onMount(async () => {
		const user = authStore.get().user;
		if (!user) {
			await goto('/sign-in-up');
			return;
		}

		await fetchUsers();
	});

	async function fetchUsers() {
		isLoading = true;
		error = null;
		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/admin/users`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				if (res.status === 401 || res.status === 403) {
					error = 'Unauthorized. You need admin privileges.';
				} else {
					error = 'Failed to fetch users.';
				}
				return;
			}

			users = await res.json();
		} catch (e) {
			console.error(e);
			error = 'An error occurred.';
		} finally {
			isLoading = false;
		}
	}

	async function handleAction(
		userId: string,
		action: 'approve' | 'suspend' | 'restore' | 'delete',
		type: string = 'user'
	) {
		if (!confirm(`Are you sure you want to ${action} this user?`)) return;

		try {
			const token = localStorage.getItem('bayanihan_token');
			let url = `${API_BASE_URL}/admin/users/${userId}`;
			let method = 'POST';

			if (action === 'approve') url += '/approve';
			else if (action === 'suspend') url += '/suspend';
			else if (action === 'restore') url += '/restore';
			else if (action === 'delete') {
				method = 'DELETE';
				if (type === 'pending') url += '?type=pending';
			}

			const res = await fetch(url, {
				method,
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (res.ok) {
				await fetchUsers();
			} else {
				alert('Action failed');
			}
		} catch (e) {
			console.error(e);
			alert('An error occurred');
		}
	}

	$: filteredUsers = users.filter((user) => {
		const matchesSearch =
			user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			user.email.toLowerCase().includes(searchQuery.toLowerCase());
		const matchesFilter =
			filterStatus === 'all' ||
			(filterStatus === 'active' && user.status === 'active') ||
			(filterStatus === 'suspended' && user.status === 'suspended') ||
			(filterStatus === 'pending' && user.verification_status === 'Pending Approval');
		return matchesSearch && matchesFilter;
	});

	$: stats = {
		total: users.length,
		active: users.filter((u) => u.status === 'active').length,
		suspended: users.filter((u) => u.status === 'suspended').length,
		pending: users.filter((u) => u.verification_status === 'Pending Approval').length
	};
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-900">User Management</h1>
				<p class="mt-2 text-sm text-gray-600">Manage and monitor all platform users</p>
			</div>
			<button
				class="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all hover:bg-orange-600 hover:shadow-xl hover:shadow-orange-500/40"
				onclick={() => fetchUsers()}
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
		<div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-blue-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 flex items-center justify-between">
						<div class="rounded-lg bg-blue-100 p-2">
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
									d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
								/>
							</svg>
						</div>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.total}</div>
					<div class="text-sm text-gray-600">Total Users</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-green-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 flex items-center justify-between">
						<div class="rounded-lg bg-green-100 p-2">
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
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.active}</div>
					<div class="text-sm text-gray-600">Active</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-red-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 flex items-center justify-between">
						<div class="rounded-lg bg-red-100 p-2">
							<svg
								class="h-5 w-5 text-red-600"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
								/>
							</svg>
						</div>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.suspended}</div>
					<div class="text-sm text-gray-600">Suspended</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-yellow-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 flex items-center justify-between">
						<div class="rounded-lg bg-yellow-100 p-2">
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
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.pending}</div>
					<div class="text-sm text-gray-600">Pending Approval</div>
				</div>
			</div>
		</div>

		<!-- Filters -->
		<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div class="relative max-w-md flex-1">
				<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
					<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
				</div>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search users by name or email..."
					class="block w-full rounded-lg border-0 py-2.5 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-orange-500 sm:text-sm"
				/>
			</div>
			<div class="flex gap-2">
				<button
					onclick={() => (filterStatus = 'all')}
					class={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
						filterStatus === 'all'
							? 'bg-orange-500 text-white shadow-lg shadow-orange-500/30'
							: 'bg-white text-gray-700 ring-1 ring-gray-300 hover:bg-gray-50'
					}`}
				>
					All
				</button>
				<button
					onclick={() => (filterStatus = 'active')}
					class={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
						filterStatus === 'active'
							? 'bg-green-500 text-white shadow-lg shadow-green-500/30'
							: 'bg-white text-gray-700 ring-1 ring-gray-300 hover:bg-gray-50'
					}`}
				>
					Active
				</button>
				<button
					onclick={() => (filterStatus = 'suspended')}
					class={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
						filterStatus === 'suspended'
							? 'bg-red-500 text-white shadow-lg shadow-red-500/30'
							: 'bg-white text-gray-700 ring-1 ring-gray-300 hover:bg-gray-50'
					}`}
				>
					Suspended
				</button>
				<button
					onclick={() => (filterStatus = 'pending')}
					class={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
						filterStatus === 'pending'
							? 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/30'
							: 'bg-white text-gray-700 ring-1 ring-gray-300 hover:bg-gray-50'
					}`}
				>
					Pending
				</button>
			</div>
		</div>

		{#if error}
			<div class="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-800">
				<div class="flex items-start gap-3">
					<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
							clip-rule="evenodd"
						/>
					</svg>
					<p class="font-medium">{error}</p>
				</div>
			</div>
		{/if}

		<!-- Table -->
		<div class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5">
			{#if isLoading}
				<div class="p-12 text-center">
					<div
						class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-orange-500 border-r-transparent"
					></div>
					<p class="mt-4 text-sm text-gray-500">Loading users...</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>User</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Location</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Verification</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Status</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-right text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Actions</th
								>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each filteredUsers as user}
								<tr class="transition-colors hover:bg-gray-50">
									<td class="whitespace-nowrap px-6 py-4">
										<div class="flex items-center gap-3">
											<div
												class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-pink-500 text-sm font-semibold text-white"
											>
												{user.name.charAt(0).toUpperCase()}
											</div>
											<div>
												<div class="font-medium text-gray-900">{user.name}</div>
												<div class="text-sm text-gray-500">{user.email}</div>
											</div>
										</div>
									</td>
									<td class="whitespace-nowrap px-6 py-4">
										{#if user.location}
											<div class="flex items-center gap-2 text-sm text-gray-900">
												<svg
													class="h-4 w-4 text-gray-400"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
													/>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
													/>
												</svg>
												{user.location}
											</div>
										{:else}
											<span class="text-sm text-gray-400">—</span>
										{/if}
									</td>
									<td class="whitespace-nowrap px-6 py-4">
										{#if user.verification_status === 'Verified'}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800"
											>
												<svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
													<path
														fill-rule="evenodd"
														d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
														clip-rule="evenodd"
													/>
												</svg>
												Verified
											</span>
										{:else if user.verification_status === 'Pending Approval'}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-800"
											>
												<svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
													<path
														fill-rule="evenodd"
														d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
														clip-rule="evenodd"
													/>
												</svg>
												Pending Approval
											</span>
										{:else}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-800"
											>
												Unverified
											</span>
										{/if}
									</td>
									<td class="whitespace-nowrap px-6 py-4">
										{#if user.status === 'active'}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800"
											>
												<span class="h-1.5 w-1.5 rounded-full bg-green-500"></span>
												Active
											</span>
										{:else if user.status === 'suspended'}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-800"
											>
												<span class="h-1.5 w-1.5 rounded-full bg-red-500"></span>
												Suspended
											</span>
										{:else if user.status === 'Pending'}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-800"
											>
												<span class="h-1.5 w-1.5 rounded-full bg-yellow-500"></span>
												Pending
											</span>
										{:else}
											<span
												class="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-800"
											>
												{user.status}
											</span>
										{/if}
									</td>
									<td class="whitespace-nowrap px-6 py-4 text-right">
										<div class="flex items-center justify-end gap-2">
											{#if user.verification_status === 'Pending Approval'}
												<button
													class="inline-flex items-center gap-1.5 rounded-lg bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-green-600 hover:shadow-lg hover:shadow-green-500/30"
													onclick={() => handleAction(user.id, 'approve', 'pending')}
												>
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M5 13l4 4L19 7"
														/>
													</svg>
													Approve
												</button>
												<button
													class="inline-flex items-center gap-1.5 rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/30"
													onclick={() => handleAction(user.id, 'delete', 'pending')}
												>
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M6 18L18 6M6 6l12 12"
														/>
													</svg>
													Reject
												</button>
											{:else}
												{#if user.status === 'suspended'}
													<button
														class="inline-flex items-center gap-1.5 rounded-lg bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-green-600 hover:shadow-lg hover:shadow-green-500/30"
														onclick={() => handleAction(user.id, 'restore')}
													>
														<svg
															class="h-4 w-4"
															fill="none"
															stroke="currentColor"
															viewBox="0 0 24 24"
														>
															<path
																stroke-linecap="round"
																stroke-linejoin="round"
																stroke-width="2"
																d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
															/>
														</svg>
														Restore
													</button>
												{:else}
													<button
														class="inline-flex items-center gap-1.5 rounded-lg bg-orange-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-orange-600 hover:shadow-lg hover:shadow-orange-500/30"
														onclick={() => handleAction(user.id, 'suspend')}
													>
														<svg
															class="h-4 w-4"
															fill="none"
															stroke="currentColor"
															viewBox="0 0 24 24"
														>
															<path
																stroke-linecap="round"
																stroke-linejoin="round"
																stroke-width="2"
																d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
															/>
														</svg>
														Suspend
													</button>
												{/if}
												<button
													class="inline-flex items-center gap-1.5 rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/30"
													onclick={() => handleAction(user.id, 'delete')}
												>
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
														/>
													</svg>
													Delete
												</button>
											{/if}
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>

					{#if filteredUsers.length === 0}
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
									d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
								/>
							</svg>
							<p class="mt-4 text-sm font-medium text-gray-900">No users found</p>
							<p class="mt-1 text-sm text-gray-500">Try adjusting your search or filter</p>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>
