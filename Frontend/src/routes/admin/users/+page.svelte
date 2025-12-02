<script lang="ts">
	import { onMount } from 'svelte';
	import { adminService } from '$lib/services/adminService';

	let users: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);

	async function loadUsers() {
		isLoading = true;
		try {
			users = await adminService.getUsers();
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	async function handleDelete(userId: string) {
		if (!confirm('Are you sure you want to delete this user?')) return;
		try {
			await adminService.deleteUser(userId);
			users = users.filter((u) => u.id !== userId);
		} catch (err: any) {
			alert('Failed to delete user: ' + err.message);
		}
	}

	onMount(loadUsers);
</script>

<div class="mx-auto max-w-7xl">
	<div class="mb-8 flex items-center justify-between">
		<h2 class="text-2xl font-bold text-gray-900">Users Management</h2>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl bg-red-50 p-4 text-red-700">{error}</div>
	{/if}

	<div class="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="border-b border-gray-100 bg-gray-50 font-medium text-gray-600">
					<tr>
						<th class="px-6 py-4">Name</th>
						<th class="px-6 py-4">Email</th>
						<th class="px-6 py-4">Role</th>
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
						{#each users as user}
							<tr class="transition-colors hover:bg-gray-50">
								<td class="px-6 py-4 font-medium text-gray-900">{user.name}</td>
								<td class="px-6 py-4 text-gray-500">{user.email}</td>
								<td class="px-6 py-4">
									<span
										class={`rounded-full px-2 py-1 text-xs font-medium ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'}`}
									>
										{user.role}
									</span>
								</td>
								<td class="px-6 py-4">
									<span
										class={`rounded-full px-2 py-1 text-xs font-medium ${user.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}
									>
										{user.is_verified ? 'Verified' : 'Unverified'}
									</span>
								</td>
								<td class="px-6 py-4 text-right">
									<button
										onclick={() => handleDelete(user.id)}
										class="font-medium text-red-600 hover:text-red-800"
										disabled={user.role === 'admin'}
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
