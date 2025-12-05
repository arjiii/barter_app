<script lang="ts">
	import { onMount } from 'svelte';
	import { adminService } from '$lib/services/adminService';

	let items: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let searchQuery = $state('');
	let filterCategory = $state('all');
	let filterStatus = $state('all');

	async function loadItems() {
		isLoading = true;
		try {
			items = await adminService.getItems();
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	async function handleDelete(itemId: string) {
		if (!confirm('Are you sure you want to delete this item?')) return;
		try {
			await adminService.deleteItem(itemId);
			items = items.filter((i) => i.id !== itemId);
		} catch (err: any) {
			alert('Failed to delete item: ' + err.message);
		}
	}

	async function handleStatusChange(itemId: string, newStatus: string) {
		try {
			await adminService.updateItemStatus(itemId, newStatus);
			items = items.map((i) => (i.id === itemId ? { ...i, status: newStatus } : i));
		} catch (err: any) {
			alert('Failed to update status: ' + err.message);
		}
	}

	onMount(loadItems);

	const filteredItems = $derived(
		items.filter((item) => {
			const matchesSearch =
				item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				item.owner_name?.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesCategory = filterCategory === 'all' || item.category === filterCategory;
			const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
			return matchesSearch && matchesCategory && matchesStatus;
		})
	);

	const categories = $derived([...new Set(items.map((i) => i.category))]);

	const stats = $derived({
		total: items.length,
		available: items.filter((i) => i.status === 'available').length,
		traded: items.filter((i) => i.status === 'traded').length,
		pending: items.filter((i) => i.status === 'pending').length
	});
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-900">Items Management</h1>
				<p class="mt-2 text-sm text-gray-600">Monitor and manage all listed items</p>
			</div>
			<button
				class="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all hover:bg-orange-600 hover:shadow-xl hover:shadow-orange-500/40"
				onclick={() => loadItems()}
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
								d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
							/>
						</svg>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.total}</div>
					<div class="text-sm text-gray-600">Total Items</div>
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
					<div class="text-2xl font-bold text-gray-900">{stats.available}</div>
					<div class="text-sm text-gray-600">Available</div>
				</div>
			</div>

			<div
				class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md"
			>
				<div
					class="absolute right-0 top-0 -mr-6 -mt-6 h-24 w-24 rounded-full bg-purple-50 opacity-50"
				></div>
				<div class="relative">
					<div class="mb-2 w-fit rounded-lg bg-purple-100 p-2">
						<svg
							class="h-5 w-5 text-purple-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
							/>
						</svg>
					</div>
					<div class="text-2xl font-bold text-gray-900">{stats.traded}</div>
					<div class="text-sm text-gray-600">Traded</div>
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
		</div>

		{#if error}
			<div class="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
		{/if}

		<!-- Filters -->
		<div class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
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
					placeholder="Search items..."
					class="block w-full rounded-lg border-0 py-2.5 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-orange-500 sm:text-sm"
				/>
			</div>

			<div class="flex flex-wrap gap-2">
				<select
					bind:value={filterStatus}
					class="rounded-lg border-0 px-3 py-2 text-sm font-medium ring-1 ring-gray-300 focus:ring-2 focus:ring-orange-500"
				>
					<option value="all">All Status</option>
					<option value="available">Available</option>
					<option value="traded">Traded</option>
					<option value="pending">Pending</option>
				</select>

				<select
					bind:value={filterCategory}
					class="rounded-lg border-0 px-3 py-2 text-sm font-medium ring-1 ring-gray-300 focus:ring-2 focus:ring-orange-500"
				>
					<option value="all">All Categories</option>
					{#each categories as category}
						<option value={category}>{category}</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Table -->
		<div class="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-gray-900/5">
			{#if isLoading}
				<div class="p-12 text-center">
					<div
						class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-orange-500 border-r-transparent"
					></div>
					<p class="mt-4 text-sm text-gray-500">Loading items...</p>
				</div>
			{:else if filteredItems.length === 0}
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
							d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
						/>
					</svg>
					<p class="mt-4 text-sm font-medium text-gray-900">No items found</p>
					<p class="mt-1 text-sm text-gray-500">Try adjusting your search or filter</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Item</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Category</th
								>
								<th
									scope="col"
									class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
									>Owner</th
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
							{#each filteredItems as item}
								<tr class="group transition-colors hover:bg-gray-50">
									<td class="px-6 py-4">
										<div class="flex items-center gap-3">
											<div
												class="flex h-12 w-12 flex-shrink-0 items-center justify-center overflow-hidden rounded-lg bg-gray-100 ring-2 ring-gray-200"
											>
												{#if item.images && item.images.length > 0}
													<img
														src={item.images[0]}
														alt=""
														class="h-full w-full object-cover"
														onerror={(e) => {
															e.target.src = 'https://via.placeholder.com/48?text=No+Img';
														}}
													/>
												{:else}
													<svg
														class="h-6 w-6 text-gray-400"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
														></path>
													</svg>
												{/if}
											</div>
											<div>
												<div class="font-medium text-gray-900">{item.title}</div>
												<div class="text-xs text-gray-500">ID: {item.id.slice(0, 8)}...</div>
											</div>
										</div>
									</td>
									<td class="px-6 py-4">
										<span
											class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"
										>
											{item.category}
										</span>
									</td>
									<td class="px-6 py-4">
										<div class="flex items-center gap-2">
											<div
												class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-pink-500 text-xs font-semibold text-white"
											>
												{item.owner_name ? item.owner_name.charAt(0).toUpperCase() : '?'}
											</div>
											<span class="text-sm text-gray-600">{item.owner_name || 'Unknown'}</span>
										</div>
									</td>
									<td class="px-6 py-4">
										<span
											class={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
												item.status === 'available'
													? 'bg-green-100 text-green-800'
													: item.status === 'traded'
														? 'bg-blue-100 text-blue-800'
														: 'bg-gray-100 text-gray-800'
											}`}
										>
											<span
												class={`h-1.5 w-1.5 rounded-full ${
													item.status === 'available'
														? 'bg-green-400'
														: item.status === 'traded'
															? 'bg-blue-400'
															: 'bg-gray-400'
												}`}
											></span>
											{item.status.charAt(0).toUpperCase() + item.status.slice(1)}
										</span>
									</td>
									<td class="px-6 py-4 text-right">
										<div class="flex items-center justify-end gap-2">
											<select
												onchange={(e) => handleStatusChange(item.id, e.target.value)}
												value={item.status}
												class="rounded-lg border-gray-300 px-3 py-1.5 text-xs font-medium transition-all focus:border-orange-500 focus:ring-orange-500"
											>
												<option value="available">Available</option>
												<option value="traded">Traded</option>
												<option value="pending">Pending</option>
											</select>
											<button
												onclick={() => handleDelete(item.id)}
												class="inline-flex items-center gap-1.5 rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/30"
												title="Delete Item"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
													></path>
												</svg>
												Delete
											</button>
										</div>
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
