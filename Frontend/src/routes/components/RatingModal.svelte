<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { tradeService } from '$lib/services/tradeService';

	const dispatch = createEventDispatcher();

	let { isOpen = $bindable(false), tradeId = '', raterUserId = '', rateeUserId = '', rateeUserName = '' } = $props<{
		isOpen?: boolean;
		tradeId?: string;
		raterUserId?: string;
		rateeUserId?: string;
		rateeUserName?: string;
	}>();

	let score = $state(5);
	let feedback = $state('');
	let isLoading = $state(false);
	let error: string | null = $state(null);
	let success = $state(false);

	// Reset form when modal opens/closes
	$effect(() => {
		if (isOpen) {
			score = 5;
			feedback = '';
			error = null;
			success = false;
		}
	});

	async function handleSubmit() {
		if (!tradeId || !raterUserId || !rateeUserId) {
			error = 'Missing required information';
			return;
		}

		isLoading = true;
		error = null;

		try {
			const ok = await tradeService.rateTrade(tradeId, raterUserId, rateeUserId, score, feedback.trim() || undefined);
			
			if (ok) {
				success = true;
				dispatch('rated', { tradeId, score, feedback });
				
				// Close modal after a short delay
				setTimeout(() => {
					isOpen = false;
				}, 1500);
			} else {
				error = 'Failed to submit rating. Please try again.';
			}
		} catch (err) {
			error = `Failed to submit rating: ${(err as Error).message}`;
			console.error('Error rating trade:', err);
		} finally {
			isLoading = false;
		}
	}

	function closeModal() {
		if (!isLoading) {
			isOpen = false;
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onclick={closeModal}>
		<div class="bg-white rounded-xl shadow-xl max-w-md w-full" onclick={(e) => e.stopPropagation()}>
			<!-- Header -->
			<div class="flex items-center justify-between p-6 border-b border-gray-200">
				<h2 class="text-xl font-semibold text-gray-900">Rate User</h2>
				<button
					onclick={closeModal}
					disabled={isLoading}
					class="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
					aria-label="Close modal"
				>
					<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="p-6 space-y-6">
				{#if rateeUserName}
					<div class="text-center">
						<p class="text-gray-600">Rate your experience with</p>
						<p class="text-lg font-semibold text-gray-900">{rateeUserName}</p>
					</div>
				{/if}

				<!-- Star Rating -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3 text-center">
						Rating
					</label>
					<div class="flex justify-center items-center space-x-2">
						{#each [1, 2, 3, 4, 5] as star}
							<button
								type="button"
								onclick={() => score = star}
								disabled={isLoading}
								class="focus:outline-none transition-transform hover:scale-110 disabled:opacity-50"
							>
								<svg
									class="w-10 h-10 {score >= star ? 'text-yellow-400' : 'text-gray-300'}"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
								</svg>
							</button>
						{/each}
					</div>
					<p class="text-center text-sm text-gray-500 mt-2">{score} out of 5 stars</p>
				</div>

				<!-- Feedback -->
				<div>
					<label for="rating-feedback" class="block text-sm font-medium text-gray-700 mb-2">
						Feedback (optional)
					</label>
					<textarea
						id="rating-feedback"
						bind:value={feedback}
						placeholder="Share your experience..."
						rows="4"
						disabled={isLoading}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none disabled:opacity-50"
					></textarea>
				</div>

				<!-- Error/Success Messages -->
				{#if error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-3">
						<div class="flex items-center">
							<svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
							</svg>
							<p class="text-sm text-red-700">{error}</p>
						</div>
					</div>
				{/if}

				{#if success}
					<div class="bg-green-50 border border-green-200 rounded-lg p-3">
						<div class="flex items-center">
							<svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
							</svg>
							<p class="text-sm text-green-700">Rating submitted successfully!</p>
						</div>
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
				<button
					onclick={closeModal}
					disabled={isLoading}
					class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors font-medium disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={handleSubmit}
					disabled={isLoading}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
				>
					{#if isLoading}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{/if}
					Submit Rating
				</button>
			</div>
		</div>
	</div>
{/if}










