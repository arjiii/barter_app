<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { tradeService } from '$lib/services/tradeService';
	import { itemService } from '$lib/services/itemService';
	import { messageService } from '$lib/services/messageService';
	import type { CreateTradeData } from '$lib/types/trades';
	import type { Item } from '$lib/types/items';

	const dispatch = createEventDispatcher();

	let { isOpen = $bindable(false), targetItem = null } = $props<{
		isOpen?: boolean;
		targetItem?: Item | null;
	}>();

	let isLoading = $state(false);
	let error: string | null = $state(null);
	let success: string | null = $state(null);
	let myItems: Item[] = $state([]);
	let selectedItem: Item | null = $state(null);
	let message = $state('');

	// Load user's items when modal opens
	async function loadMyItems() {
		if (!isOpen) return;
		
		const authState = authStore.get();
		if (!authState.user) return;

		try {
			const items = await itemService.getItems({ userId: authState.user.id, status: 'available' });
			myItems = items;
		} catch (err) {
			console.error('Error loading my items:', err);
			error = 'Failed to load your items';
		}
	}

	// Watch for modal open/close
	$effect(() => {
		if (isOpen) {
			loadMyItems();
		} else {
			// Reset form when closing
			selectedItem = null;
			message = '';
			error = null;
			success = null;
		}
	});

	async function handleSubmit() {
		if (!selectedItem || !targetItem) return;

		const authState = authStore.get();
		if (!authState.user) {
			error = 'Please sign in to make a trade offer';
			return;
		}

		isLoading = true;
		error = null;
		success = null;

		try {
			const tradeData: CreateTradeData = {
				to_user_id: targetItem.user_id,
				from_item_id: selectedItem.id,
				to_item_id: targetItem.id,
				message: message.trim() || `I'd like to trade my ${selectedItem.title} for your ${targetItem.title}`
			};

			const createdTrade = await tradeService.createTrade(tradeData);
			
			if (createdTrade) {
				// Create initial message automatically when trade offer is made
				try {
					const messageContent = message.trim() || `I'd like to trade my ${selectedItem.title} for your ${targetItem.title}`;
					await messageService.createMessage({
						trade_id: createdTrade.id,
						receiver_id: targetItem.user_id,
						content: messageContent
					});
				} catch (msgError) {
					console.warn('Failed to create initial message:', msgError);
					// Don't fail the trade creation if message creation fails
				}

				success = 'Trade offer sent successfully! You can now message each other.';
				dispatch('tradeCreated', createdTrade);
				
				// Close modal after success and navigate to messages
				setTimeout(() => {
					isOpen = false;
					// Navigate to messages page with the trade ID
					goto(`/messages?trade=${createdTrade.id}`);
				}, 1500);
			} else {
				throw new Error('Failed to create trade offer');
			}
		} catch (err) {
			error = `Failed to send trade offer: ${(err as Error).message}`;
			console.error('Error creating trade:', err);
		} finally {
			isLoading = false;
		}
	}

	function closeModal() {
		isOpen = false;
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<!-- Header -->
			<div class="flex items-center justify-between p-6 border-b border-gray-200">
				<h2 class="text-xl font-semibold text-gray-900">Make Trade Offer</h2>
				<button
					onclick={closeModal}
					class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
					aria-label="Close modal"
				>
					<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="p-6 space-y-6">
				{#if targetItem}
					<!-- Target Item -->
					<div class="bg-gray-50 rounded-lg p-4">
						<h3 class="font-medium text-gray-900 mb-2">Item you want:</h3>
						<div class="flex items-center space-x-3">
							{#if targetItem.images && targetItem.images.length > 0}
								<img src={targetItem.images[0]} alt={targetItem.title} class="w-16 h-16 object-cover rounded-lg" />
							{:else}
								<div class="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center text-gray-500 text-xs">
									No Image
								</div>
							{/if}
							<div>
								<h4 class="font-medium text-gray-900">{targetItem.title}</h4>
								<p class="text-sm text-gray-600">{targetItem.description}</p>
								<p class="text-xs text-gray-500">Condition: {targetItem.condition}</p>
							</div>
						</div>
					</div>

					<!-- Your Items -->
					<div>
						<h3 class="font-medium text-gray-900 mb-3">Choose an item to trade:</h3>
						{#if myItems.length === 0}
							<div class="text-center py-8 text-gray-500">
								<p>You don't have any available items to trade.</p>
								<p class="text-sm mt-1">Post some items first!</p>
							</div>
						{:else}
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
								{#each myItems as item (item.id)}
									<button
										onclick={() => selectedItem = item}
										class="flex items-center space-x-3 p-3 rounded-lg border transition-colors text-left
											{selectedItem?.id === item.id 
												? 'border-red-500 bg-red-50' 
												: 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}"
									>
										{#if item.images && item.images.length > 0}
											<img src={item.images[0]} alt={item.title} class="w-12 h-12 object-cover rounded" />
										{:else}
											<div class="w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-gray-500 text-xs">
												No Image
											</div>
										{/if}
										<div class="flex-1 min-w-0">
											<h4 class="font-medium text-gray-900 truncate">{item.title}</h4>
											<p class="text-sm text-gray-600 truncate">{item.description}</p>
											<p class="text-xs text-gray-500">Condition: {item.condition}</p>
										</div>
									</button>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Message -->
					<div>
						<label for="trade-message" class="block text-sm font-medium text-gray-700 mb-2">
							Message (optional)
						</label>
						<textarea
							id="trade-message"
							bind:value={message}
							placeholder="Add a message to your trade offer..."
							rows="3"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
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
								<p class="text-sm text-green-700">{success}</p>
							</div>
						</div>
					{/if}
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
				<button
					onclick={closeModal}
					class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors font-medium"
					disabled={isLoading}
				>
					Cancel
				</button>
				<button
					onclick={handleSubmit}
					disabled={!selectedItem || isLoading}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
				>
					{#if isLoading}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{/if}
					Send Trade Offer
				</button>
			</div>
		</div>
	</div>
{/if}
