<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { authService } from '$lib/services/authService';
	import { tradeService } from '$lib/services/tradeService';
	import { userService } from '$lib/services/userService';
	import type { User } from '$lib/types/auth';

	let user: User | null = $state(null);
	let isAuthenticated = $state(false);
	let isLoading = $state(true);
	let nameInput = $state('');
	let locationInput = $state('');
	let profileMsg: string | null = $state(null);
	let pwdMsg: string | null = $state(null);
	let oldPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let ratings: any[] = $state([]);
	let isLoadingRatings = $state(true);
	let isLocating = $state(false);
	let isEditingLocation = $state(false);

	async function loadRatings() {
		if (!user) return;
		try {
			isLoadingRatings = true;
			const userRatings = await tradeService.getUserRatings(user.id);

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

	onMount(() => {
		const unsubscribe = authStore.subscribe(async (authState) => {
			user = authState.user;
			isAuthenticated = authState.isAuthenticated;
			isLoading = authState.isLoading;
			if (authState.user) {
				nameInput = authState.user.name;
				locationInput = authState.user.location || '';
				if (authState.isAuthenticated) {
					await loadRatings();
				}
			}
			if (!authState.isLoading && !authState.isAuthenticated) {
				goto('/sign-in-up');
			}
		});
		return unsubscribe;
	});

	async function handleLocateMe() {
		if (!('geolocation' in navigator)) {
			profileMsg = 'Geolocation is not supported by your browser';
			return;
		}

		isLocating = true;
		profileMsg = null;
		isEditingLocation = false; // Lock it back when locating

		try {
			// Check permissions first
			if (navigator.permissions && navigator.permissions.query) {
				const result = await navigator.permissions.query({ name: 'geolocation' });
				if (result.state === 'denied') {
					profileMsg =
						'Location access is denied. Please enable permissions in your browser settings.';
					isLocating = false;
					return;
				}
			}

			navigator.geolocation.getCurrentPosition(
				async (position) => {
					const { latitude, longitude } = position.coords;
					try {
						// Use OpenStreetMap Nominatim for free reverse geocoding
						const response = await fetch(
							`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
						);
						const data = await response.json();
						const address = data.address;

						// Construct readable address
						// Prioritize city/municipality/town, then province/state
						const city =
							address.city ||
							address.town ||
							address.municipality ||
							address.village ||
							address.city_district;
						const state = address.state || address.province || address.region;
						const country = address.country;

						let locationString = '';
						if (city && state) {
							locationString = `${city}, ${state}`;
						} else if (city) {
							locationString = `${city}, ${country}`;
						} else if (state) {
							locationString = `${state}, ${country}`;
						} else {
							locationString = 'Unknown Location';
						}

						locationInput = locationString;

						// Auto-save the location update with coordinates
						const updated = await authService.updateProfile(
							nameInput.trim(),
							locationString,
							latitude,
							longitude
						);
						if (updated) {
							authStore.setUser(updated);
							profileMsg = 'Location updated successfully';
						} else {
							profileMsg = 'Failed to update location';
						}
					} catch (e) {
						console.error('Geocoding error:', e);
						profileMsg = 'Unable to retrieve address details';
					} finally {
						isLocating = false;
					}
				},
				(err) => {
					console.error('Geolocation error:', err);
					if (err.code === 1) profileMsg = 'Location access denied. Please enable permissions.';
					else if (err.code === 2) profileMsg = 'Location unavailable. Please try again.';
					else if (err.code === 3) profileMsg = 'Location request timed out.';
					else profileMsg = 'Unable to retrieve your location.';
					isLocating = false;
				},
				{
					enableHighAccuracy: true, // Force GPS/Wi-Fi for better accuracy
					timeout: 15000, // Give it a bit more time to find satellites
					maximumAge: 0 // Do not use cached position
				}
			);
		} catch (e) {
			console.error('Error checking permissions:', e);
			isLocating = false;
			profileMsg = 'Error checking location permissions.';
		}
	}

	async function handleSaveProfile() {
		profileMsg = null;
		if (!nameInput.trim()) {
			profileMsg = 'Name is required';
			return;
		}
		const updated = await authService.updateProfile(nameInput.trim(), locationInput.trim());
		if (updated) {
			authStore.setUser(updated);
			profileMsg = 'Profile updated successfully';
			isEditingLocation = false; // Lock after saving
		} else {
			profileMsg = 'Failed to update profile';
		}
	}

	async function handleChangePassword() {
		pwdMsg = null;
		if (!oldPassword || !newPassword) {
			pwdMsg = 'Enter old and new password';
			return;
		}
		if (newPassword !== confirmPassword) {
			pwdMsg = 'Passwords do not match';
			return;
		}
		const ok = await authService.changePassword(oldPassword, newPassword);
		pwdMsg = ok ? 'Password changed successfully' : 'Failed to change password';
		if (ok) {
			oldPassword = newPassword = confirmPassword = '';
		}
	}
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
	{:else if isAuthenticated && user}
		<!-- Profile Header -->
		<div class="mb-6 rounded-2xl bg-gradient-to-r from-red-600 to-red-700 p-8 text-white shadow-lg">
			<div class="flex items-center space-x-6">
				<div
					class="flex h-20 w-20 items-center justify-center rounded-full bg-white bg-opacity-20 text-3xl font-bold"
				>
					{user.name?.charAt(0)?.toUpperCase() || 'U'}
				</div>
				<div>
					<h1 class="mb-2 text-3xl font-bold">{user.name || 'User'}</h1>
					<p class="flex items-center text-red-100">
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
							></path>
						</svg>
						{user.email}
					</p>
				</div>
			</div>
		</div>

		<div class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
			<!-- Profile Section -->
			<div
				class="rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
			>
				<div class="mb-6 flex items-center">
					<div class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
						<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
							></path>
						</svg>
					</div>
					<h2 class="text-xl font-bold text-gray-900">Profile Information</h2>
				</div>
				<div class="space-y-4">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Email Address</label>
						<div class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-gray-700">
							{user.email}
						</div>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Display Name</label>
						<input
							type="text"
							class="w-full rounded-lg border border-gray-300 px-4 py-3 transition-all focus:border-red-500 focus:ring-2 focus:ring-red-500"
							bind:value={nameInput}
							placeholder="Enter your display name"
						/>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Location</label>
						<div class="flex gap-2">
							<div class="relative flex-1">
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
											d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
										></path>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
										></path>
									</svg>
								</div>
								<input
									type="text"
									readonly={!isEditingLocation}
									class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-10 {isEditingLocation
										? 'bg-white'
										: 'cursor-not-allowed bg-gray-50 text-gray-600'}"
									bind:value={locationInput}
									placeholder="Location not set"
								/>
								<!-- Edit Button -->
								<button
									type="button"
									onclick={() => (isEditingLocation = !isEditingLocation)}
									class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
									title={isEditingLocation ? 'Lock location' : 'Edit location manually'}
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										{#if isEditingLocation}
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M5 13l4 4L19 7"
											/>
										{:else}
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
											/>
										{/if}
									</svg>
								</button>
							</div>
							<button
								type="button"
								onclick={handleLocateMe}
								disabled={isLocating}
								class="flex items-center gap-2 whitespace-nowrap rounded-lg bg-red-100 px-4 py-2 font-medium text-red-700 transition-colors hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50"
							>
								{#if isLocating}
									<svg
										class="h-4 w-4 animate-spin"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
									>
										<circle
											class="opacity-25"
											cx="12"
											cy="12"
											r="10"
											stroke="currentColor"
											stroke-width="4"
										></circle>
										<path
											class="opacity-75"
											fill="currentColor"
											d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
										></path>
									</svg>
								{:else}
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
										/>
									</svg>
								{/if}
								{isLocating ? 'Locating...' : 'Locate Me'}
							</button>
						</div>
						<p class="mt-1 text-xs text-gray-500">
							Click "Locate Me" to automatically set your exact location.
						</p>
					</div>
					<button
						class="w-full rounded-lg bg-red-600 px-6 py-3 font-semibold text-white shadow-md transition-colors hover:bg-red-700 hover:shadow-lg"
						onclick={handleSaveProfile}
					>
						Save Changes
					</button>
					{#if profileMsg}
						<div
							class="rounded-lg p-3 {profileMsg.includes('successfully')
								? 'bg-green-50 text-green-700'
								: 'bg-red-50 text-red-700'}"
						>
							<p class="text-sm font-medium">{profileMsg}</p>
						</div>
					{/if}
				</div>
			</div>

			<!-- Change Password Section -->
			<div
				class="rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
			>
				<div class="mb-6 flex items-center">
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
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							></path>
						</svg>
					</div>
					<h2 class="text-xl font-bold text-gray-900">Change Password</h2>
				</div>
				<div class="space-y-4">
					<div>
						<input
							type="password"
							placeholder="Old password"
							class="w-full rounded-lg border border-gray-300 px-4 py-3 transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
							bind:value={oldPassword}
						/>
					</div>
					<div>
						<input
							type="password"
							placeholder="New password"
							class="w-full rounded-lg border border-gray-300 px-4 py-3 transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
							bind:value={newPassword}
						/>
					</div>
					<div>
						<input
							type="password"
							placeholder="Confirm new password"
							class="w-full rounded-lg border border-gray-300 px-4 py-3 transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
							bind:value={confirmPassword}
						/>
					</div>
					<button
						class="w-full rounded-lg bg-gray-800 px-6 py-3 font-semibold text-white shadow-md transition-colors hover:bg-gray-900 hover:shadow-lg"
						onclick={handleChangePassword}
					>
						Update Password
					</button>
					{#if pwdMsg}
						<div
							class="rounded-lg p-3 {pwdMsg.includes('successfully')
								? 'bg-green-50 text-green-700'
								: 'bg-red-50 text-red-700'}"
						>
							<p class="text-sm font-medium">{pwdMsg}</p>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Ratings Section -->
		<div
			class="rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition-shadow hover:shadow-xl"
		>
			<div class="mb-6 flex items-center">
				<div class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-100">
					<svg class="h-6 w-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
						></path>
					</svg>
				</div>
				<h2 class="text-xl font-bold text-gray-900">My Ratings & Reviews</h2>
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
					<p class="text-gray-500">No ratings yet. Complete some trades to get rated!</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each ratings as rating (rating.id)}
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
									{#each [1, 2, 3, 4, 5] as star (star)}
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
						</div>
					{/each}
				</div>

				<!-- Average Rating -->
				{#if ratings.length > 0}
					<div class="mt-8 border-t-2 border-gray-200 pt-6">
						<div class="grid grid-cols-2 gap-6">
							<div
								class="rounded-xl border border-yellow-200 bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 text-center"
							>
								<p class="mb-2 text-sm font-medium text-gray-600">Average Rating</p>
								<div class="mb-2 flex items-center justify-center space-x-2">
									<p class="text-4xl font-bold text-gray-900">
										{(ratings.reduce((sum, r) => sum + r.score, 0) / ratings.length).toFixed(1)}
									</p>
									<svg class="h-8 w-8 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
										<path
											d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
										></path>
									</svg>
								</div>
								<p class="text-xs text-gray-500">out of 5.0</p>
							</div>
							<div
								class="rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 text-center"
							>
								<p class="mb-2 text-sm font-medium text-gray-600">Total Ratings</p>
								<p class="mb-2 text-4xl font-bold text-gray-900">{ratings.length}</p>
								<p class="text-xs text-gray-500">reviews received</p>
							</div>
						</div>
					</div>
				{/if}
			{/if}
		</div>
	{:else}
		<p class="text-gray-600">Please sign in to view your profile.</p>
	{/if}
</div>
