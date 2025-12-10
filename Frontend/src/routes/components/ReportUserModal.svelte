<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { userService } from '$lib/services/userService';
	import LoadingSpinner from './LoadingSpinner.svelte';

	let {
		isOpen = $bindable(false),
		reportedUserId,
		reportedUserName
	} = $props<{
		isOpen?: boolean;
		reportedUserId: string;
		reportedUserName: string;
	}>();

	const dispatch = createEventDispatcher();

	let reason = $state('spam');
	let description = $state('');
	let isSubmitting = $state(false);
	let error = $state<string | null>(null);

	const reportReasons = [
		{ value: 'spam', label: 'Spam' },
		{ value: 'inappropriate', label: 'Inappropriate Content' },
		{ value: 'scam', label: 'Scam or Fraud' },
		{ value: 'harassment', label: 'Harassment' },
		{ value: 'other', label: 'Other' }
	];

	function close() {
		isOpen = false;
		reason = 'spam';
		description = '';
		error = null;
	}

	async function handleSubmit() {
		if (!description.trim()) {
			error = 'Please provide a description for your report';
			return;
		}

		try {
			isSubmitting = true;
			error = null;
			await userService.reportUser(reportedUserId, reason, description);
			dispatch('reportSubmitted');
			close();
			alert('User reported successfully. Thank you for helping keep our community safe.');
		} catch (err: any) {
			console.error('Failed to report user:', err);
			error = err.message || 'Failed to submit report. Please try again.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
		<div class="w-full max-w-md rounded-2xl bg-white shadow-xl" use:clickOutside={close}>
			<div class="border-b border-gray-100 p-6">
				<h3 class="text-xl font-bold text-gray-900">Report User</h3>
				<p class="mt-1 text-sm text-gray-500">
					Report {reportedUserName} for violating community guidelines.
				</p>
			</div>

			<div class="space-y-4 p-6">
				{#if error}
					<div class="rounded-lg bg-red-50 p-3 text-sm text-red-600">
						{error}
					</div>
				{/if}

				<div>
					<label class="mb-2 block text-sm font-medium text-gray-700" for="reason">Reason</label>
					<select
						id="reason"
						bind:value={reason}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
					>
						{#each reportReasons as r}
							<option value={r.value}>{r.label}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="mb-2 block text-sm font-medium text-gray-700" for="description"
						>Description</label
					>
					<textarea
						id="description"
						bind:value={description}
						rows="4"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
						placeholder="Please provide specific details about the issue..."
					></textarea>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 border-t border-gray-100 p-6">
				<button
					onclick={close}
					disabled={isSubmitting}
					class="rounded-lg px-4 py-2 font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={handleSubmit}
					disabled={isSubmitting}
					class="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-50"
				>
					{#if isSubmitting}
						<LoadingSpinner size="small" color="white" />
					{/if}
					Submit Report
				</button>
			</div>
		</div>
	</div>
{/if}
