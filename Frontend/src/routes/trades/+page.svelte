<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { tradeService } from '$lib/services/tradeService';
	import { itemService } from '$lib/services/itemService';
import { userService } from '$lib/services/userService';
	import LoadingSpinner from '../components/LoadingSpinner.svelte';
	import RatingModal from '../components/RatingModal.svelte';
	import type { User } from '$lib/types/auth';
	import type { Trade } from '$lib/types/trades';
	import type { Item } from '$lib/types/items';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let isLoading = $state(true);
	let selectedTab = $state('received');
	let trades: Trade[] = $state([]);
	let error: string | null = $state(null);
	let showRatingModal = $state(false);
	let selectedTradeForRating: Trade | null = $state(null);
	let rateeUserForRating: { id: string; name: string } | null = $state(null);
	let userRatingsMap = $state<Map<string, boolean>>(new Map()); // Map of tradeId -> hasRated

	const tabs = [
		{ id: 'received', label: 'Received Offers', count: 0 },
		{ id: 'sent', label: 'Sent Offers', count: 0 },
		{ id: 'active', label: 'Active Trades', count: 0 },
		{ id: 'completed', label: 'Completed', count: 0 }
	];

	let filteredTrades = $derived(trades.filter(trade => {
		if (selectedTab === 'received') {
			// Only show non-completed trades in received offers
			return trade.toUserId === user?.id && trade.status !== 'completed';
		}
		if (selectedTab === 'sent') {
			// Only show non-completed trades in sent offers
			return trade.fromUserId === user?.id && trade.status !== 'completed';
		}
		if (selectedTab === 'active') {
			return trade.status === 'active' || trade.status === 'accepted';
		}
		if (selectedTab === 'completed') {
			return trade.status === 'completed';
		}
		return true;
	}));

	function getTradeDirection(trade: Trade): 'received' | 'sent' {
		if (!user) return 'received';
		return trade.toUserId === user.id ? 'received' : 'sent';
	}

	async function loadTrades() {
		if (!user) return;
		
		try {
			isLoading = true;
			error = null;
			
			// Add timeout to prevent infinite loading
			const timeoutPromise = new Promise((_, reject) => 
				setTimeout(() => reject(new Error('Request timeout')), 10000)
			);
			
			const tradesPromise = tradeService.getTrades({ userId: user.id });
			const allTrades = await Promise.race([tradesPromise, timeoutPromise]) as Trade[];
			
			// Enhance trades with item and user details
			const enhancedTrades = await Promise.all(
				allTrades.map(async (trade) => {
					try {
						const [fromItem, toItem, fromUser, toUser] = await Promise.all([
							itemService.getItemById(trade.fromItemId),
							itemService.getItemById(trade.toItemId),
							userService.getUserById(trade.fromUserId),
							userService.getUserById(trade.toUserId)
						]);
						
						return {
							...trade,
						fromItem: fromItem ? {
								id: fromItem.id,
								title: fromItem.title,
								image: fromItem.images?.[0]
						} : undefined,
							toItem: toItem ? {
								id: toItem.id,
								title: toItem.title,
								image: toItem.images?.[0]
							} : undefined,
							fromUser: fromUser ? { id: fromUser.id, name: fromUser.name } : undefined,
							toUser: toUser ? { id: toUser.id, name: toUser.name } : undefined
						};
					} catch (err) {
						console.error('Error loading item details for trade:', trade.id, err);
						return trade;
					}
				})
			);
			
			trades = enhancedTrades;
			
			// Check which trades the user has already rated
			if (user) {
				const ratingsChecks = await Promise.all(
					trades
						.filter(t => t.status === 'completed')
						.map(async (trade) => {
							const hasRated = await tradeService.checkUserRated(trade.id, user.id);
							return [trade.id, hasRated] as [string, boolean];
						})
				);
				userRatingsMap = new Map(ratingsChecks);
			}
			
			// Update tab counts - exclude completed from received/sent counts
			tabs[0].count = trades.filter(t => t.toUserId === user!.id && t.status !== 'completed').length;
			tabs[1].count = trades.filter(t => t.fromUserId === user!.id && t.status !== 'completed').length;
			tabs[2].count = trades.filter(t => t.status === 'active' || t.status === 'accepted').length;
			tabs[3].count = trades.filter(t => t.status === 'completed').length;
		} catch (err) {
			console.error('Error loading trades:', err);
			error = (err as Error).message === 'Request timeout' 
				? 'Request timed out. Please check your connection and try again.'
				: 'Failed to load trades. Please try again.';
			trades = [];
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		const unsubscribe = authStore.subscribe(async (authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			isLoading = authState.isLoading;
			
			// Redirect if not authenticated
			if (!authState.isLoading && !authState.isAuthenticated) {
				goto('/sign-in-up');
			} else if (authState.isAuthenticated && authState.user) {
				// Load trades when user is authenticated
				await loadTrades();
			}
		});
		return unsubscribe;
	});

	async function handleAcceptTrade(trade: Trade) {
		if (!user) return;
		
		try {
			await tradeService.acceptTrade(trade.id, user.id);
			await loadTrades(); // Reload trades
		} catch (error) {
			console.error('Error accepting trade:', error);
		}
	}

	async function handleRejectTrade(trade: Trade) {
		if (!user) return;
		
		try {
			await tradeService.rejectTrade(trade.id, user.id);
			await loadTrades(); // Reload trades
		} catch (error) {
			console.error('Error rejecting trade:', error);
		}
	}

	async function handleCompleteTrade(trade: Trade) {
		if (!user) return;
		
		try {
			// Complete trade - status will automatically be set to 'completed'
			await tradeService.completeTrade(trade.id, user.id);
			await loadTrades(); // Reload trades
		} catch (error) {
			console.error('Error completing trade:', error);
		}
	}

	function handleMessageTrade(trade: Trade) {
		// Navigate to messages page with trade ID
		goto(`/messages?trade=${trade.id}`);
	}

	function handleRateUser(trade: Trade) {
		if (!user) return;
		
		const rateeUserId = trade.toUserId === user.id ? trade.fromUserId : trade.toUserId;
		const rateeUser = trade.toUserId === user.id ? trade.fromUser : trade.toUser;
		
		selectedTradeForRating = trade;
		rateeUserForRating = rateeUser ? { id: rateeUserId, name: rateeUser.name } : { id: rateeUserId, name: 'User' };
		showRatingModal = true;
	}

	async function handleRated() {
		// Mark trade as rated in the map
		if (selectedTradeForRating) {
			userRatingsMap.set(selectedTradeForRating.id, true);
		}
		// Reload trades after rating to refresh data
		await loadTrades();
		selectedTradeForRating = null;
		rateeUserForRating = null;
	}
</script>

<div class="p-4 lg:p-6">
	<!-- Header removed per request -->

	{#if isLoading}
		<LoadingSpinner size="large" message="Loading your trades..." />
	{:else if isAuthenticated}
		<!-- Tabs -->
		<div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-6 lg:mb-8">
			<div class="border-b border-gray-200">
				<nav class="-mb-px flex overflow-x-auto px-4 lg:px-6">
					{#each tabs as tab}
						<button
							onclick={() => selectedTab = tab.id}
							class="flex items-center space-x-2 py-4 px-3 lg:px-6 border-b-2 font-medium text-sm transition-colors whitespace-nowrap
								{selectedTab === tab.id 
									? 'border-red-500 text-red-600' 
									: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							<span>{tab.label}</span>
							<span class="bg-gray-100 text-gray-600 py-1 px-2 rounded-full text-xs font-semibold">
								{tab.count}
							</span>
						</button>
					{/each}
				</nav>
			</div>
		</div>

		<!-- Loading State -->
		{#if isLoading}
			<LoadingSpinner size="large" message="Loading trades..." />
		{:else if error}
			<div class="text-center py-16">
				<div class="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md mx-auto">
					<svg class="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
					</svg>
					<h3 class="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h3>
					<p class="text-gray-600 mb-4">{error}</p>
					<button 
						onclick={loadTrades}
						class="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
					>
						Try Again
					</button>
				</div>
			</div>
		{:else if filteredTrades.length === 0}
			<div class="text-center py-16">
				<svg class="mx-auto h-16 w-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
				</svg>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">No {selectedTab} trades</h3>
				<p class="text-gray-500">You don't have any {selectedTab} trades yet.</p>
			</div>
		{:else}
			<!-- Trades List -->
			<div class="space-y-4 lg:space-y-6">
				{#each filteredTrades as trade}
				<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 lg:p-6 hover:shadow-md transition-shadow">
					<div class="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-4 space-y-4 lg:space-y-0">
						<div class="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
							<!-- My Item -->
							<div class="flex items-center space-x-3">
								<img 
									src={trade.fromItem?.image || 'https://via.placeholder.com/64x64?text=No+Image'} 
									alt={trade.fromItem?.title || 'Item'}
									class="w-12 h-12 sm:w-16 sm:h-16 rounded-lg object-cover"
								/>
								<div>
									<p class="text-xs sm:text-sm text-gray-500">Your item</p>
									<p class="font-medium text-gray-900 text-sm sm:text-base">{trade.fromItem?.title || 'Unknown Item'}</p>
								</div>
							</div>

							<!-- Arrow -->
							<svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
							</svg>

							<!-- Offered Item -->
							<div class="flex items-center space-x-3">
								<img 
									src={trade.toItem?.image || 'https://via.placeholder.com/64x64?text=No+Image'} 
									alt={trade.toItem?.title || 'Item'}
									class="w-12 h-12 sm:w-16 sm:h-16 rounded-lg object-cover"
								/>
								<div>
									<p class="text-xs sm:text-sm text-gray-500">
										{trade.toUserId === user?.id ? 'Offered by' : 'Offering to'}
									</p>
									<p class="font-medium text-gray-900 text-sm sm:text-base">{trade.toItem?.title || 'Unknown Item'}</p>
								</div>
							</div>
						</div>

						<!-- Status Badge -->
					<span class="px-3 py-1 rounded-full text-xs font-semibold self-start
						{trade.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
						 trade.status === 'active' || trade.status === 'accepted' ? 'bg-green-100 text-green-800' :
						 trade.status === 'completed' ? 'bg-blue-100 text-blue-800' :
						 trade.status === 'rejected' ? 'bg-red-50 text-red-700' :
						 'bg-gray-100 text-gray-800'}"
					>
							{trade.status === 'accepted' ? 'Active' : trade.status.charAt(0).toUpperCase() + trade.status.slice(1)}
						</span>
					</div>

					<!-- User Info -->
					<div class="flex items-center space-x-3 mb-4">
					<img 
						src={getTradeDirection(trade) === 'received' ? (trade.fromUser?.avatar || 'https://via.placeholder.com/32') : (trade.toUser?.avatar || 'https://via.placeholder.com/32')} 
						alt={getTradeDirection(trade) === 'received' ? (trade.fromUser?.name || 'User') : (trade.toUser?.name || 'User')}
						class="w-8 h-8 rounded-full object-cover"
					/>
						<div>
						<p class="font-medium text-gray-900">
							{getTradeDirection(trade) === 'received' ? (trade.fromUser?.name || 'User') : (trade.toUser?.name || 'User')}
						</p>
							<div class="flex items-center space-x-1">
								<svg class="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
								</svg>
							<span class="text-sm text-gray-600">
								{getTradeDirection(trade) === 'received' ? (trade.fromUser?.rating ?? '—') : (trade.toUser?.rating ?? '—')}
							</span>
							</div>
						</div>
					</div>

					<!-- Message -->
					<div class="bg-gray-50 rounded-lg p-4 mb-4">
						<p class="text-gray-700 text-sm">{trade.message}</p>
					</div>

					<!-- Meeting Info (for active trades) -->
					{#if (trade.status === 'active' || trade.status === 'accepted') && trade.meetingLocation}
						<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
							<div class="flex items-center space-x-2 mb-2">
								<svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
								</svg>
								<span class="font-medium text-green-800">Meeting Scheduled</span>
							</div>
							<p class="text-green-700 text-sm">{trade.meetingLocation}</p>
							<p class="text-green-700 text-sm">{trade.meetingTime}</p>
						</div>
					{/if}

					<!-- Actions -->
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
						<div class="text-sm text-gray-500">
						{getTradeDirection(trade) === 'received' ? 'Received' : 'Sent'} {new Date(trade.createdAt).toLocaleString()}
							{#if trade.expiresAt}
							• Expires {new Date(trade.expiresAt).toLocaleString()}
							{/if}
						</div>
						
						<div class="flex flex-wrap items-center gap-2">
						{#if trade.status === 'pending' && getTradeDirection(trade) === 'received'}
								<button 
									onclick={() => handleAcceptTrade(trade)}
									class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700 transition-colors shadow-sm hover:shadow-md"
								>
									Accept
								</button>
								<button 
									onclick={() => handleRejectTrade(trade)}
									class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors shadow-sm hover:shadow-md"
								>
									Reject
								</button>
							{:else if trade.status === 'active' || trade.status === 'accepted'}
								<button 
									onclick={() => handleCompleteTrade(trade)}
									class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
								>
									Mark Complete
								</button>
							{/if}

						{#if trade.status === 'completed' && user && !userRatingsMap.get(trade.id)}
							<button 
								onclick={() => handleRateUser(trade)}
								class="bg-yellow-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors flex items-center gap-2"
							>
								<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
								</svg>
								Rate User
							</button>
						{:else if trade.status === 'completed' && user && userRatingsMap.get(trade.id)}
							<span class="text-sm text-gray-500 italic">Already rated</span>
						{/if}
							
							<button 
								onclick={() => handleMessageTrade(trade)}
								class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors"
							>
								Message
							</button>
						</div>
					</div>
				</div>
			{/each}
			</div>
		{/if}
	{/if}
</div>

<!-- Rating Modal -->
{#if selectedTradeForRating && rateeUserForRating && user}
	<RatingModal 
		bind:isOpen={showRatingModal}
		tradeId={selectedTradeForRating.id}
		raterUserId={user.id}
		rateeUserId={rateeUserForRating.id}
		rateeUserName={rateeUserForRating.name}
		on:rated={handleRated}
	/>
{/if}
