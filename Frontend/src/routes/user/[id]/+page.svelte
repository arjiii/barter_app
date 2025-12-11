<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { userService } from '$lib/services/userService';
	import { tradeService } from '$lib/services/tradeService';
	import { itemService } from '$lib/services/itemService';
	import { messageService } from '$lib/services/messageService';
	import ReportUserModal from '../../components/ReportUserModal.svelte';
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
	let isStartingChat = $state(false);
	let showReportModal = $state(false);

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
			await Promise.all([loadRatings(), loadUserItems(), loadUserTrades()]);
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
			userItems = items.filter((item) => item.status === 'available').slice(0, 6);
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
				.filter(
					(trade) =>
						(trade.from_user_id === userId || trade.to_user_id === userId) &&
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

	async function ensureRecipientHasAnchorItem(): Promise<string | null> {
		if (userItems.length > 0) {
			return userItems[0]?.id || null;
		}

		try {
			const items = await itemService.getItems({ userId });
			const available = items.find((item) => item.status === 'available');
			if (available) {
				userItems = [available, ...userItems];
				return available.id;
			}
		} catch (error) {
			console.warn('Failed to fetch items for chat context:', error);
		}

		return null;
	}

	async function handleMessageUser() {
		if (!profileUser) return;
		if (!currentUser) {
			goto('/sign-in-up');
			return;
		}
		if (currentUser.id === profileUser.id) {
			return;
		}

		try {
			isStartingChat = true;

			const trades = await tradeService.getTrades({ userId: currentUser.id });
			const existingTrade = trades.find(
				(trade) =>
					(trade.from_user_id === currentUser?.id && trade.to_user_id === profileUser?.id) ||
					(trade.to_user_id === currentUser?.id && trade.from_user_id === profileUser?.id)
			);

			if (existingTrade) {
				await goto(`/messages?trade=${existingTrade.id}`);
				return;
			}

			const anchorItemId = await ensureRecipientHasAnchorItem();
			if (!anchorItemId) {
				alert('This neighbor has no active listings yet, so messaging is unavailable for now.');
				return;
			}

			const quickMessage = `Hi ${profileUser.name || 'there'}! I'd love to connect.`;
			const createdTrade = await tradeService.createTrade({
				to_user_id: profileUser.id,
				from_item_id: anchorItemId,
				to_item_id: anchorItemId,
				message: quickMessage
			});

			if (createdTrade) {
				try {
					await messageService.createMessage({
						trade_id: createdTrade.id,
						receiver_id: profileUser.id,
						content: quickMessage
					});
				} catch (err) {
					console.warn('Failed to send initial chat message from profile page:', err);
				}

				await goto(`/messages?trade=${createdTrade.id}`);
			} else {
				alert('Unable to start a chat right now. Please try again in a moment.');
			}
		} catch (error) {
			console.error('Error starting chat from profile page:', error);
			alert('Something went wrong while trying to open a chat.');
		} finally {
			isStartingChat = false;
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
		<div class="flex min-h-[400px] items-center justify-center">
			<div class="text-center">
				<svg
					class="mx-auto mb-4 h-8 w-8 animate-spin text-red-600"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
				<p class="text-gray-600">Loading profile...</p>
			</div>
		</div>
	{:else if error}
		<div class="py-12 text-center">
			<svg
				class="mx-auto mb-4 h-12 w-12 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				></path>
			</svg>
			<h3 class="mb-2 text-lg font-medium text-gray-900">{error}</h3>
			<button
				onclick={() => goto('/discovery')}
				class="mt-4 rounded-lg bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700"
			>
				Go to Discovery
			</button>
		</div>
	{:else if profileUser}
		<!-- Profile Header -->
		<div class="mb-6 rounded-2xl bg-gradient-to-r from-red-600 to-red-700 p-8 text-white shadow-lg">
			<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
				<div class="flex items-center space-x-6">
					<div
						class="flex h-24 w-24 items-center justify-center rounded-full bg-white bg-opacity-20 text-4xl font-bold"
					>
						{profileUser.name?.charAt(0)?.toUpperCase() || 'U'}
					</div>
					<div>
						<h1 class="mb-2 text-3xl font-bold">{profileUser.name || 'User'}</h1>
						<p class="mb-4 flex items-center text-red-100">
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
								></path>
							</svg>
							{profileUser.email}
						</p>
						{#if ratings.length > 0}
							<div class="flex items-center space-x-4">
								<div class="flex items-center rounded-lg bg-white bg-opacity-20 px-4 py-2">
									<svg class="mr-2 h-5 w-5 text-yellow-300" fill="currentColor" viewBox="0 0 20 20">
										<path
											d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
										></path>
									</svg>
									<span class="font-semibold">
										{(ratings.reduce((sum, r) => sum + r.score, 0) / ratings.length).toFixed(1)}
									</span>
									<span class="ml-2 text-red-100"
										>({ratings.length} {ratings.length === 1 ? 'review' : 'reviews'})</span
									>
								</div>
							</div>
						{/if}
					</div>
				</div>
				<div class="flex flex-wrap gap-3">
					<button
						type="button"
						disabled={isStartingChat || !currentUser || currentUser.id === profileUser.id}
						onclick={handleMessageUser}
						class="inline-flex items-center gap-2 rounded-xl bg-white bg-opacity-15 px-5 py-3 font-semibold text-gray-600 shadow-lg shadow-red-900/20 transition hover:bg-white hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-60"
					>
						{#if isStartingChat}
							<svg
								class="h-5 w-5 animate-spin text-current"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
							>
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke-width="4"></circle>
								<path
									class="opacity-75"
									d="M4 12a8 8 0 018-8"
									stroke-width="4"
									stroke-linecap="round"
								></path>
							</svg>
						{:else}
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
								/>
							</svg>
						{/if}
						Message {profileUser.name?.split(' ')?.[0] || 'User'}
					</button>
					<button
						type="button"
						onclick={() => (showReportModal = true)}
						class="inline-flex items-center gap-2 rounded-xl bg-red-900 bg-opacity-30 px-3 py-3 font-semibold text-white transition hover:bg-opacity-50"
						title="Report User"
					>
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Ratings Section -->
		<div
			class="mb-6 rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
		>
			<div class="mb-6 flex items-center">
				<div class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-100">
					<svg class="h-6 w-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
						></path>
					</svg>
				</div>
				<h2 class="text-xl font-bold text-gray-900">Ratings & Reviews</h2>
			</div>
			{#if isLoadingRatings}
				<p class="text-gray-600">Loading ratings...</p>
			{:else if ratings.length === 0}
				<div class="py-8 text-center">
					<svg class="mx-auto mb-4 h-12 w-12 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
						></path>
					</svg>
					<p class="text-gray-500">No ratings yet. This user hasn't received any reviews.</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each ratings as rating}
						<div
							class="rounded-xl border border-gray-200 p-5 shadow-sm transition-all hover:border-gray-300 hover:bg-gray-50"
						>
							<div class="mb-3 flex items-start justify-between">
								<div class="flex items-center space-x-4">
									<div
										class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-red-500 to-red-600 shadow-md"
									>
										<span class="text-lg font-bold text-white">
											{rating.raterName?.charAt(0)?.toUpperCase() || 'U'}
										</span>
									</div>
									<div>
										<p class="text-lg font-semibold text-gray-900">{rating.raterName || 'User'}</p>
										<p class="mt-1 flex items-center text-xs text-gray-500">
											<svg
												class="mr-1 h-3 w-3"
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
											{new Date(rating.created_at).toLocaleDateString('en-US', {
												year: 'numeric',
												month: 'long',
												day: 'numeric'
											})}
										</p>
									</div>
								</div>
								<div class="flex items-center space-x-1 rounded-lg bg-yellow-50 px-3 py-2">
									{#each [1, 2, 3, 4, 5] as star}
										<svg
											class="h-5 w-5 {rating.score >= star ? 'text-yellow-400' : 'text-gray-300'}"
											fill="currentColor"
											viewBox="0 0 20 20"
										>
											<path
												d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
											></path>
										</svg>
									{/each}
									<span class="ml-2 text-sm font-bold text-gray-800">{rating.score}/5</span>
								</div>
							</div>
							{#if rating.feedback}
								<div class="mt-3 pl-16">
									<p
										class="rounded-lg border-l-4 border-red-500 bg-gray-50 p-3 text-sm leading-relaxed text-gray-700"
									>
										{rating.feedback}
									</p>
								</div>
							{/if}
							{#if rating.blockchain_tx_hash}
								<div class="mt-2 pl-16 text-xs text-gray-400">
									<a
										href={`https://sepolia.etherscan.io/tx/${rating.blockchain_tx_hash}`}
										target="_blank"
										rel="noopener noreferrer"
										class="flex items-center gap-1 hover:text-red-500 hover:underline"
									>
										<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"
											><path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
											></path></svg
										>
										Blockchain Verified: {rating.blockchain_tx_hash.slice(0, 10)}...{rating.blockchain_tx_hash.slice(
											-8
										)}
									</a>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- User's Active Items -->
		<div
			class="mb-6 rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
		>
			<div class="mb-6 flex items-center justify-between">
				<div class="flex items-center">
					<div class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
						<svg
							class="h-6 w-6 text-blue-600"
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
					</div>
					<h2 class="text-xl font-bold text-gray-900">Active Items</h2>
				</div>
			</div>
			{#if isLoadingItems}
				<p class="text-gray-600">Loading items...</p>
			{:else if userItems.length === 0}
				<p class="py-8 text-center text-gray-500">No active items available.</p>
			{:else}
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each userItems as item}
						<div
							class="cursor-pointer overflow-hidden rounded-lg border border-gray-200 transition-shadow hover:shadow-md"
							onclick={() => goto(`/item/${item.id}`)}
						>
							<img src={item.images?.[0] || ''} alt={item.title} class="h-32 w-full object-cover" />
							<div class="p-3">
								<h3 class="mb-1 line-clamp-1 text-sm font-semibold text-gray-900">{item.title}</h3>
								<p class="line-clamp-2 text-xs text-gray-500">{item.description}</p>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Recent Completed Trades -->
		<div
			class="rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
		>
			<div class="mb-6 flex items-center">
				<div class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
					<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						></path>
					</svg>
				</div>
				<h2 class="text-xl font-bold text-gray-900">Recent Completed Trades</h2>
			</div>
			{#if isLoadingTrades}
				<p class="text-gray-600">Loading trades...</p>
			{:else if userTrades.length === 0}
				<p class="py-8 text-center text-gray-500">No completed trades yet.</p>
			{:else}
				<div class="space-y-3">
					{#each userTrades as trade}
						<div class="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50">
							<div class="flex items-center justify-between">
								<div class="flex-1">
									<p class="text-sm font-medium text-gray-900">
										Trade #{trade.id.slice(0, 8)}...
									</p>
									<p class="mt-1 text-xs text-gray-500">
										Completed on {new Date(trade.created_at || Date.now()).toLocaleDateString()}
									</p>
									{#if trade.blockchain_tx_hash}
										<div class="mt-1 text-xs text-gray-400">
											<a
												href={`https://sepolia.etherscan.io/tx/${trade.blockchain_tx_hash}`}
												target="_blank"
												rel="noopener noreferrer"
												class="flex items-center gap-1 hover:text-red-500 hover:underline"
											>
												<svg
													class="h-3 w-3"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
													><path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
													></path></svg
												>
												Blockchain Verified: {trade.blockchain_tx_hash.slice(0, 10)}...{trade.blockchain_tx_hash.slice(
													-8
												)}
											</a>
										</div>
									{/if}
								</div>
								<span
									class="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800"
								>
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

{#if profileUser}
	<ReportUserModal
		bind:isOpen={showReportModal}
		reportedUserId={profileUser.id}
		reportedUserName={profileUser.name}
	/>
{/if}
