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

	let filteredTrades = $derived(
		trades.filter((trade) => {
			if (selectedTab === 'received') {
				// Only show non-completed trades in received offers
				return trade.to_user_id === user?.id && trade.status !== 'completed';
			}
			if (selectedTab === 'sent') {
				// Only show non-completed trades in sent offers
				return trade.from_user_id === user?.id && trade.status !== 'completed';
			}
			if (selectedTab === 'active') {
				return trade.status === 'active' || trade.status === 'accepted';
			}
			if (selectedTab === 'completed') {
				return trade.status === 'completed';
			}
			return true;
		})
	);

	function getTradeDirection(trade: Trade): 'received' | 'sent' {
		if (!user) return 'received';
		return trade.to_user_id === user.id ? 'received' : 'sent';
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
			const allTrades = (await Promise.race([tradesPromise, timeoutPromise])) as Trade[];

			// Enhance trades with item and user details
			const enhancedTrades = await Promise.all(
				allTrades.map(async (trade) => {
					try {
						const [fromItem, toItem, fromUser, toUser] = await Promise.all([
							itemService.getItemById(trade.from_item_id),
							itemService.getItemById(trade.to_item_id),
							userService.getUserById(trade.from_user_id),
							userService.getUserById(trade.to_user_id)
						]);

						return {
							...trade,
							from_item: fromItem
								? {
										id: fromItem.id,
										title: fromItem.title,
										image: fromItem.images?.[0]
									}
								: undefined,
							to_item: toItem
								? {
										id: toItem.id,
										title: toItem.title,
										image: toItem.images?.[0]
									}
								: undefined,
							from_user: fromUser
								? {
										id: fromUser.id,
										name: fromUser.name,
										rating: fromUser.rating,
										avatar: fromUser.avatar
									}
								: undefined,
							to_user: toUser
								? { id: toUser.id, name: toUser.name, rating: toUser.rating, avatar: toUser.avatar }
								: undefined
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
				const currentUserId = user.id;
				const ratingsChecks = await Promise.all(
					trades
						.filter((t) => t.status === 'completed')
						.map(async (trade) => {
							const hasRated = await tradeService.checkUserRated(trade.id, currentUserId);
							return [trade.id, hasRated] as [string, boolean];
						})
				);
				userRatingsMap = new Map(ratingsChecks);
			}

			// Update tab counts - exclude completed from received/sent counts
			tabs[0].count = trades.filter(
				(t) => t.to_user_id === user!.id && t.status !== 'completed'
			).length;
			tabs[1].count = trades.filter(
				(t) => t.from_user_id === user!.id && t.status !== 'completed'
			).length;
			tabs[2].count = trades.filter((t) => t.status === 'active' || t.status === 'accepted').length;
			tabs[3].count = trades.filter((t) => t.status === 'completed').length;
		} catch (err) {
			console.error('Error loading trades:', err);
			error =
				(err as Error).message === 'Request timeout'
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
			await tradeService.acceptTrade(trade.id);
			await loadTrades(); // Reload trades
		} catch (error) {
			console.error('Error accepting trade:', error);
		}
	}

	async function handleRejectTrade(trade: Trade) {
		if (!user) return;

		try {
			await tradeService.rejectTrade(trade.id);
			await loadTrades(); // Reload trades
		} catch (error) {
			console.error('Error rejecting trade:', error);
		}
	}

	async function handleCompleteTrade(trade: Trade) {
		if (!user) return;

		try {
			// Complete trade - status will automatically be set to 'completed'
			await tradeService.completeTrade(trade.id);
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

		let rateeUserId: string;
		let rateeUser: typeof trade.from_user;

		if (trade.to_user_id === user.id) {
			rateeUserId = trade.from_user_id;
			rateeUser = trade.from_user;
		} else {
			rateeUserId = trade.to_user_id;
			rateeUser = trade.to_user;
		}

		selectedTradeForRating = trade;
		rateeUserForRating = rateeUser
			? { id: rateeUserId, name: rateeUser.name }
			: { id: rateeUserId, name: 'User' };
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
		<div class="mb-6 rounded-xl border border-gray-200 bg-white shadow-sm lg:mb-8">
			<div class="border-b border-gray-200">
				<nav class="-mb-px flex overflow-x-auto px-4 lg:px-6">
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
			</div>
		</div>

		<!-- Loading State -->
		{#if isLoading}
			<LoadingSpinner size="large" message="Loading trades..." />
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
						onclick={loadTrades}
						class="rounded-lg bg-red-600 px-6 py-2 font-medium text-white transition-colors hover:bg-red-700"
					>
						Try Again
					</button>
				</div>
			</div>
		{:else if filteredTrades.length === 0}
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
						d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
					></path>
				</svg>
				<h3 class="mb-2 text-lg font-semibold text-gray-900">No {selectedTab} trades</h3>
				<p class="text-gray-500">You don't have any {selectedTab} trades yet.</p>
			</div>
		{:else}
			<!-- Trades List -->
			<div class="space-y-4 lg:space-y-6">
				{#each filteredTrades as trade}
					<div
						class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md lg:p-6"
					>
						<div
							class="mb-4 flex flex-col space-y-4 lg:flex-row lg:items-start lg:justify-between lg:space-y-0"
						>
							<div
								class="flex flex-col items-start space-y-4 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0"
							>
								<!-- My Item -->
								<div class="flex items-center space-x-3">
									<img
										src={trade.from_item?.image ||
											'https://via.placeholder.com/64x64?text=No+Image'}
										alt={trade.from_item?.title || 'Item'}
										class="h-12 w-12 rounded-lg object-cover sm:h-16 sm:w-16"
									/>
									<div>
										<p class="text-xs text-gray-500 sm:text-sm">Your item</p>
										<p class="text-sm font-medium text-gray-900 sm:text-base">
											{trade.from_item?.title || 'Unknown Item'}
										</p>
									</div>
								</div>

								<!-- Arrow -->
								<svg
									class="h-5 w-5 flex-shrink-0 text-gray-400 sm:h-6 sm:w-6"
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

								<!-- Offered Item -->
								<div class="flex items-center space-x-3">
									<img
										src={trade.to_item?.image || 'https://via.placeholder.com/64x64?text=No+Image'}
										alt={trade.to_item?.title || 'Item'}
										class="h-12 w-12 rounded-lg object-cover sm:h-16 sm:w-16"
									/>
									<div>
										<p class="text-xs text-gray-500 sm:text-sm">
											{trade.to_user_id === user?.id ? 'Offered by' : 'Offering to'}
										</p>
										<p class="text-sm font-medium text-gray-900 sm:text-base">
											{trade.to_item?.title || 'Unknown Item'}
										</p>
									</div>
								</div>
							</div>

							<!-- Status Badge -->
							<span
								class="self-start rounded-full px-3 py-1 text-xs font-semibold
						{trade.status === 'pending'
									? 'bg-yellow-100 text-yellow-800'
									: trade.status === 'active' || trade.status === 'accepted'
										? 'bg-green-100 text-green-800'
										: trade.status === 'completed'
											? 'bg-blue-100 text-blue-800'
											: trade.status === 'rejected'
												? 'bg-red-50 text-red-700'
												: 'bg-gray-100 text-gray-800'}"
							>
								{trade.status === 'accepted'
									? 'Active'
									: trade.status.charAt(0).toUpperCase() + trade.status.slice(1)}
							</span>
						</div>

						<!-- User Info -->
						<div class="mb-4 flex items-center space-x-3">
							<div
								class="flex cursor-pointer items-center space-x-3 transition-opacity hover:opacity-80"
								role="button"
								tabindex="0"
								onclick={() => {
									const targetUserId =
										getTradeDirection(trade) === 'received'
											? trade.from_user?.id
											: trade.to_user?.id;
									if (targetUserId) goto(`/user/${targetUserId}`);
								}}
								onkeydown={(e) => {
									if (e.key === 'Enter' || e.key === ' ') {
										const targetUserId =
											getTradeDirection(trade) === 'received'
												? trade.from_user?.id
												: trade.to_user?.id;
										if (targetUserId) goto(`/user/${targetUserId}`);
									}
								}}
							>
								<img
									src={getTradeDirection(trade) === 'received'
										? trade.from_user?.avatar || 'https://via.placeholder.com/32'
										: trade.to_user?.avatar || 'https://via.placeholder.com/32'}
									alt={getTradeDirection(trade) === 'received'
										? trade.from_user?.name || 'User'
										: trade.to_user?.name || 'User'}
									class="h-8 w-8 rounded-full object-cover"
								/>
								<div>
									<p class="font-medium text-gray-900">
										{getTradeDirection(trade) === 'received'
											? trade.from_user?.name || 'User'
											: trade.to_user?.name || 'User'}
									</p>
									<div class="flex items-center space-x-1">
										<svg class="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
											<path
												d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
											></path>
										</svg>
										<span class="text-sm text-gray-600">
											{getTradeDirection(trade) === 'received'
												? (trade.from_user?.rating ?? '—')
												: (trade.to_user?.rating ?? '—')}
										</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Message -->
						<div class="mb-4 rounded-lg bg-gray-50 p-4">
							<p class="text-sm text-gray-700">{trade.message}</p>
						</div>

						<!-- Meeting Info (for active trades) -->
						{#if (trade.status === 'active' || trade.status === 'accepted') && trade.meeting_location}
							<div class="mb-4 rounded-lg border border-green-200 bg-green-50 p-4">
								<div class="mb-2 flex items-center space-x-2">
									<svg
										class="h-5 w-5 text-green-600"
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
									<span class="font-medium text-green-800">Meeting Scheduled</span>
								</div>
								<p class="text-sm text-green-700">{trade.meeting_location}</p>
								<p class="text-sm text-green-700">{trade.meeting_time}</p>
							</div>
						{/if}

						<!-- Actions -->
						<div
							class="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
						>
							<div class="text-sm text-gray-500">
								{getTradeDirection(trade) === 'received' ? 'Received' : 'Sent'}
								{new Date(trade.created_at).toLocaleString()}
								{#if trade.expires_at}
									• Expires {new Date(trade.expires_at).toLocaleString()}
								{/if}
							</div>

							<div class="flex flex-wrap items-center gap-2">
								{#if trade.status === 'pending' && getTradeDirection(trade) === 'received'}
									<button
										onclick={() => handleAcceptTrade(trade)}
										class="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-green-700 hover:shadow-md"
									>
										Accept
									</button>
									<button
										onclick={() => handleRejectTrade(trade)}
										class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-red-700 hover:shadow-md"
									>
										Reject
									</button>
								{:else if trade.status === 'active' || trade.status === 'accepted'}
									<button
										onclick={() => handleCompleteTrade(trade)}
										class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 hover:shadow-md"
									>
										Mark Complete
									</button>
								{/if}

								{#if trade.status === 'completed' && user && !userRatingsMap.get(trade.id)}
									<button
										onclick={() => handleRateUser(trade)}
										class="flex items-center gap-2 rounded-lg bg-yellow-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-yellow-600"
									>
										<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
											<path
												d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
											></path>
										</svg>
										Rate User
									</button>
								{:else if trade.status === 'completed' && user && userRatingsMap.get(trade.id)}
									<span class="text-sm italic text-gray-500">Already rated</span>
								{/if}

								<button
									onclick={() => handleMessageTrade(trade)}
									class="rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-300"
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
