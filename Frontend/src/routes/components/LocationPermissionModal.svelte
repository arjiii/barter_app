<script lang="ts">
	import { onMount } from 'svelte';

	interface LocationData {
		city: string;
		radius: number;
		lat: number;
		lng: number;
	}

	interface Props {
		isOpen: boolean;
		onComplete: (location: LocationData) => void;
		onSkip: () => void;
	}

	let { isOpen, onComplete, onSkip }: Props = $props();

	let searchInput = $state('');
	let selectedCity = $state('Olongapo');
	let selectedRadius = $state(20);
	let mapCenter = $state({ lat: 14.8294, lng: 120.2828 }); //  Olongapo coordinates
	let map: any = $state(null);
	let marker: any = $state(null);
	let circle: any = $state(null);

	const radiusOptions = [5, 10, 20, 50, 100];

	onMount(() => {
		if (isOpen && typeof window !== 'undefined') {
			setTimeout(initializeMap, 100);
		}
	});

	$effect(() => {
		if (isOpen && typeof window !== 'undefined' && !map) {
			setTimeout(initializeMap, 100);
		}
	});

	// Note: For now, skip map loading - you'll need a Google Maps API key
	async function initializeMap() {
		// Simplified: don't load maps for now unless you have API key
		console.log('Map initialization skipped - needs Google Maps API key');
	}

	function handleRadiusChange(radius: number) {
		selectedRadius = radius;
	}

	function handleSearch() {
		selectedCity = searchInput || 'Olongapo';
	}

	function detectMyLocation() {
		if ('geolocation' in navigator) {
			navigator.geolocation.getCurrentPosition(
				(position) => {
					mapCenter = {
						lat: position.coords.latitude,
						lng: position.coords.longitude
					};
					selectedCity = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
					searchInput = selectedCity;
				},
				(error) => {
					console.error('Geolocation error:', error);
					alert('Could not detect your location. Please search manually.');
				}
			);
		}
	}

	function handleApply() {
		onComplete({
			city: selectedCity,
			radius: selectedRadius,
			lat: mapCenter.lat,
			lng: mapCenter.lng
		});
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
		<div class="relative w-full max-w-lg overflow-hidden rounded-2xl bg-[#1a1a1a] shadow-2xl">
			<!-- Header -->
			<div class="border-b border-gray-700 bg-[#222] px-6 py-4">
				<div class="flex items-center justify-between">
					<h2 class="text-xl font-semibold text-white">Change location</h2>
					<button
						onclick={onSkip}
						aria-label="Close"
						class="rounded-full p-1 text-gray-400 transition-colors hover:bg-gray-700 hover:text-white"
					>
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Content -->
			<div class="p-6">
				<!-- Search Box -->
				<div class="mb-4">
					<p class="mb-2 text-sm text-gray-400">Search by city, neighborhood or ZIP code</p>
					<div class="relative flex gap-2">
						<div class="relative flex-1">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
							</span>
							<input
								type="text"
								bind:value={searchInput}
								onkeydown={(e) => e.key === 'Enter' && handleSearch()}
								placeholder="Location"
								class="w-full rounded-lg border border-gray-600 bg-[#2a2a2a] py-2.5 pl-10 pr-4 text-white placeholder-gray-500 transition-colors focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
							/>
						</div>
						<button
							onclick={detectMyLocation}
							title="Use my location"
							aria-label="Use my current location"
							class="rounded-lg border border-gray-600 bg-[#2a2a2a] p-2.5 text-gray-300 transition-colors hover:bg-gray-700"
						>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
								/>
							</svg>
						</button>
					</div>
				</div>

				<!-- Radius Selector -->
				<div class="mb-4">
					<p class="mb-2 text-sm text-gray-400">Radius</p>
					<div class="flex items-center gap-2">
						{#each radiusOptions as radius}
							<button
								onclick={() => handleRadiusChange(radius)}
								class="flex-1 rounded-lg border py-2 text-sm font-medium transition-all {selectedRadius ===
								radius
									? 'border-blue-500 bg-blue-500/20 text-blue-400'
									: 'border-gray-600 bg-[#2a2a2a] text-gray-300 hover:border-gray-500'}"
							>
								{radius} km
							</button>
						{/each}
						<button
							aria-label="More radius options"
							class="rounded-lg border border-gray-600 bg-[#2a2a2a] p-2 text-gray-300 hover:border-gray-500"
						>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 9l-7 7-7-7"
								/>
							</svg>
						</button>
					</div>
				</div>

				<!-- Map Placeholder -->
				<div class="relative mb-4 overflow-hidden rounded-lg">
					<div class="h-64 w-full bg-gradient-to-br from-[#1a3a52] via-[#0a4d68] to-[#1a3a52]">
						<div class="flex h-full items-center justify-center">
							<div class="text-center">
								<svg
									class="mx-auto h-12 w-12 animate-pulse text-blue-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
									/>
								</svg>
								<p class="mt-2 text-sm text-gray-400">
									{selectedCity} - {selectedRadius}km radius
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Apply Button -->
				<button
					onclick={handleApply}
					class="w-full rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#1a1a1a]"
				>
					Apply
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Custom scrollbar for dark theme */
	:global(body) {
		scrollbar-width: thin;
		scrollbar-color: #4a5568 #1a1a1a;
	}

	:global(body::-webkit-scrollbar) {
		width: 8px;
	}

	:global(body::-webkit-scrollbar-track) {
		background: #1a1a1a;
	}

	:global(body::-webkit-scrollbar-thumb) {
		background-color: #4a5568;
		border-radius: 4px;
	}
</style>
