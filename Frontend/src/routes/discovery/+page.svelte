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

	let filteredItems = $derived(items.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        item.description.toLowerCase().includes(searchQuery.toLowerCase());
		const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    // AI-ish preference boost: if desiredQuery provided, prefer items containing it
    const wants = desiredQuery.trim().toLowerCase();
    const matchesDesired = wants ? (item.title.toLowerCase().includes(wants) || item.description.toLowerCase().includes(wants) || item.category.toLowerCase().includes(wants)) : true;
    
    // Location filter: if enabled, match user location with item location
    let matchesLocation = true;
    if (filterByLocation && isAuthenticated && user) {
      const userLocation = user.location?.trim().toLowerCase();
      const itemLocation = item.location?.trim().toLowerCase();
      
      if (userLocation) {
        // If user has location, filter items by location match
        matchesLocation = itemLocation ? itemLocation.includes(userLocation) || userLocation.includes(itemLocation) : false;
      } else {
        // If user doesn't have location, show all items (fallback)
        matchesLocation = true;
      }
    }
    
    return matchesSearch && matchesCategory && matchesDesired && matchesLocation;
	}));

	async function loadData() {
		try {
			console.log('Loading data...');
			isLoading = true;
			error = null;
			
			// Add timeout to prevent infinite loading
			const timeoutPromise = new Promise((_, reject) => 
				setTimeout(() => reject(new Error('Request timeout')), 10000)
			);
			
			// Load categories and items in parallel
			const dataPromise = Promise.all([
				itemService.getCategories(),
				itemService.getItems({ status: 'available' })
			]);
			
			const [categoriesData, itemsData] = await Promise.race([dataPromise, timeoutPromise]) as [Category[], Item[]];
			
			categories = [
				{ id: 'all', name: 'All Items', createdAt: new Date() }, 
				...categoriesData
			];
			items = itemsData;
			console.log('Loaded items:', items.length);
		} catch (err) {
			console.error('Error loading data:', err);
			error = (err as Error).message === 'Request timeout' 
				? 'Request timed out. Please check your connection and try again.'
				: 'Failed to load items. Please try again.';
			
			// Set default data to prevent empty state
			categories = [{ id: 'all', name: 'All Items', createdAt: new Date() }];
			items = [];
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		const unsubscribe = authStore.subscribe((authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			authInitialized = !authState.isLoading;
			console.log('Auth state changed:', authState);
		});
		// Initialize auth state
		authStore.initializeAuth();
		// Seed initial data and load dynamic data
		(async () => {
			await seedService.seedInitialData();
			await loadData();
		})();
		return unsubscribe;
	});

	function handleItemClick(item: Item) {
		goto(`/item/${item.id}`);
	}

	function handleTradeOffer(item: Item, event: Event) {
		event.stopPropagation(); // Prevent item click
		if (!isAuthenticated) {
			goto('/sign-in-up');
			return;
		}
		selectedItem = item;
		showTradeModal = true;
	}

	async function handleContactOwner(item: Item, event: Event) {
		event.stopPropagation();

		if (!isAuthenticated) {
			goto('/sign-in-up');
			return;
		}

		if (!user) return;

		const currentUserId = user.id; // Store in local variable for TypeScript

		try {
			// 1) Check for any existing trade between current user and item owner
			const trades = await tradeService.getTrades({ userId: currentUserId });
			const existingTrade = trades.find((t) => {
				return (
					(t.fromUserId === currentUserId && t.toUserId === item.userId) ||
					(t.toUserId === currentUserId && t.fromUserId === item.userId)
				);
			});

			if (existingTrade) {
				goto(`/messages?trade=${existingTrade.id}`);
				return;
			}

			// 2) No existing conversation: create a simple chat trade + first message
			const quickMessage =
				`Hi ${item.owner?.name || ''}, I'm interested in your "${item.title}".`.trim();

			const createdTrade = await tradeService.createTrade(currentUserId, {
				toUserId: item.userId,
				fromItemId: item.id,
				toItemId: item.id,
				message: quickMessage
			});

			if (createdTrade) {
				try {
					await messageService.createMessage(currentUserId, {
						tradeId: createdTrade.id,
						receiverId: item.userId,
						content: quickMessage
					});
				} catch (msgErr) {
					console.warn('Failed to create initial chat message (discovery):', msgErr);
				}

				goto(`/messages?trade=${createdTrade.id}`);
				return;
			}

			console.error('Failed to create quick chat trade from discovery');
		} catch (err) {
			console.error('Error contacting owner from discovery:', err);
		}
	}

	function handleTradeCreated(event: CustomEvent<Trade>) {
		console.log('Trade created:', event.detail);
		// Could show a success message or update UI
	}

	function toggleLocationFilter() {
		if (!isAuthenticated || !user) {
			// Prompt user to sign in if they want to use location filter
			goto('/sign-in-up');
			return;
		}
		
		const userLocation = user.location;
		if (!userLocation && !filterByLocation) {
			// Show message that user needs to set location first
			alert('Please set your location in your profile settings to use location-based filtering.');
			return;
		}
		
		filterByLocation = !filterByLocation;
	}

	async function createTestUser() {
		try {
			const result = await authService.createTestUser();
			if (result.success && result.user) {
				authStore.setUser(result.user);
				console.log('Test user created and logged in:', result.user);
			} else {
				console.error('Failed to create test user:', result.message);
			}
		} catch (error) {
			console.error('Error creating test user:', error);
		}
	}
</script>

<!-- Header -->
<!-- Removed header per request -->

<div class="p-4 lg:p-6">
	{#if !authInitialized}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
			<p class="text-gray-600">Loading...</p>
		</div>
	{:else}
	<div>
	<!-- Search and Filters -->
	<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 lg:p-6 mb-6 lg:mb-8">
		<div class="flex flex-col lg:flex-row gap-4">
			<!-- Search Bar -->
			<div class="flex-1">
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
						</svg>
					</div>
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Search items..."
						class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
					/>
				</div>
			</div>

			<!-- Category Filter -->
			<div class="lg:w-64">
				<select
					bind:value={selectedCategory}
					class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
				>
					{#each categories as category}
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
					class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
				/>
			</div>

			<!-- Action Buttons -->
			<div class="flex space-x-3">
				<!-- Location Filter Toggle -->
				<button 
					onclick={toggleLocationFilter}
					class={`px-4 py-3 rounded-xl transition-all duration-200 font-medium flex items-center ${
						filterByLocation 
							? 'bg-red-600 text-white hover:bg-red-700' 
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
					}`}
					title={isAuthenticated && user && user.location 
						? `Show items near ${user.location}` 
						: 'Filter by your location'}
				>
					<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
					</svg>
					<span class="hidden sm:inline">Near Me</span>
				</button>
				
				<!-- Refresh Button -->
				<button 
					onclick={loadData}
					class="bg-gray-100 text-gray-700 px-4 py-3 rounded-xl hover:bg-gray-200 transition-all duration-200 font-medium flex items-center"
					title="Refresh items"
				>
					<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
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
		<div class="text-center py-16">
			<div class="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md mx-auto">
				<svg class="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
				</svg>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button 
					onclick={loadData}
					class="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
				>
					Try Again
				</button>
			</div>
		</div>
	{:else if filteredItems.length === 0}
		<div class="text-center py-16">
			<svg class="mx-auto h-16 w-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
			</svg>
			<h3 class="text-lg font-semibold text-gray-900 mb-2">No items found</h3>
			<p class="text-gray-500 mb-6">Try adjusting your search or filter criteria.</p>
			{#if searchQuery || selectedCategory !== 'all' || filterByLocation}
				<button 
					onclick={() => { searchQuery = ''; selectedCategory = 'all'; filterByLocation = false; }}
					class="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
				>
					Clear filters
				</button>
			{/if}
		</div>
	{:else}
		<!-- Items Grid -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
			{#each filteredItems as item}
				<div
					class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 group cursor-pointer"
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
					<div class="relative bg-gray-200 overflow-hidden">
						<img 
							src={item.images[0] || 'https://via.placeholder.com/400x300?text=No+Image'} 
							alt={item.title}
							class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
						/>
						<div class="absolute top-3 right-3">
							<span class="bg-white bg-opacity-90 text-gray-800 text-xs px-2 py-1 rounded-full font-medium">
								{item.condition}
							</span>
						</div>
					</div>

					<!-- Item Details -->
					<div class="p-4 lg:p-5">
						<div class="mb-3">
							<h3 class="font-semibold text-gray-900 text-lg mb-2 line-clamp-1 group-hover:text-red-600 transition-colors">{item.title}</h3>
							<p class="text-gray-600 text-sm line-clamp-2">{item.description}</p>
						</div>
						
						<div class="flex items-center justify-between text-sm text-gray-500 mb-3">
							<div class="flex items-center space-x-3">
							<div class="flex items-center">
								<svg class="h-4 w-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
								</svg>
								<span>{item.category}</span>
							</div>
								<div class="flex items-center">
									<svg class="h-4 w-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
									</svg>
									<span>{item.postedAgo || 'Recently'}</span>
								</div>
							</div>
						</div>

						<div class="pt-3 border-t border-gray-100">
							<div class="flex items-center justify-between mb-3">
								<button
									type="button"
									class="flex items-center cursor-pointer hover:text-red-600 transition-colors focus:outline-none"
									onclick={(e) => {
										e.stopPropagation();
										if (item.owner?.id) {
											goto(`/user/${item.owner.id}`);
										}
									}}
									aria-label={`View ${item.owner?.name || 'user'} profile`}
								>
									<div class="w-6 h-6 bg-gradient-to-br from-red-500 to-red-600 rounded-full mr-2 flex items-center justify-center">
										<span class="text-xs text-white font-medium">
											{item.owner?.name?.charAt(0)?.toUpperCase() || '?'}
										</span>
									</div>
									<span class="text-sm text-gray-600 font-medium hover:text-red-600">{item.owner?.name || 'User'}</span>
								</button>
							</div>
							
							<!-- Action Buttons -->
							<div class="flex space-x-2">
								<button 
									onclick={(e) => {
										e.stopPropagation();
										handleItemClick(item);
									}}
									class="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-200 transition-colors font-medium"
								>
									View Details
								</button>
								{#if isAuthenticated && item.userId !== user?.id}
									<button
										onclick={(e) => handleTradeOffer(item, e)}
										class="flex-1 bg-red-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-red-700 transition-colors font-medium"
									>
										Trade Offer
									</button>
								{:else if !isAuthenticated}
									<button
										onclick={() => goto('/sign-in-up')}
										class="flex-1 bg-gray-300 text-gray-600 px-3 py-2 rounded-lg text-sm font-medium"
									>
										Sign in to trade
									</button>
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
<TradeOfferModal bind:isOpen={showTradeModal} targetItem={selectedItem} on:tradeCreated={handleTradeCreated} />

