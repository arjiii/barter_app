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
						<th class="px-6 py-4">Initiator</th>
						<th class="px-6 py-4">Receiver</th>
						<th class="px-6 py-4">Status</th>
						<th class="px-6 py-4">Created At</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100">
					{#if isLoading}
						{#each Array(5) as _}
							<tr>
								<td colspan="4" class="px-6 py-4">
									<div class="h-4 w-3/4 animate-pulse rounded bg-gray-100"></div>
								</td>
							</tr>
						{/each}
					{:else}
						{#each trades as trade}
							<tr class="transition-colors hover:bg-gray-50">
								<td class="px-6 py-4 font-medium text-gray-900"
									>{trade.initiator ? trade.initiator.name : 'Unknown'}</td
								>
								<td class="px-6 py-4 text-gray-500"
									>{trade.receiver ? trade.receiver.name : 'Unknown'}</td
								>
								<td class="px-6 py-4">
									<span
										class={`rounded-full px-2 py-1 text-xs font-medium 
										${
											trade.status === 'completed'
												? 'bg-green-100 text-green-700'
												: trade.status === 'pending'
													? 'bg-yellow-100 text-yellow-700'
													: 'bg-gray-100 text-gray-700'
										}`}
									>
										{trade.status}
									</span>
								</td>
								<td class="px-6 py-4 text-gray-500"
									>{new Date(trade.created_at).toLocaleDateString()}</td
								>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>
