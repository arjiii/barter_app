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
	let relatedItems = $state([] as Item[]);
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
				const sameCategory = await itemService.getItems({
					status: 'available',
					category: item.category
				});
				relatedItems = sameCategory.filter((i) => i.id !== itemId).slice(0, 8);
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

	function handleTradeCreated(_event: CustomEvent<Trade>) {
		// console.log('Trade created:', _event.detail);
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
		const targetItem = item!;
		const currentUser = user!;

		try {
			// 1) Check for existing trade between the two users (any item)
			const trades = await tradeService.getTrades({ userId: currentUser.id });
			const existingTrade = trades.find((t) => {
				return (
					(t.from_user_id === currentUser.id && t.to_user_id === targetItem.user_id) ||
					(t.to_user_id === currentUser.id && t.from_user_id === targetItem.user_id)
				);
			});

			if (existingTrade) {
				goto(`/messages?trade=${existingTrade.id}`);
				return;
			}

			// 2) No existing conversation: create a simple chat trade + first message,
			// then go straight to the messages page so both users can chat.
			const quickMessage =
				`Hi ${targetItem.owner?.name || ''}, I'm interested in your "${targetItem.title}".`.trim();

			const createdTrade = await tradeService.createTrade({
				to_user_id: targetItem.user_id,
				// Use the viewed item as both from/to to satisfy backend shape;
				// this acts as a lightweight "chat context" for this item.
				from_item_id: targetItem.id,
				to_item_id: targetItem.id,
				message: quickMessage
			});

			if (createdTrade) {
				try {
					await messageService.createMessage({
						trade_id: createdTrade.id,
						receiver_id: targetItem.user_id,
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
		<div class="flex min-h-screen items-center justify-center">
			<div class="text-center">
				<div
					class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-red-600"
				></div>
				<p class="text-gray-600">Loading item details...</p>
			</div>
		</div>
	{:else if error}
		<div class="flex min-h-screen items-center justify-center">
			<div class="text-center">
				<svg
					class="mx-auto mb-4 h-16 w-16 text-gray-300"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
					></path>
				</svg>
				<h3 class="mb-2 text-lg font-semibold text-gray-900">Something went wrong</h3>
				<p class="mb-4 text-gray-600">{error}</p>
				<a
					href="/discovery"
					class="rounded-lg bg-red-600 px-6 py-2 font-medium text-white transition-colors hover:bg-red-700"
				>
					Back to Discovery
				</a>
			</div>
		</div>
	{:else if item}
		<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
			<!-- Back Button -->
			<a
				href="/discovery"
				class="mb-6 flex items-center text-gray-600 transition-colors hover:text-gray-900"
			>
				<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"
					></path>
				</svg>
				Back to Discovery
			</a>

			<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
				<!-- Image Gallery -->
				<div class="space-y-4">
					<!-- Main Image -->
					<div
						class="relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm"
					>
						<img
							src={item.images[currentImageIndex] ||
								'https://via.placeholder.com/600x400?text=No+Image'}
							alt={item.title}
							class="h-96 w-full object-cover"
						/>

						<!-- Image Navigation -->
						{#if item.images.length > 1}
							<button
								onclick={prevImage}
								class="absolute left-4 top-1/2 -translate-y-1/2 transform rounded-full bg-black bg-opacity-50 p-2 text-white transition-all hover:bg-opacity-70"
								aria-label="Previous image"
							>
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 19l-7-7 7-7"
									></path>
								</svg>
							</button>
							<button
								onclick={nextImage}
								class="absolute right-4 top-1/2 -translate-y-1/2 transform rounded-full bg-black bg-opacity-50 p-2 text-white transition-all hover:bg-opacity-70"
								aria-label="Next image"
							>
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 5l7 7-7 7"
									></path>
								</svg>
							</button>

							<!-- Image Counter -->
							<div
								class="absolute bottom-4 right-4 rounded-full bg-black bg-opacity-50 px-3 py-1 text-sm text-white"
							>
								{currentImageIndex + 1} / {item.images.length}
							</div>
						{/if}
					</div>

					<!-- Thumbnail Gallery -->
					{#if item.images.length > 1}
						<div class="grid grid-cols-4 gap-2">
							{#each item.images as image, index (index)}
								<button
									onclick={() => (currentImageIndex = index)}
									class="relative overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md
										{currentImageIndex === index ? 'ring-2 ring-red-500' : ''}"
									aria-label={`View image ${index + 1}`}
								>
									<img src={image} alt="Thumbnail {index + 1}" class="h-20 w-full object-cover" />
								</button>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Item Details -->
				<div class="space-y-6">
					<!-- Header -->
					<div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
						<div class="mb-4 flex items-start justify-between">
							<div class="flex-1">
								<h1 class="mb-2 text-3xl font-bold text-gray-900">{item.title}</h1>
								<div class="flex items-center space-x-4 text-sm text-gray-500">
									<span class="rounded-full bg-red-100 px-3 py-1 font-medium text-red-800">
										{item.condition}
									</span>
									<span class="rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-800">
										{item.category}
									</span>
								</div>
							</div>
							<div class="text-right">
								<div class="text-sm text-gray-500">Posted</div>
								<div class="font-medium">{itemService.formatPostedAgo(item.created_at)}</div>
							</div>
						</div>

						<!-- Description -->
						<div class="mb-6">
							<h3 class="mb-3 text-lg font-semibold text-gray-900">Description</h3>
							<p class="leading-relaxed text-gray-700">{item.description}</p>
						</div>

						<!-- More Info -->
						<div class="mb-6">
							<h3 class="mb-3 text-lg font-semibold text-gray-900">More information</h3>
							<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Status</div>
									<div class="font-medium capitalize text-gray-900">{item.status}</div>
								</div>
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Condition</div>
									<div class="font-medium text-gray-900">{item.condition}</div>
								</div>
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Category</div>
									<div class="font-medium text-gray-900">{item.category}</div>
								</div>
								{#if item.location}
									<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
										<div class="text-xs text-gray-500">Location</div>
										<div class="flex items-center font-medium text-gray-900">
											<svg
												class="mr-1 h-4 w-4 text-gray-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
												></path>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
												></path>
											</svg>
											{item.location}
										</div>
									</div>
								{/if}
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Item ID</div>
									<div class="break-all font-mono text-sm text-gray-900">{item.id}</div>
								</div>
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Created</div>
									<div class="font-medium text-gray-900">
										{new Date(item.created_at).toLocaleString()}
									</div>
								</div>
								<div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
									<div class="text-xs text-gray-500">Updated</div>
									<div class="font-medium text-gray-900">
										{new Date(item.updated_at).toLocaleString()}
									</div>
								</div>
							</div>
						</div>

						<!-- Stats -->
						<div class="grid grid-cols-2 gap-4 border-t border-gray-200 py-4">
							<div class="text-center">
								<div class="text-2xl font-bold text-gray-900">{item.views}</div>
								<div class="text-sm text-gray-500">Views</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-gray-900">{0}</div>
								<div class="text-sm text-gray-500">Offers</div>
							</div>
						</div>
					</div>

					<!-- Owner Info -->
					<div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
						<h3 class="mb-4 text-lg font-semibold text-gray-900">Posted by</h3>
						<div
							class="flex cursor-pointer items-center space-x-4 rounded-lg p-2 transition-colors hover:bg-gray-50"
							onclick={() => {
								const targetId = item?.owner?.id || item?.user_id;
								if (targetId) goto(`/user/${targetId}`);
							}}
							onkeydown={(e) => {
								if (e.key === 'Enter' || e.key === ' ') {
									const targetId = item?.owner?.id || item?.user_id;
									if (targetId) {
										e.preventDefault();
										goto(`/user/${targetId}`);
									}
								}
							}}
							role="button"
							tabindex="0"
						>
							<div
								class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-red-500 to-red-600"
							>
								<span class="font-semibold text-white">
									{item.owner?.name?.charAt(0) || 'U'}
								</span>
							</div>
							<div class="flex-1">
								<div class="font-semibold text-gray-900 transition-colors hover:text-red-600">
									{item.owner?.name || item.owner_name || 'User'}
								</div>
								<div class="text-sm text-gray-500">
									{#if item.owner?.rating}
										⭐ {item.owner.rating.toFixed(1)} rating
									{:else}
										Member
									{/if}
								</div>
							</div>
							<svg
								class="h-5 w-5 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 5l7 7-7 7"
								></path>
							</svg>
						</div>
					</div>

					<!-- Action Buttons -->
					<div class="space-y-3">
						{#if isAuthenticated}
							{#if item.user_id !== user?.id}
								<button
									onclick={handleMakeOffer}
									class="w-full rounded-xl bg-red-600 px-6 py-4 text-lg font-semibold text-white shadow-sm transition-colors hover:bg-red-700 hover:shadow-md"
								>
									Make an Offer
								</button>
								<button
									onclick={handleContactOwner}
									class="w-full rounded-xl bg-gray-100 px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-200"
								>
									Contact Owner
								</button>
							{:else}
								<div class="rounded-xl border border-blue-200 bg-blue-50 p-4 text-center">
									<p class="font-medium text-blue-800">This is your item</p>
									<p class="mt-1 text-sm text-blue-600">
										You cannot make an offer on your own item
									</p>
								</div>
							{/if}
						{:else}
							<!-- eslint-disable-next-line -->
							<a
								href="/sign-in-up"
								class="block w-full rounded-xl bg-red-600 px-6 py-4 text-center text-lg font-semibold text-white shadow-sm transition-colors hover:bg-red-700 hover:shadow-md"
							>
								Sign in to Make Offer
							</a>
						{/if}
					</div>
				</div>
			</div>

			<!-- Related Items -->
			{#if relatedItems.length}
				<div class="mt-10">
					<h3 class="mb-4 text-xl font-semibold text-gray-900">Similar items</h3>
					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
						{#each relatedItems as ri (ri.id)}
							<!-- eslint-disable-next-line -->
							<a
								href="/item/{ri.id}"
								class="block overflow-hidden rounded-xl border border-gray-200 bg-white text-left shadow-sm transition hover:shadow-md"
							>
								<img
									src={ri.images[0] || 'https://via.placeholder.com/400x300?text=No+Image'}
									alt={ri.title}
									class="h-40 w-full object-cover"
								/>
								<div class="p-4">
									<div class="mb-1 line-clamp-1 font-medium text-gray-900">{ri.title}</div>
									<div class="line-clamp-2 text-sm text-gray-600">{ri.description}</div>
								</div>
							</a>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>

<!-- Trade Offer Modal -->
{#if item}
	{#key item?.id}
		<TradeOfferModal
			bind:isOpen={showTradeModal}
			targetItem={item}
			on:tradeCreated={handleTradeCreated}
		/>
	{/key}
{/if}
