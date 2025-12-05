<script lang="ts">
	import { onMount } from 'svelte';
	import { supportService } from '$lib/services/supportService';

	let requests: any[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let showCreateModal = $state(false);
	let newRequest = $state({
		type: 'password_reset',
		subject: '',
		message: ''
	});
	let isSubmitting = $state(false);

	async function loadRequests() {
		isLoading = true;
		try {
			requests = await supportService.getRequests();
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		isSubmitting = true;
		try {
			const createdRequest = await supportService.createRequest(newRequest);
			requests = [createdRequest, ...requests];
			showCreateModal = false;
			newRequest = { type: 'password_reset', subject: '', message: '' };
			alert('Support request submitted successfully');
		} catch (err: any) {
			alert('Failed to submit request: ' + err.message);
		} finally {
			isSubmitting = false;
		}
	}

	onMount(loadRequests);
</script>

<div class="mx-auto max-w-4xl">
	<div class="mb-8 flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Help & Support</h1>
			<p class="mt-1 text-sm text-gray-500">Manage your support requests and account issues.</p>
		</div>
		<button
			onclick={() => (showCreateModal = true)}
			class="flex items-center rounded-xl bg-[#ff6d3f] px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-[#e55a2f] focus:outline-none focus:ring-2 focus:ring-[#ff6d3f] focus:ring-offset-2"
		>
			<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			New Request
		</button>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl bg-red-50 p-4 text-red-700">{error}</div>
	{/if}

	{#if isLoading}
		<div class="space-y-4">
			{#each Array(3) as _}
				<div class="h-24 animate-pulse rounded-xl bg-gray-100"></div>
			{/each}
		</div>
	{:else if requests.length === 0}
		<div class="rounded-2xl border border-dashed border-gray-300 bg-gray-50 p-12 text-center">
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
					d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			<h3 class="mt-2 text-sm font-medium text-gray-900">No support requests</h3>
			<p class="mt-1 text-sm text-gray-500">Get started by creating a new request.</p>
			<div class="mt-6">
				<button
					onclick={() => (showCreateModal = true)}
					class="inline-flex items-center rounded-md border border-transparent bg-[#ff6d3f] px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-[#e55a2f] focus:outline-none focus:ring-2 focus:ring-[#ff6d3f] focus:ring-offset-2"
				>
					<svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					New Request
				</button>
			</div>
		</div>
	{:else}
		<div class="space-y-4">
			{#each requests as request}
				<div
					class="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm transition-all hover:shadow-md"
				>
					<div class="p-6">
						<div class="flex items-start justify-between">
							<div class="space-y-1">
								<div class="flex items-center space-x-2">
									<h3 class="text-lg font-medium text-gray-900">{request.subject}</h3>
									<span
										class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
											request.status === 'resolved'
												? 'bg-green-100 text-green-800'
												: request.status === 'rejected'
													? 'bg-red-100 text-red-800'
													: 'bg-yellow-100 text-yellow-800'
										}`}
									>
										{request.status.charAt(0).toUpperCase() + request.status.slice(1)}
									</span>
								</div>
								<p class="text-sm text-gray-500">
									Type: <span class="font-medium text-gray-700"
										>{request.type.replace('_', ' ')}</span
									>
								</p>
							</div>
							<div class="text-sm text-gray-500">
								{new Date(request.created_at).toLocaleDateString()}
							</div>
						</div>
						<div class="mt-4 text-sm text-gray-600">
							{request.message}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showCreateModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
		<div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
			<div class="mb-4 flex items-center justify-between">
				<h3 class="text-lg font-bold text-gray-900">New Support Request</h3>
				<button onclick={() => (showCreateModal = false)} class="text-gray-400 hover:text-gray-500">
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
			<form onsubmit={handleSubmit} class="space-y-4">
				<div>
					<label for="type" class="block text-sm font-medium text-gray-700">Request Type</label>
					<select
						id="type"
						bind:value={newRequest.type}
						class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-[#ff6d3f] focus:outline-none focus:ring-1 focus:ring-[#ff6d3f]"
					>
						<option value="password_reset">Password Reset</option>
						<option value="account_issue">Account Issue</option>
						<option value="other">Other</option>
					</select>
				</div>
				<div>
					<label for="subject" class="block text-sm font-medium text-gray-700">Subject</label>
					<input
						type="text"
						id="subject"
						bind:value={newRequest.subject}
						required
						class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-[#ff6d3f] focus:outline-none focus:ring-1 focus:ring-[#ff6d3f]"
						placeholder="Brief summary of your request"
					/>
				</div>
				<div>
					<label for="message" class="block text-sm font-medium text-gray-700">Message</label>
					<textarea
						id="message"
						bind:value={newRequest.message}
						required
						rows="4"
						class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-[#ff6d3f] focus:outline-none focus:ring-1 focus:ring-[#ff6d3f]"
						placeholder="Describe your issue in detail..."
					></textarea>
				</div>
				<div class="mt-6 flex justify-end space-x-3">
					<button
						type="button"
						onclick={() => (showCreateModal = false)}
						class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
					>
						Cancel
					</button>
					<button
						type="submit"
						disabled={isSubmitting}
						class="rounded-lg bg-[#ff6d3f] px-4 py-2 text-sm font-medium text-white hover:bg-[#e55a2f] disabled:opacity-50"
					>
						{isSubmitting ? 'Submitting...' : 'Submit Request'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
