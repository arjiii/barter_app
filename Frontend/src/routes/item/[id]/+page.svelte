<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { itemService } from '$lib/services/itemService';
	import { tradeService } from '$lib/services/tradeService';
	import { messageService } from '$lib/services/messageService';
	import TradeOfferModal from '../../components/TradeOfferModal.svelte';
	import type { Item } from '$lib/types/items';
	import type { User } from '$lib/types/auth';
	import type { Trade } from '$lib/types/trades';

	let item: Item | null = $state(null);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let currentImageIndex = $state(0);
let relatedItems: Item[] = $state([]);
	let showTradeModal = $state(false);

	// Get item ID from URL params
	let itemId = $derived($page.params.id);

	async function loadItem() {
		if (!itemId) {
			error = 'Item not found';
			isLoading = false;
			return;
		}

    try {
			isLoading = true;
			error = null;
        item = await itemService.getItemById(itemId);
        // Load related items from same category (excluding this item)
        if (item?.category) {
            const sameCategory = await itemService.getItems({ status: 'available', category: item.category });
            relatedItems = sameCategory.filter(i => i.id !== itemId).slice(0, 8);
        } else {
            relatedItems = [];
        }
		} catch (err) {
			error = 'Failed to load item details';
			console.error('Error loading item:', err);
		} finally {
			isLoading = false;
		}
	}

	function nextImage() {
		if (item && item.images.length > 1) {
			currentImageIndex = (currentImageIndex + 1) % item.images.length;
		}
	}

	function prevImage() {
		if (item && item.images.length > 1) {
			currentImageIndex = currentImageIndex === 0 ? item.images.length - 1 : currentImageIndex - 1;
		}
	}

	function handleMakeOffer() {
		if (!isAuthenticated) {
			goto('/sign-in-up');
			return;
		}
		if (item) {
			showTradeModal = true;
		}
	}

	function handleTradeCreated(event: CustomEvent<Trade>) {
		console.log('Trade created:', event.detail);
		// Reload item to update offers count
		if (item) {
			loadItem();
		}
	}

	async function handleContactOwner() {
		if (!isAuthenticated) {
			goto('/sign-in-up');
			return;
		}
		if (!item || !user) return;

		try {
			// 1) Check for existing trade between the two users (any item)
			const trades = await tradeService.getTrades({ userId: user.id });
			const existingTrade = trades.find((t) => {
				return (
					(t.fromUserId === user.id && t.toUserId === item.userId) ||
					(t.toUserId === user.id && t.fromUserId === item.userId)
				);
			});

			if (existingTrade) {
				goto(`/messages?trade=${existingTrade.id}`);
				return;
			}

			// 2) No existing conversation: create a simple chat trade + first message,
			// then go straight to the messages page so both users can chat.
			const quickMessage =
				`Hi ${item.owner?.name || ''}, I'm interested in your "${item.title}".` .trim();

			const createdTrade = await tradeService.createTrade(user.id, {
				toUserId: item.userId,
				// Use the viewed item as both from/to to satisfy backend shape;
				// this acts as a lightweight "chat context" for this item.
				fromItemId: item.id,
				toItemId: item.id,
				message: quickMessage
			});

			if (createdTrade) {
				try {
					await messageService.createMessage(user.id, {
						tradeId: createdTrade.id,
						receiverId: item.userId,
						content: quickMessage
					});
				} catch (msgErr) {
					console.warn('Failed to create initial chat message:', msgErr);
				}

				goto(`/messages?trade=${createdTrade.id}`);
				return;
			}

			console.error('Failed to create quick chat trade');
		} catch (err) {
			console.error('Error contacting owner:', err);
		}
	}

	onMount(() => {
		// Load auth state
		const unsubscribe = authStore.subscribe((authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
		});

		// Load item data
		loadItem();

		return unsubscribe;
	});
</script>

<div class="min-h-screen bg-gray-50">
	{#if isLoading}
		<div class="flex items-center justify-center min-h-screen">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
				<p class="text-gray-600">Loading item details...</p>
			</div>
		</div>
	{:else if error}
		<div class="flex items-center justify-center min-h-screen">
			<div class="text-center">
				<svg class="mx-auto h-16 w-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
				</svg>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button 
					onclick={() => goto('/discovery')}
					class="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
				>
					Back to Discovery
				</button>
			</div>
		</div>
	{:else if item}
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<!-- Back Button -->
			<button 
				onclick={() => goto('/discovery')}
				class="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
			>
				<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
				</svg>
				Back to Discovery
			</button>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<!-- Image Gallery -->
				<div class="space-y-4">
					<!-- Main Image -->
					<div class="relative bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
						<img 
							src={item.images[currentImageIndex] || 'https://via.placeholder.com/600x400?text=No+Image'} 
							alt={item.title}
							class="w-full h-96 object-cover"
						/>
						
						<!-- Image Navigation -->
						{#if item.images.length > 1}
							<button 
								onclick={prevImage}
								class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
							>
								<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
								</svg>
							</button>
							<button 
								onclick={nextImage}
								class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
							>
								<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
								</svg>
							</button>
							
							<!-- Image Counter -->
							<div class="absolute bottom-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
								{currentImageIndex + 1} / {item.images.length}
							</div>
						{/if}
					</div>

					<!-- Thumbnail Gallery -->
					{#if item.images.length > 1}
						<div class="grid grid-cols-4 gap-2">
							{#each item.images as image, index}
								<button 
									onclick={() => currentImageIndex = index}
									class="relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow
										{currentImageIndex === index ? 'ring-2 ring-red-500' : ''}"
								>
									<img 
										src={image} 
										alt="Thumbnail {index + 1}"
										class="w-full h-20 object-cover"
									/>
								</button>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Item Details -->
				<div class="space-y-6">
					<!-- Header -->
					<div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
						<div class="flex items-start justify-between mb-4">
							<div class="flex-1">
								<h1 class="text-3xl font-bold text-gray-900 mb-2">{item.title}</h1>
								<div class="flex items-center space-x-4 text-sm text-gray-500">
									<span class="bg-red-100 text-red-800 px-3 py-1 rounded-full font-medium">
										{item.condition}
									</span>
									<span class="bg-gray-100 text-gray-800 px-3 py-1 rounded-full font-medium">
										{item.category}
									</span>
								</div>
							</div>
							<div class="text-right">
								<div class="text-sm text-gray-500">Posted</div>
								<div class="font-medium">{item.postedAgo}</div>
							</div>
						</div>

						<!-- Description -->
						<div class="mb-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Description</h3>
							<p class="text-gray-700 leading-relaxed">{item.description}</p>
						</div>

					<!-- More Info -->
					<div class="mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-3">More information</h3>
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Status</div>
								<div class="font-medium text-gray-900 capitalize">{item.status}</div>
							</div>
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Condition</div>
								<div class="font-medium text-gray-900">{item.condition}</div>
							</div>
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Category</div>
								<div class="font-medium text-gray-900">{item.category}</div>
							</div>
							{#if item.location}
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Location</div>
								<div class="font-medium text-gray-900 flex items-center">
									<svg class="w-4 h-4 mr-1 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
									</svg>
									{item.location}
								</div>
							</div>
							{/if}
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Item ID</div>
								<div class="font-mono text-sm text-gray-900 break-all">{item.id}</div>
							</div>
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Created</div>
								<div class="font-medium text-gray-900">{new Date(item.createdAt).toLocaleString()}</div>
							</div>
							<div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
								<div class="text-xs text-gray-500">Updated</div>
								<div class="font-medium text-gray-900">{new Date(item.updatedAt).toLocaleString()}</div>
							</div>
						</div>
					</div>

						<!-- Stats -->
						<div class="grid grid-cols-2 gap-4 py-4 border-t border-gray-200">
							<div class="text-center">
								<div class="text-2xl font-bold text-gray-900">{item.views}</div>
								<div class="text-sm text-gray-500">Views</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-gray-900">{item.offersCount || 0}</div>
								<div class="text-sm text-gray-500">Offers</div>
							</div>
						</div>
					</div>

					<!-- Owner Info -->
					<div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4">Posted by</h3>
						<div 
							class="flex items-center space-x-4 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
							onclick={() => item?.owner?.id && goto(`/user/${item.owner.id}`)}
							role="button"
							tabindex="0"
						>
							<div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center">
								<span class="text-white font-semibold">
									{item.owner?.name?.charAt(0) || 'U'}
								</span>
							</div>
							<div class="flex-1">
								<div class="font-semibold text-gray-900 hover:text-red-600 transition-colors">{item.owner?.name || 'User'}</div>
								<div class="text-sm text-gray-500">
									{#if item.owner?.rating}
										⭐ {item.owner.rating.toFixed(1)} rating
									{:else}
										Member
									{/if}
								</div>
							</div>
							<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
							</svg>
						</div>
					</div>

					<!-- Action Buttons -->
					<div class="space-y-3">
						{#if isAuthenticated}
							{#if item.userId !== user?.id}
							<button 
								onclick={handleMakeOffer}
								class="w-full bg-red-600 text-white py-4 px-6 rounded-xl hover:bg-red-700 transition-colors font-semibold text-lg shadow-sm hover:shadow-md"
							>
								Make an Offer
							</button>
							<button 
								onclick={handleContactOwner}
								class="w-full bg-gray-100 text-gray-700 py-3 px-6 rounded-xl hover:bg-gray-200 transition-colors font-medium"
							>
								Contact Owner
							</button>
							{:else}
								<div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
									<p class="text-blue-800 font-medium">This is your item</p>
									<p class="text-blue-600 text-sm mt-1">You cannot make an offer on your own item</p>
								</div>
							{/if}
						{:else}
							<button 
								onclick={() => goto('/sign-in-up')}
								class="w-full bg-red-600 text-white py-4 px-6 rounded-xl hover:bg-red-700 transition-colors font-semibold text-lg shadow-sm hover:shadow-md"
							>
								Sign in to Make Offer
							</button>
						{/if}
					</div>
				</div>
			</div>

		<!-- Related Items -->
		{#if relatedItems.length}
			<div class="mt-10">
				<h3 class="text-xl font-semibold text-gray-900 mb-4">Similar items</h3>
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
					{#each relatedItems as ri}
						<button onclick={() => goto(`/item/${ri.id}`)} class="text-left bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition overflow-hidden">
							<img src={ri.images[0] || 'https://via.placeholder.com/400x300?text=No+Image'} alt={ri.title} class="w-full h-40 object-cover" />
							<div class="p-4">
								<div class="font-medium text-gray-900 line-clamp-1 mb-1">{ri.title}</div>
								<div class="text-sm text-gray-600 line-clamp-2">{ri.description}</div>
							</div>
						</button>
					{/each}
				</div>
			</div>
		{/if}
		</div>
	{/if}
</div>

<!-- Trade Offer Modal -->
{#if item}
	<TradeOfferModal bind:isOpen={showTradeModal} bind:targetItem={item} on:tradeCreated={handleTradeCreated} />
{/if}
