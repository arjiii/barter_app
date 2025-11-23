<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { userService } from '$lib/services/userService';
	import { tradeService } from '$lib/services/tradeService';
	import { itemService } from '$lib/services/itemService';
	import type { User } from '$lib/types/auth';

	let profileUser: User | null = $state(null);
	let currentUser: User | null = $state(null);
	let isLoading = $state(true);
	let error: string | null = $state(null);
	let ratings = $state<any[]>([]);
	let userItems = $state<any[]>([]);
	let userTrades = $state<any[]>([]);
	let isLoadingRatings = $state(true);
	let isLoadingItems = $state(true);
	let isLoadingTrades = $state(true);

	let userId = $derived($page.params.id);

	async function loadUserProfile() {
		if (!userId) {
			error = 'User ID not found';
			isLoading = false;
			return;
		}

		try {
			isLoading = true;
			error = null;

			// Load user profile
			profileUser = await userService.getUserById(userId);
			if (!profileUser) {
				error = 'User not found';
				isLoading = false;
				return;
			}

			// Load user ratings, items, and trades in parallel
			await Promise.all([
				loadRatings(),
				loadUserItems(),
				loadUserTrades()
			]);
		} catch (err) {
			console.error('Error loading user profile:', err);
			error = 'Failed to load user profile';
		} finally {
			isLoading = false;
		}
	}

	async function loadRatings() {
		if (!userId) return;
		try {
			isLoadingRatings = true;
			const userRatings = await tradeService.getUserRatings(userId);
			
			// Enhance ratings with rater user info
			const enhancedRatings = await Promise.all(
				userRatings.map(async (rating) => {
					try {
						const rater = await userService.getUserById(rating.rater_user_id);
						return {
							...rating,
							raterName: rater?.name || 'User',
							raterId: rater?.id || rating.rater_user_id
						};
					} catch (err) {
						console.error('Error loading rater info:', err);
						return {
							...rating,
							raterName: 'User',
							raterId: rating.rater_user_id
						};
					}
				})
			);
			
			ratings = enhancedRatings;
		} catch (error) {
			console.error('Error loading ratings:', error);
			ratings = [];
		} finally {
			isLoadingRatings = false;
		}
	}

	async function loadUserItems() {
		if (!userId) return;
		try {
			isLoadingItems = true;
			const items = await itemService.getItems({ userId });
			userItems = items.filter(item => item.status === 'available').slice(0, 6);
		} catch (error) {
			console.error('Error loading user items:', error);
			userItems = [];
		} finally {
			isLoadingItems = false;
		}
	}

	async function loadUserTrades() {
		if (!userId) return;
		try {
			isLoadingTrades = true;
			// Get all trades where user is involved
			const allTrades = await tradeService.getTrades();
			userTrades = allTrades
				.filter(trade => 
					(trade.fromUserId === userId || trade.toUserId === userId) &&
					trade.status === 'completed'
				)
				.slice(0, 10);
		} catch (error) {
			console.error('Error loading user trades:', error);
			userTrades = [];
		} finally {
			isLoadingTrades = false;
		}
	}

	onMount(() => {
		const unsubscribe = authStore.subscribe((authState) => {
			currentUser = authState.user;
		});
		
		loadUserProfile();
		
		return unsubscribe;
	});
</script>

<div class="p-4 lg:p-6">
	{#if isLoading}
		<div class="flex items-center justify-center min-h-[400px]">
			<div class="text-center">
				<svg class="animate-spin h-8 w-8 text-red-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				<p class="text-gray-600">Loading profile...</p>
			</div>
		</div>
	{:else if error}
		<div class="text-center py-12">
			<svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
			</svg>
			<h3 class="text-lg font-medium text-gray-900 mb-2">{error}</h3>
			<button 
				onclick={() => goto('/discovery')}
				class="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
			>
				Go to Discovery
			</button>
		</div>
	{:else if profileUser}
		<!-- Profile Header -->
		<div class="bg-gradient-to-r from-red-600 to-red-700 rounded-2xl shadow-lg mb-6 p-8 text-white">
			<div class="flex items-center space-x-6">
				<div class="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-4xl font-bold">
					{profileUser.name?.charAt(0)?.toUpperCase() || 'U'}
				</div>
				<div class="flex-1">
					<h1 class="text-3xl font-bold mb-2">{profileUser.name || 'User'}</h1>
					<p class="text-red-100 flex items-center mb-4">
						<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
						</svg>
						{profileUser.email}
					</p>
					{#if ratings.length > 0}
						<div class="flex items-center space-x-4">
							<div class="flex items-center bg-white bg-opacity-20 px-4 py-2 rounded-lg">
								<svg class="w-5 h-5 text-yellow-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
								</svg>
								<span class="font-semibold">
									{(ratings.reduce((sum, r) => sum + r.score, 0) / ratings.length).toFixed(1)}
								</span>
								<span class="text-red-100 ml-2">({ratings.length} {ratings.length === 1 ? 'review' : 'reviews'})</span>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Ratings Section -->
		<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6 hover:shadow-xl transition-shadow">
			<div class="flex items-center mb-6">
				<div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
					<svg class="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
						<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
					</svg>
				</div>
				<h2 class="text-xl font-bold text-gray-900">Ratings & Reviews</h2>
			</div>
			{#if isLoadingRatings}
				<p class="text-gray-600">Loading ratings...</p>
			{:else if ratings.length === 0}
				<div class="text-center py-8">
					<svg class="mx-auto h-12 w-12 text-gray-300 mb-4" fill="currentColor" viewBox="0 0 20 20">
						<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
					</svg>
					<p class="text-gray-500">No ratings yet. This user hasn't received any reviews.</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each ratings as rating}
						<div class="border border-gray-200 rounded-xl p-5 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm">
							<div class="flex items-start justify-between mb-3">
								<div class="flex items-center space-x-4">
									<div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center shadow-md">
										<span class="text-white font-bold text-lg">
											{rating.raterName?.charAt(0)?.toUpperCase() || 'U'}
										</span>
									</div>
									<div>
										<p class="font-semibold text-gray-900 text-lg">{rating.raterName || 'User'}</p>
										<p class="text-xs text-gray-500 flex items-center mt-1">
											<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
											</svg>
											{new Date(rating.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
										</p>
									</div>
								</div>
								<div class="flex items-center space-x-1 bg-yellow-50 px-3 py-2 rounded-lg">
									{#each [1, 2, 3, 4, 5] as star}
										<svg class="w-5 h-5 {rating.score >= star ? 'text-yellow-400' : 'text-gray-300'}" fill="currentColor" viewBox="0 0 20 20">
											<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
										</svg>
									{/each}
									<span class="ml-2 text-sm font-bold text-gray-800">{rating.score}/5</span>
								</div>
							</div>
							{#if rating.feedback}
								<div class="mt-3 pl-16">
									<p class="text-gray-700 text-sm leading-relaxed bg-gray-50 p-3 rounded-lg border-l-4 border-red-500">
										{rating.feedback}
									</p>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- User's Active Items -->
		<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6 hover:shadow-xl transition-shadow">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center">
					<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
						<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
						</svg>
					</div>
					<h2 class="text-xl font-bold text-gray-900">Active Items</h2>
				</div>
			</div>
			{#if isLoadingItems}
				<p class="text-gray-600">Loading items...</p>
			{:else if userItems.length === 0}
				<p class="text-gray-500 text-center py-8">No active items available.</p>
			{:else}
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each userItems as item}
						<div 
							class="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
							onclick={() => goto(`/item/${item.id}`)}
						>
							<img src={item.images?.[0] || ''} alt={item.title} class="w-full h-32 object-cover" />
							<div class="p-3">
								<h3 class="font-semibold text-gray-900 text-sm mb-1 line-clamp-1">{item.title}</h3>
								<p class="text-xs text-gray-500 line-clamp-2">{item.description}</p>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Recent Completed Trades -->
		<div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow">
			<div class="flex items-center mb-6">
				<div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
					<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
					</svg>
				</div>
				<h2 class="text-xl font-bold text-gray-900">Recent Completed Trades</h2>
			</div>
			{#if isLoadingTrades}
				<p class="text-gray-600">Loading trades...</p>
			{:else if userTrades.length === 0}
				<p class="text-gray-500 text-center py-8">No completed trades yet.</p>
			{:else}
				<div class="space-y-3">
					{#each userTrades as trade}
						<div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
							<div class="flex items-center justify-between">
								<div class="flex-1">
									<p class="text-sm font-medium text-gray-900">
										Trade #{trade.id.slice(0, 8)}...
									</p>
									<p class="text-xs text-gray-500 mt-1">
										Completed on {new Date(trade.created_at || Date.now()).toLocaleDateString()}
									</p>
								</div>
								<span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
									Completed
								</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>










