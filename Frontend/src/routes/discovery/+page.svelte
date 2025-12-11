<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { authService } from '$lib/services/authService';
	import { itemService } from '$lib/services/itemService';
	import { tradeService } from '$lib/services/tradeService';
	import { messageService } from '$lib/services/messageService';
	import { seedService } from '$lib/services/seedService';
	import LoadingSpinner from '../components/LoadingSpinner.svelte';
	import TradeOfferModal from '../components/TradeOfferModal.svelte';
	import { calculateDistance, formatDistance } from '$lib/utils/distance';
	import type { User } from '$lib/types/auth';
	import type { Item, Category } from '$lib/types/items';
	import type { Trade } from '$lib/types/trades';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let authInitialized = $state(false);
	let searchQuery = $state('');
	let selectedCategory = $state('all');
	let desiredQuery = $state('');
	let filterByLocation = $state(false);
	let items: Item[] = $state([]);
	let categories: Category[] = $state([]);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let showTradeModal = $state(false);
	let selectedItem: Item | null = $state(null);
	let selectedRadius = $state(50); // Default 50km

	let filteredItems = $derived(
		(() => {
			// First, filter items based on search, category, and desired criteria
			const currentUser = user as User | null;
			let filtered = items.filter((item) => {
				const matchesSearch =
					item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
					item.description.toLowerCase().includes(searchQuery.toLowerCase());
				const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
				// AI-ish preference boost: if desiredQuery provided, prefer items containing it
				const wants = desiredQuery.trim().toLowerCase();
				const matchesDesired = wants
					? item.title.toLowerCase().includes(wants) ||
						item.description.toLowerCase().includes(wants) ||
						item.category.toLowerCase().includes(wants)
					: true;

				return matchesSearch && matchesCategory && matchesDesired;
			});

			// Calculate distances if user has coordinates
			if (
				isAuthenticated &&
				currentUser &&
				currentUser.latitude != null &&
				currentUser.longitude != null
			) {
				const userLat = currentUser.latitude;
				const userLng = currentUser.longitude;
				filtered = filtered.map((item) => {
					if (item.latitude && item.longitude) {
						const distance = calculateDistance(userLat, userLng, item.latitude, item.longitude);
						return { ...item, distance };
					}
					return item;
				});

				// Filter by radius if location filter is active
				if (filterByLocation) {
					filtered = filtered.filter((item) => {
						if (item.distance !== undefined) {
							return item.distance <= selectedRadius;
						}
						// Keep items without distance for now, they will be sorted to the bottom

						if (item.distance !== undefined) {
							return item.distance <= selectedRadius;
						}
						return true; // Keep items with unknown location at the bottom
					});
				}
			}

			// Sort by distance if location filter is active
			if (filterByLocation && isAuthenticated && currentUser?.latitude && currentUser?.longitude) {
				filtered = filtered.sort((a, b) => {
					// 1. Sort by distance availability (items with distance come first)
					const aHasDist = a.distance !== undefined;
					const bHasDist = b.distance !== undefined;

					if (aHasDist && !bHasDist) return -1;
					if (!aHasDist && bHasDist) return 1;

					// 2. Sort by distance value (ascending)
					if (aHasDist && bHasDist) {
						// If distances are essentially equal (within 10 meters), sort by date
						if (Math.abs(a.distance! - b.distance!) < 0.01) {
							return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
						}
						return a.distance! - b.distance!;
					}

					// 3. Secondary sort for items without distance: Newest first
					return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
				});
			}

			return filtered;
		})()
	);

	function toggleLocationFilter() {
		if (!isAuthenticated || !user) {
			// Prompt user to sign in if they want to use location filter
			goto('/sign-in-up');
			return;
		}

		// Check if user has coordinates set
		if ((!user.latitude || !user.longitude) && !filterByLocation) {
			// Show message that user needs to set location first
			if (
				confirm(
					'Please set your location in your profile settings to use location-based filtering. Go to profile?'
				)
			) {
				goto('/profile');
			}
			return;
		}

		filterByLocation = !filterByLocation;
	}

	async function loadData() {
		try {
			isLoading = true;
			error = null;

			// Load items and categories in parallel
			const [itemsResult, categoriesResult] = await Promise.all([
				itemService.getItems({ status: 'available' }),
				itemService.getCategories()
			]);

			// itemService.getItems() returns Item[] directly
			if (Array.isArray(itemsResult)) {
				items = itemsResult;
			} else {
				error = 'Failed to load items';
			}

			// itemService.getCategories() returns Category[] directly
			if (Array.isArray(categoriesResult)) {
				categories = [
					{ id: 'all', name: 'All Categories', createdAt: new Date() },
					...categoriesResult
				];
			}
		} catch (err) {
			console.error('Error loading data:', err);
			error = 'Failed to load items. Please try again.';
		} finally {
			isLoading = false;
		}
	}

	async function handleItemClick(item: Item) {
		selectedItem = item;
		showTradeModal = false;
		// Navigate to item detail page or show modal
		await goto(`/item/${item.id}`);
	}

	async function handleTradeOffer(item: Item, event: MouseEvent) {
		event.stopPropagation();
		if (!isAuthenticated) {
			await goto('/sign-in-up');
			return;
		}
		selectedItem = item;
		showTradeModal = true;
	}

	async function handleTradeCreated() {
		showTradeModal = false;
		selectedItem = null;
		// Optionally reload items or show success message
	}

	onMount(() => {
		// Subscribe to auth store
		const unsubscribe = authStore.subscribe((state) => {
			user = state.user;
			isAuthenticated = state.isAuthenticated;
			authInitialized = !state.isLoading;
		});

		// Load initial data
		loadData();

		return () => {
			unsubscribe();
		};
	});
</script>

<!-- Header -->
<!-- Removed header per request -->

<div class="p-4 lg:p-6">
	{#if !authInitialized}
		<div class="py-12 text-center">
			<div class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-red-600"></div>
			<p class="text-gray-600">Loading...</p>
		</div>
	{:else}
		<div>
			<!-- Search and Filters -->
			<div class="mb-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm lg:mb-8 lg:p-6">
				<div class="flex flex-col gap-4 lg:flex-row">
					<!-- Search Bar -->
					<div class="flex-1">
						<div class="relative">
							<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
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
										d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
									></path>
								</svg>
							</div>
							<input
								type="text"
								bind:value={searchQuery}
								placeholder="Search items..."
								class="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
							/>
						</div>
					</div>

					<!-- Category Filter -->
					<div class="lg:w-64">
						<select
							bind:value={selectedCategory}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
						>
							{#each categories as category (category.id)}
								<option value={category.id}>{category.name}</option>
							{/each}
						</select>
					</div>

					<!-- Desired item (AI preference) -->
					<div class="flex-1">
						<input
							type="text"
							bind:value={desiredQuery}
							placeholder="I want to trade for... (e.g., guitar, laptop)"
							class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
						/>
					</div>

					<!-- Action Buttons -->
					<div class="flex space-x-3">
						<!-- Location Filter Toggle -->
						<div class="flex items-center gap-2">
							<button
								onclick={toggleLocationFilter}
								class={`flex items-center rounded-xl px-4 py-3 font-medium transition-all duration-200 ${
									filterByLocation
										? 'bg-red-600 text-white hover:bg-red-700'
										: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
								}`}
								title={isAuthenticated && user && user.location
									? `Show items near ${user.location}`
									: 'Filter by your location'}
							>
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
								<span class="hidden sm:inline">Near Me</span>
							</button>

							{#if filterByLocation}
								<div
									class="flex items-center gap-3 rounded-xl border border-gray-300 bg-white px-4 py-2 shadow-sm"
								>
									<span class="whitespace-nowrap text-sm font-medium text-gray-700">Radius:</span>
									<input
										type="range"
										min="1"
										max="500"
										step="1"
										bind:value={selectedRadius}
										class="h-2 w-24 cursor-pointer appearance-none rounded-lg bg-gray-200 accent-red-600 sm:w-32"
									/>
									<div class="flex items-center gap-1">
										<input
											type="number"
											min="1"
											max="1000"
											bind:value={selectedRadius}
											class="w-16 rounded-lg border border-gray-200 px-2 py-1 text-center text-sm font-medium text-gray-900 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
										/>
										<span class="text-xs text-gray-500">km</span>
									</div>
								</div>
							{/if}
						</div>

						<!-- Refresh Button -->
						<button
							onclick={loadData}
							class="flex items-center rounded-xl bg-gray-100 px-4 py-3 font-medium text-gray-700 transition-all duration-200 hover:bg-gray-200"
							title="Refresh items"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								></path>
							</svg>
							<span class="hidden sm:inline">Refresh</span>
						</button>
					</div>
				</div>
			</div>

			<!-- Loading State -->
			{#if isLoading}
				<LoadingSpinner size="large" message="Loading items..." />
			{:else if error}
				<div class="py-16 text-center">
					<div class="mx-auto max-w-md rounded-xl border border-red-200 bg-red-50 p-6">
						<svg
							class="mx-auto mb-4 h-12 w-12 text-red-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
							></path>
						</svg>
						<h3 class="mb-2 text-lg font-semibold text-gray-900">Something went wrong</h3>
						<p class="mb-4 text-gray-600">{error}</p>
						<button
							onclick={loadData}
							class="rounded-lg bg-red-600 px-6 py-2 font-medium text-white transition-colors hover:bg-red-700"
						>
							Try Again
						</button>
					</div>
				</div>
			{:else if filteredItems.length === 0}
				<div class="py-16 text-center">
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
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						></path>
					</svg>
					<h3 class="mb-2 text-lg font-semibold text-gray-900">No items found</h3>
					<p class="mb-6 text-gray-500">Try adjusting your search or filter criteria.</p>
					{#if searchQuery || selectedCategory !== 'all' || filterByLocation}
						<button
							onclick={() => {
								searchQuery = '';
								selectedCategory = 'all';
								filterByLocation = false;
							}}
							class="rounded-lg bg-red-600 px-6 py-2 font-medium text-white transition-colors hover:bg-red-700"
						>
							Clear filters
						</button>
					{/if}
				</div>
			{:else}
				<!-- Items Grid -->
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6 xl:grid-cols-4">
					{#each filteredItems as item (item.id)}
						{@const postedAgo = itemService.formatPostedAgo(item.created_at)}
						<div
							class="group cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:shadow-lg"
							role="button"
							tabindex="0"
							onclick={() => handleItemClick(item)}
							onkeydown={(event) => {
								if (event.key === 'Enter' || event.key === ' ') {
									event.preventDefault();
									handleItemClick(item);
								}
							}}
						>
							<!-- Item Image -->
							<div class="relative overflow-hidden bg-gray-200">
								<img
									src={item.images[0] || 'https://via.placeholder.com/400x300?text=No+Image'}
									alt={item.title}
									class="h-48 w-full object-cover transition-transform duration-200 group-hover:scale-105"
								/>
								<div class="absolute right-3 top-3 flex flex-col items-end gap-2">
									<span
										class="rounded-full bg-white bg-opacity-90 px-2 py-1 text-xs font-medium text-gray-800"
									>
										{item.condition}
									</span>
									{#if filterByLocation && item.distance !== undefined}
										<span
											class="flex items-center gap-1 rounded-full bg-red-600 bg-opacity-90 px-2 py-1 text-xs font-medium text-white"
										>
											<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
											{formatDistance(item.distance)}
										</span>
									{/if}
								</div>
							</div>

							<!-- Item Details -->
							<div class="p-4 lg:p-5">
								<div class="mb-3">
									<h3
										class="mb-2 line-clamp-1 text-lg font-semibold text-gray-900 transition-colors group-hover:text-red-600"
									>
										{item.title}
									</h3>
									<p class="line-clamp-2 text-sm text-gray-600">{item.description}</p>
								</div>

								<div class="mb-3 flex items-center justify-between text-sm text-gray-500">
									<div class="flex items-center space-x-3">
										<div class="flex items-center">
											<svg
												class="mr-1 h-4 w-4 text-gray-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
												></path>
											</svg>
											<span>{item.category}</span>
										</div>
										{#if postedAgo}
											<div class="flex items-center">
												<svg
													class="mr-1 h-4 w-4 text-gray-400"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
													></path>
												</svg>
												<span>{postedAgo}</span>
											</div>
										{/if}
									</div>
								</div>

								<div class="border-t border-gray-100 pt-3">
									<div class="mb-3 flex items-center justify-between">
										<button
											type="button"
											class="flex cursor-pointer items-center transition-colors hover:text-red-600 focus:outline-none"
											onclick={(e) => {
												e.stopPropagation();
												const targetId = item.owner?.id || item.user_id;
												if (targetId) {
													goto(`/user/${targetId}`);
												}
											}}
											aria-label={`View ${item.owner?.name || 'user'} profile`}
										>
											<div
												class="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-red-500 to-red-600"
											>
												<span class="text-xs font-medium text-white">
													{item.owner?.name?.charAt(0)?.toUpperCase() || '?'}
												</span>
											</div>
											<span class="text-sm font-medium text-gray-600 hover:text-red-600"
												>{item.owner?.name || item.owner_name || 'User'}</span
											>
										</button>
									</div>

									<!-- Action Buttons -->
									<div class="flex space-x-2">
										<button
											onclick={(e) => {
												e.stopPropagation();
												handleItemClick(item);
											}}
											class="flex-1 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
										>
											View Details
										</button>
										{#if isAuthenticated && item.user_id !== user?.id}
											<button
												onclick={(e) => handleTradeOffer(item, e)}
												class="flex-1 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
											>
												Trade Offer
											</button>
										{:else if !isAuthenticated}
											<a
												href="/sign-in-up"
												class="flex-1 rounded-lg bg-gray-300 px-3 py-2 text-center text-sm font-medium text-gray-600"
											>
												Sign in to trade
											</a>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<!-- Trade Offer Modal -->
{#key selectedItem?.id}
	<TradeOfferModal
		bind:isOpen={showTradeModal}
		targetItem={selectedItem}
		on:tradeCreated={handleTradeCreated}
	/>
{/key}
