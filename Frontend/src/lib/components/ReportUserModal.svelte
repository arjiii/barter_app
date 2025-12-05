<script lang="ts">
	import { API_BASE_URL } from '$lib/config/api';

	interface Props {
		isOpen: boolean;
		userId: string;
		userName: string;
		onClose: () => void;
		onSuccess?: () => void;
	}

	let { isOpen = $bindable(), userId, userName, onClose, onSuccess }: Props = $props();

	let reason = $state('spam');
	let description = $state('');
	let isSubmitting = $state(false);
	let error = $state('');

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!description.trim()) {
			error = 'Please provide a description';
			return;
		}

		isSubmitting = true;
		error = '';

		try {
			const token = localStorage.getItem('bayanihan_token');
			const res = await fetch(`${API_BASE_URL}/reports/user`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({
					reported_user_id: userId,
					reason,
					description
				})
			});

			if (!res.ok) {
				const data = await res.json();
				throw new Error(data.detail || 'Failed to submit report');
			}

			// Success
			onSuccess?.();
			resetForm();
			onClose();
		} catch (err: any) {
			error = err.message;
		} finally {
			isSubmitting = false;
		}
	}

	function resetForm() {
		reason = 'spam';
		description = '';
		error = '';
	}

	function handleClose() {
		resetForm();
		onClose();
	}
</script>

{#if isOpen}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
		onclick={handleClose}
	>
		<div
			class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
			onclick={(e) => e.stopPropagation()}
		>
			<div class="mb-4 flex items-center justify-between">
				<h2 class="text-xl font-bold text-gray-900">Report User</h2>
				<button
					onclick={handleClose}
					class="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>

			<p class="mb-4 text-sm text-gray-600">
				You are reporting <span class="font-semibold">{userName}</span>
			</p>

			{#if error}
				<div class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			{/if}

			<form onsubmit={handleSubmit}>
				<div class="mb-4">
					<label for="reason" class="mb-2 block text-sm font-medium text-gray-700">Reason</label>
					<select
						id="reason"
						bind:value={reason}
						class="block w-full rounded-lg border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-orange-500"
					>
						<option value="spam">Spam</option>
						<option value="inappropriate">Inappropriate Content</option>
						<option value="scam">Scam or Fraud</option>
						<option value="harassment">Harassment</option>
						<option value="other">Other</option>
					</select>
				</div>

				<div class="mb-6">
					<label for="description" class="mb-2 block text-sm font-medium text-gray-700"
						>Description</label
					>
					<textarea
						id="description"
						bind:value={description}
						rows="4"
						placeholder="Please provide details about why you're reporting this user..."
						class="block w-full rounded-lg border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-orange-500"
					></textarea>
				</div>

				<div class="flex gap-3">
					<button
						type="button"
						onclick={handleClose}
						class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
					>
						Cancel
					</button>
					<button
						type="submit"
						disabled={isSubmitting}
						class="flex-1 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-red-500/30 transition-all hover:bg-red-600 hover:shadow-xl hover:shadow-red-500/40 disabled:opacity-50"
					>
						{isSubmitting ? 'Submitting...' : 'Submit Report'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
