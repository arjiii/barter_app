<script lang="ts">
	import { onMount } from 'svelte';
	import { adminService } from '$lib/services/adminService';

	let items: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);

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

	onMount(loadItems);
</script>

<div class="mx-auto max-w-7xl">
	<div class="mb-8 flex items-center justify-between">
		<h2 class="text-2xl font-bold text-gray-900">Items Management</h2>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl bg-red-50 p-4 text-red-700">{error}</div>
	{/if}

	<div class="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="border-b border-gray-100 bg-gray-50 font-medium text-gray-600">
					<tr>
						<th class="px-6 py-4">Title</th>
						<th class="px-6 py-4">Category</th>
						<th class="px-6 py-4">Owner</th>
						<th class="px-6 py-4">Status</th>
						<th class="px-6 py-4 text-right">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100">
					{#if isLoading}
						{#each Array(5) as _}
							<tr>
								<td colspan="5" class="px-6 py-4">
									<div class="h-4 w-3/4 animate-pulse rounded bg-gray-100"></div>
								</td>
							</tr>
						{/each}
					{:else}
						{#each items as item}
							<tr class="transition-colors hover:bg-gray-50">
								<td class="px-6 py-4 font-medium text-gray-900">
									<div class="flex items-center">
										{#if item.images && item.images.length > 0}
											<img src={item.images[0]} alt="" class="mr-3 h-8 w-8 rounded object-cover" />
										{/if}
										{item.title}
									</div>
								</td>
								<td class="px-6 py-4 text-gray-500">{item.category}</td>
								<td class="px-6 py-4 text-gray-500">{item.owner ? item.owner.name : 'Unknown'}</td>
								<td class="px-6 py-4">
									<span
										class={`rounded-full px-2 py-1 text-xs font-medium ${item.status === 'available' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}
									>
										{item.status}
									</span>
								</td>
								<td class="px-6 py-4 text-right">
									<button
										onclick={() => handleDelete(item.id)}
										class="font-medium text-red-600 hover:text-red-800"
									>
										Delete
									</button>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>
