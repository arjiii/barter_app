<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { itemService } from '$lib/services/itemService';
	import PostItemModal from '../components/PostItemModal.svelte';
	import LoadingSpinner from '../components/LoadingSpinner.svelte';
	import type { User } from '$lib/types/auth';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let isLoading = $state(true);
	let selectedTab = $state('active');
	let showPostModal = $state(false);
	let editItem: any = $state(null);
	let deleteConfirmItem: any = $state(null);

	let tabs = $state([
		{ id: 'active', label: 'Active Items', count: 0 },
		{ id: 'pending', label: 'Pending Trades', count: 0 },
		{ id: 'completed', label: 'Completed', count: 0 },
		{ id: 'drafts', label: 'Drafts', count: 0 }
	]);

	type MyItem = {
		id: string;
		title: string;
		description: string;
		category: string;
		condition: string;
		image: string;
		status: string;
		views: number;
		offers: number;
		posted: string;
	};
	let myItems: MyItem[] = $state([]);
	let filteredItems = $derived(
		myItems.filter((item) => {
			if (selectedTab === 'active') return item.status === 'available';
			if (selectedTab === 'pending') return item.status === 'pending';
			if (selectedTab === 'completed') return item.status === 'completed';
			if (selectedTab === 'drafts') return item.status === 'draft';
			return true;
		})
	);

	async function loadMyItems() {
		if (!user) return;
		isLoading = true;
		try {
			// Add timeout to prevent infinite loading
			const timeoutPromise = new Promise((_, reject) =>
				setTimeout(() => reject(new Error('Request timeout')), 10000)
			);

			const itemsPromise = itemService.getItems({ userId: user.id });
			const items = (await Promise.race([itemsPromise, timeoutPromise])) as any[];

			// Extra safety: ensure only current user's items are shown even if API ignores filter
			const ownItems = (items || []).filter(
				(it: any) => it.userId === user.id || it.user_id === user.id
			);

			myItems = ownItems.map((i: any) => ({
				id: i.id,
				title: i.title,
				description: i.description,
				category: i.category,
				condition: i.condition,
				image: i.images[0] || '',
				status: i.status,
				views: i.views || 0,
				offers: 0,
				posted:
					(i.createdAt
						? new Date(i.createdAt)
						: i.created_at
							? new Date(i.created_at)
							: null
					)?.toLocaleDateString() || ''
			}));

			// Update tab counts
			tabs = tabs.map((tab) => ({
				...tab,
				count: myItems.filter((item) => {
					if (tab.id === 'active') return item.status === 'available';
					if (tab.id === 'pending') return item.status === 'pending';
					if (tab.id === 'completed') return item.status === 'completed';
					if (tab.id === 'drafts') return item.status === 'draft';
					return false;
				}).length
			}));
		} catch (error) {
			console.error('Error loading my items:', error);
			// Set empty items to prevent infinite loading
			myItems = [];
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		const unsubscribe = authStore.subscribe((authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			isLoading = authState.isLoading;

			if (!authState.isLoading && !authState.isAuthenticated) {
				goto('/sign-in-up');
			} else if (authState.isAuthenticated && authState.user) {
				loadMyItems();
			}
		});

		// Initialize auth if not already done
		authStore.initializeAuth();

		return unsubscribe;
	});

	function handlePostItem() {
		goto('/item/create');
	}

	function handleItemPosted() {
		// Reload items after posting
		loadMyItems();
	}

	async function handleEditItem(item: any) {
		// Fetch full item details
		try {
			const fullItem = await itemService.getItemById(item.id);
			if (fullItem) {
				editItem = fullItem;
				showPostModal = true;
			}
		} catch (error) {
			console.error('Error loading item for edit:', error);
		}
	}

	async function handleDeleteItem(item: any) {
		if (confirm(`Are you sure you want to delete "${item.title}"? This action cannot be undone.`)) {
			try {
				const deleted = await itemService.deleteItem(item.id);
				if (deleted) {
					// Remove item from local state
					myItems = myItems.filter((i) => i.id !== item.id);
					// Reload to update counts
					loadMyItems();
				} else {
					alert('Failed to delete item. Please try again.');
				}
			} catch (error) {
				console.error('Error deleting item:', error);
				alert('Failed to delete item. Please try again.');
			}
		}
	}

	function handleItemUpdated() {
		loadMyItems();
		editItem = null;
	}

	function handleViewOffers(item: any) {
		// TODO: Navigate to offers page
		console.log('View offers for item:', item.id);
	}
</script>

<div class="p-4 lg:p-6">
	<!-- Header removed per request -->

	{#if isLoading}
		<LoadingSpinner size="large" message="Loading your items..." />
	{:else if isAuthenticated}
		<!-- Tabs -->
		<div class="mb-6 rounded-xl border border-gray-200 bg-white shadow-sm lg:mb-8">
			<div class="flex items-center justify-between px-4 py-2 lg:px-6">
				<nav class="-mb-px flex overflow-x-auto">
					{#each tabs as tab}
						<button
							onclick={() => (selectedTab = tab.id)}
							class="flex items-center space-x-2 whitespace-nowrap border-b-2 px-3 py-4 text-sm font-medium transition-colors lg:px-6
								{selectedTab === tab.id
								? 'border-red-500 text-red-600'
								: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
						>
							<span>{tab.label}</span>
							<span class="rounded-full bg-gray-100 px-2 py-1 text-xs font-semibold text-gray-600">
								{tab.count}
							</span>
						</button>
					{/each}
				</nav>
				<button
					onclick={handlePostItem}
					class="ml-4 whitespace-nowrap rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700"
				>
					+ Post New Item
				</button>
			</div>
			<div class="border-b border-gray-200"></div>
		</div>

		<!-- Action Bar -->
		<div class="mb-6 flex items-center justify-between">
			<div class="text-sm text-gray-600">
				{filteredItems.length}
				{selectedTab} item{filteredItems.length !== 1 ? 's' : ''}
			</div>
			<!-- Button moved into tabs container -->
		</div>

		<!-- Items Grid -->
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6">
			{#each filteredItems as item}
				<div
					class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
				>
					<!-- Item Image -->
					<div class="relative overflow-hidden bg-gray-200">
						<img src={item.image} alt={item.title} class="h-48 w-full object-cover" />
						<div class="absolute right-3 top-3">
							<span
								class="rounded-full bg-white bg-opacity-90 px-2 py-1 text-xs font-medium text-gray-800"
							>
								{item.condition}
							</span>
						</div>
					</div>

					<!-- Item Details -->
					<div class="p-4 lg:p-5">
						<div class="mb-3">
							<h3 class="mb-2 line-clamp-1 text-lg font-semibold text-gray-900">{item.title}</h3>
							<p class="line-clamp-2 text-sm text-gray-600">{item.description}</p>
						</div>

						<!-- Stats -->
						<div class="mb-4 flex items-center justify-between text-sm text-gray-500">
							<div class="flex items-center space-x-4">
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
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
										></path>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
										></path>
									</svg>
									<span>{item.views} views</span>
								</div>
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
											d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
										></path>
									</svg>
									<span>{item.offers} offers</span>
								</div>
							</div>
							<span class="text-xs">{item.posted}</span>
						</div>

						<!-- Actions -->
						<div
							class="flex flex-col space-y-2 border-t border-gray-100 pt-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
						>
							<div class="flex space-x-3">
								<button
									onclick={() => handleEditItem(item)}
									class="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
								>
									Edit
								</button>
								<button
									onclick={() => handleDeleteItem(item)}
									class="text-sm font-medium text-red-600 transition-colors hover:text-red-700"
								>
									Delete
								</button>
							</div>
							{#if item.offers > 0}
								<button
									onclick={() => handleViewOffers(item)}
									class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-red-700 hover:shadow-md"
								>
									View Offers ({item.offers})
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Empty State -->
		{#if filteredItems.length === 0}
			<div class="py-12 text-center">
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
						d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
					></path>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-gray-900">No {selectedTab} items</h3>
				<p class="mt-1 text-sm text-gray-500">
					{selectedTab === 'active'
						? "You haven't posted any items yet."
						: `You don't have any ${selectedTab} items.`}
				</p>
				{#if selectedTab === 'active'}
					<button
						onclick={handlePostItem}
						class="mt-4 rounded-lg bg-red-600 px-4 py-2 font-medium text-white transition-colors hover:bg-red-700"
					>
						Post Your First Item
					</button>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<!-- Post Item Modal -->
<PostItemModal
	bind:isOpen={showPostModal}
	{editItem}
	on:itemPosted={handleItemPosted}
	on:itemUpdated={handleItemUpdated}
/>
