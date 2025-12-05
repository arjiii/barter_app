<script lang="ts">
	import { onMount } from 'svelte';
	import { adminService } from '$lib/services/adminService';

	let trades: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);

	async function loadTrades() {
		isLoading = true;
		try {
			trades = await adminService.getTrades();
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	async function handleDelete(tradeId: string) {
		if (!confirm('Are you sure you want to delete this trade?')) return;
		try {
			await adminService.deleteTrade(tradeId);
			trades = trades.filter((t) => t.id !== tradeId);
		} catch (err: any) {
			alert('Failed to delete trade: ' + err.message);
		}
	}

	onMount(loadTrades);
</script>

<div class="mx-auto max-w-7xl">
	<div class="mb-8 flex items-center justify-between">
		<h2 class="text-2xl font-bold text-gray-900">Trades Management</h2>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl bg-red-50 p-4 text-red-700">{error}</div>
	{/if}

	<div class="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="border-b border-gray-100 bg-gray-50 font-medium text-gray-600">
					<tr>
						<th class="px-6 py-4">Trade Details</th>
						<th class="px-6 py-4">Participants</th>
						<th class="px-6 py-4">Status</th>
						<th class="px-6 py-4">Date</th>
						<th class="px-6 py-4 text-right">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100">
					{#if isLoading}
						{#each Array(5) as _}
							<tr>
								<td colspan="5" class="px-6 py-4">
									<div class="flex items-center space-x-4">
										<div class="h-10 w-10 animate-pulse rounded-lg bg-gray-100"></div>
										<div class="space-y-2">
											<div class="h-4 w-32 animate-pulse rounded bg-gray-100"></div>
											<div class="h-3 w-24 animate-pulse rounded bg-gray-100"></div>
										</div>
									</div>
								</td>
							</tr>
						{/each}
					{:else}
						{#each trades as trade}
							<tr class="group transition-colors hover:bg-gray-50">
								<td class="px-6 py-4">
									<div class="flex items-center">
										<div
											class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600"
										>
											<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
												></path>
											</svg>
										</div>
										<div class="ml-4">
											<div class="font-medium text-gray-900">Trade #{trade.id.slice(0, 8)}</div>
											<div class="text-xs text-gray-500">
												{trade.from_item ? trade.from_item.title : 'Item'} ↔ {trade.to_item
													? trade.to_item.title
													: 'Item'}
											</div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex -space-x-2 overflow-hidden">
										<div
											class="inline-block h-8 w-8 rounded-full bg-indigo-100 ring-2 ring-white"
											title={trade.initiator ? trade.initiator.name : 'Unknown'}
										>
											<span
												class="flex h-full w-full items-center justify-center text-xs font-medium text-indigo-700"
											>
												{trade.initiator ? trade.initiator.name.charAt(0).toUpperCase() : '?'}
											</span>
										</div>
										<div
											class="inline-block h-8 w-8 rounded-full bg-pink-100 ring-2 ring-white"
											title={trade.receiver ? trade.receiver.name : 'Unknown'}
										>
											<span
												class="flex h-full w-full items-center justify-center text-xs font-medium text-pink-700"
											>
												{trade.receiver ? trade.receiver.name.charAt(0).toUpperCase() : '?'}
											</span>
										</div>
									</div>
								</td>
								<td class="px-6 py-4">
									<span
										class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium 
										${
											trade.status === 'completed'
												? 'bg-green-100 text-green-800'
												: trade.status === 'pending'
													? 'bg-yellow-100 text-yellow-800'
													: trade.status === 'active'
														? 'bg-blue-100 text-blue-800'
														: 'bg-gray-100 text-gray-800'
										}`}
									>
										<span
											class={`mr-1.5 h-1.5 w-1.5 rounded-full 
											${
												trade.status === 'completed'
													? 'bg-green-400'
													: trade.status === 'pending'
														? 'bg-yellow-400'
														: trade.status === 'active'
															? 'bg-blue-400'
															: 'bg-gray-400'
											}`}
										></span>
										{trade.status.charAt(0).toUpperCase() + trade.status.slice(1)}
									</span>
								</td>
								<td class="px-6 py-4 text-sm text-gray-500">
									{new Date(trade.created_at).toLocaleDateString()}
								</td>
								<td class="px-6 py-4 text-right">
									<button
										onclick={() => handleDelete(trade.id)}
										class="rounded-lg p-2 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600"
										title="Delete Trade"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
											></path>
										</svg>
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
