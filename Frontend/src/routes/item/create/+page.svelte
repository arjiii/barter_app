<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { itemService } from '$lib/services/itemService';
	import type { CreateItemData, Category } from '$lib/types/items';

	let currentStep = $state(0);
	const steps = ['Basic Info', 'Details & Specs', 'Location & Media', 'Review'];

	let isLoading = $state(false);
	let error: string | null = $state(null);
	let categories: Category[] = $state([]);

	let formData = $state({
		title: '',
		description: '',
		category: '',
		condition: '',
		images: [] as string[],
		specs: [] as { key: string; value: string }[],
		location: '',
		latitude: null as number | null,
		longitude: null as number | null
	});

	let otherCategory = $state('');
	let selectedImages: File[] = $state([]);
	let imagePreviewUrls: string[] = $state([]);

	const conditions = [
		{ value: 'new', label: 'New (Never Used)' },
		{ value: 'like_new', label: 'Like New' },
		{ value: 'excellent', label: 'Excellent' },
		{ value: 'good', label: 'Good' },
		{ value: 'fair', label: 'Fair' },
		{ value: 'poor', label: 'Poor (For Parts)' }
	];

	// Fallback categories if API fails or is empty
	const fallbackCategories = [
		{ id: 'electronics', name: 'Electronics' },
		{ id: 'furniture', name: 'Furniture' },
		{ id: 'clothing', name: 'Clothing & Accessories' },
		{ id: 'books', name: 'Books & Media' },
		{ id: 'home', name: 'Home & Garden' },
		{ id: 'sports', name: 'Sports & Outdoors' },
		{ id: 'toys', name: 'Toys & Hobbies' },
		{ id: 'vehicles', name: 'Vehicles' },
		{ id: 'tools', name: 'Tools & Equipment' },
		{ id: 'art', name: 'Art & Collectibles' },
		{ id: 'services', name: 'Services' }
	];

	onMount(async () => {
		await authStore.initializeAuth();
		if (!authStore.get().isAuthenticated) {
			goto('/sign-in-up');
			return;
		}
		try {
			const fetchedCategories = await itemService.getCategories();
			if (fetchedCategories && fetchedCategories.length > 0) {
				categories = fetchedCategories;
			} else {
				categories = fallbackCategories as Category[];
			}
		} catch (err) {
			console.error('Failed to load categories:', err);
			categories = fallbackCategories as Category[];
		}
	});

	function handleImageSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const files = Array.from(target.files || []);
		if (files.length > 0) {
			selectedImages = [...selectedImages, ...files].slice(0, 5);
			updateImagePreviews();
		}
	}

	function updateImagePreviews() {
		imagePreviewUrls.forEach((url) => URL.revokeObjectURL(url));
		imagePreviewUrls = selectedImages.map((file) => URL.createObjectURL(file));
	}

	function removeImage(index: number) {
		selectedImages = selectedImages.filter((_, i) => i !== index);
		updateImagePreviews();
	}

	function addSpec() {
		formData.specs = [...formData.specs, { key: '', value: '' }];
	}

	function removeSpec(index: number) {
		formData.specs = formData.specs.filter((_, i) => i !== index);
	}

	async function detectLocation() {
		if (!('geolocation' in navigator)) {
			alert('Geolocation is not supported by your browser.');
			return;
		}

		try {
			// Check permissions first if available
			if (navigator.permissions && navigator.permissions.query) {
				const result = await navigator.permissions.query({ name: 'geolocation' });
				if (result.state === 'denied') {
					alert('Location access is denied. Please enable permissions in your browser settings.');
					return;
				}
			}

			navigator.geolocation.getCurrentPosition(
				(position) => {
					formData.latitude = position.coords.latitude;
					formData.longitude = position.coords.longitude;
					formData.location = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
				},
				(err) => {
					console.error('Geolocation error:', err);
					let msg = 'Could not detect location.';
					if (err.code === 1) msg = 'Location access denied. Please enable permissions.';
					else if (err.code === 2) msg = 'Location unavailable. Please try again.';
					else if (err.code === 3) msg = 'Location request timed out.';
					alert(msg);
				},
				{
					enableHighAccuracy: true,
					timeout: 15000,
					maximumAge: 0
				}
			);
		} catch (e) {
			console.error('Error checking permissions:', e);
			// Fallback to direct call if permission check fails
			navigator.geolocation.getCurrentPosition(
				(position) => {
					formData.latitude = position.coords.latitude;
					formData.longitude = position.coords.longitude;
					formData.location = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
				},
				(err) => {
					console.error('Geolocation error:', err);
					alert('Could not detect location.');
				}
			);
		}
	}

	function nextStep() {
		if (currentStep === 0) {
			if (!formData.title || !formData.category) {
				alert('Please fill in all required fields');
				return;
			}
		} else if (currentStep === 1) {
			if (!formData.description || !formData.condition) {
				alert('Please fill in all required fields');
				return;
			}
		}
		currentStep++;
	}

	function prevStep() {
		currentStep--;
	}

	async function handleSubmit() {
		isLoading = true;
		try {
			const user = authStore.get().user;
			if (!user) throw new Error('User not authenticated');

			const imageUrls = await Promise.all(
				selectedImages.map(async (file) => {
					return new Promise<string>((resolve) => {
						const reader = new FileReader();
						reader.onload = () => resolve(reader.result as string);
						reader.readAsDataURL(file);
					});
				})
			);

			// Convert specs array to object
			const specsObject = formData.specs.reduce(
				(acc, spec) => {
					if (spec.key.trim() && spec.value.trim()) {
						acc[spec.key.trim()] = spec.value.trim();
					}
					return acc;
				},
				{} as Record<string, string>
			);

			const itemData: CreateItemData = {
				title: formData.title,
				description: formData.description,
				category: formData.category === 'others' ? otherCategory || 'Others' : formData.category,
				condition: formData.condition,
				images: imageUrls,
				specs: specsObject,
				location: formData.location,
				latitude: formData.latitude ?? undefined,
				longitude: formData.longitude ?? undefined
			};

			await itemService.createItem(user.id, itemData);
			goto('/my-items');
		} catch (err: any) {
			error = err.message || 'Failed to create item';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen bg-[#f7f5f3] px-4 py-12 font-['Inter',sans-serif] sm:px-6 lg:px-8">
	<div class="mx-auto max-w-4xl">
		<!-- Stepper Header -->
		<div class="mb-8">
			<div class="relative flex items-center justify-between">
				<div
					class="absolute left-0 top-1/2 -z-10 h-1 w-full -translate-y-1/2 transform bg-gray-200"
				></div>
				{#each steps as step, i}
					<div class="flex flex-col items-center bg-[#f7f5f3] px-2">
						<div
							class={`mb-2 flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-colors duration-300 ${i <= currentStep ? 'bg-[#ff6d3f] text-white' : 'bg-gray-200 text-gray-500'}`}
						>
							{i + 1}
						</div>
						<span
							class={`text-xs font-medium transition-colors duration-300 ${i <= currentStep ? 'text-[#ff6d3f]' : 'text-gray-500'}`}
							>{step}</span
						>
					</div>
				{/each}
			</div>
		</div>

		<div class="rounded-2xl bg-white p-8 shadow-xl transition-all duration-300">
			<h2 class="mb-6 text-2xl font-bold text-[#1f1b17]">{steps[currentStep]}</h2>

			{#if currentStep === 0}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Item Title *</label>
						<input
							type="text"
							bind:value={formData.title}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
							placeholder="What are you trading? (e.g., iPhone 13 Pro, Vintage Bike)"
						/>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Category *</label>
						<select
							bind:value={formData.category}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
						>
							<option value="">Select category...</option>
							{#each categories as category}
								<option value={category.id}>{category.name}</option>
							{/each}
							<option value="others">Others</option>
						</select>
						{#if formData.category === 'others'}
							<input
								type="text"
								bind:value={otherCategory}
								class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
								placeholder="Specify category"
							/>
						{/if}
					</div>
				</div>
			{:else if currentStep === 1}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Condition *</label>
						<select
							bind:value={formData.condition}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
						>
							<option value="">Select condition...</option>
							{#each conditions as c}
								<option value={c.value}>{c.label}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Description *</label>
						<textarea
							bind:value={formData.description}
							rows="6"
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
							placeholder="Describe your item in detail. Include age, usage history, and any defects..."
						></textarea>
					</div>

					<!-- Product Specs Section -->
					<div>
						<div class="mb-2 flex items-center justify-between">
							<label class="block text-sm font-medium text-gray-700">Product Specifications</label>
							<button
								type="button"
								onclick={addSpec}
								class="text-sm font-medium text-[#ff6d3f] hover:text-[#e65a2f]"
							>
								+ Add Spec
							</button>
						</div>
						<div class="space-y-3">
							{#each formData.specs as spec, i}
								<div class="flex gap-3">
									<input
										type="text"
										bind:value={spec.key}
										placeholder="Feature (e.g., Color)"
										class="flex-1 rounded-xl border border-gray-300 px-4 py-2 text-sm focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
									/>
									<input
										type="text"
										bind:value={spec.value}
										placeholder="Value (e.g., Blue)"
										class="flex-1 rounded-xl border border-gray-300 px-4 py-2 text-sm focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
									/>
									<button
										type="button"
										onclick={() => removeSpec(i)}
										class="text-gray-400 hover:text-red-500"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
											/>
										</svg>
									</button>
								</div>
							{/each}
							{#if formData.specs.length === 0}
								<p class="text-xs italic text-gray-500">
									Add specifications like Brand, Model, Size, etc.
								</p>
							{/if}
						</div>
					</div>
				</div>
			{:else if currentStep === 2}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Location</label>
						<div class="flex gap-2">
							<input
								type="text"
								bind:value={formData.location}
								class="flex-1 rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
								placeholder="City, Province"
							/>
							<button
								type="button"
								onclick={detectLocation}
								class="rounded-xl bg-gray-100 px-4 py-3 text-gray-700 hover:bg-gray-200"
							>
								📍 Detect
							</button>
						</div>
						{#if formData.latitude && formData.longitude}
							<p class="mt-1 text-xs text-green-600">
								✓ Coordinates captured: {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(
									4
								)}
							</p>
						{/if}
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Photos (Max 5)</label>
						<div
							class="relative cursor-pointer rounded-xl border-2 border-dashed border-gray-300 p-8 text-center transition-colors hover:border-[#ff6d3f]"
						>
							<input
								type="file"
								accept="image/*"
								multiple
								onchange={handleImageSelect}
								class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
							/>
							<div class="text-gray-500">
								<span class="font-medium text-[#ff6d3f]">Upload files</span> or drag and drop
							</div>
							<p class="mt-1 text-xs text-gray-400">PNG, JPG up to 5MB</p>
						</div>
						{#if imagePreviewUrls.length > 0}
							<div class="mt-4 grid grid-cols-3 gap-4">
								{#each imagePreviewUrls as url, i}
									<div class="group relative">
										<img
											src={url}
											alt="Preview"
											class="h-24 w-full rounded-lg object-cover shadow-sm"
										/>
										<button
											onclick={() => removeImage(i)}
											class="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-white opacity-0 shadow-md transition-opacity group-hover:opacity-100"
											>×</button
										>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{:else if currentStep === 3}
				<div class="space-y-6">
					<div class="rounded-xl border border-gray-100 bg-gray-50 p-6">
						<div class="flex items-start justify-between">
							<div>
								<h3 class="text-xl font-bold text-gray-900">{formData.title}</h3>
								<div class="mt-1 flex items-center space-x-2 text-sm text-gray-500">
									<span class="font-medium text-[#ff6d3f]"
										>{formData.category === 'others'
											? otherCategory
											: categories.find((c) => c.id === formData.category)?.name ||
												formData.category}</span
									>
									<span>•</span>
									<span
										>{conditions.find((c) => c.value === formData.condition)?.label ||
											formData.condition}</span
									>
								</div>
							</div>
						</div>

						<div class="mt-4 border-t border-gray-200 pt-4">
							<h4 class="text-sm font-medium text-gray-900">Description</h4>
							<p class="mt-2 whitespace-pre-line text-sm text-gray-600">{formData.description}</p>
						</div>

						{#if formData.specs.length > 0}
							<div class="mt-4 border-t border-gray-200 pt-4">
								<h4 class="mb-2 text-sm font-medium text-gray-900">Specifications</h4>
								<dl class="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
									{#each formData.specs as spec}
										{#if spec.key && spec.value}
											<div class="flex justify-between sm:block">
												<dt class="text-xs font-medium text-gray-500">{spec.key}</dt>
												<dd class="text-sm text-gray-900">{spec.value}</dd>
											</div>
										{/if}
									{/each}
								</dl>
							</div>
						{/if}

						<div class="mt-4 border-t border-gray-200 pt-4">
							<h4 class="text-sm font-medium text-gray-900">Location</h4>
							<p class="mt-1 flex items-center text-sm text-gray-600">
								<svg
									class="mr-1.5 h-4 w-4 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
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
								{formData.location || 'No location specified'}
							</p>
						</div>
					</div>

					<div>
						<h4 class="mb-3 text-sm font-medium text-gray-900">
							Photos ({imagePreviewUrls.length})
						</h4>
						<div class="grid grid-cols-3 gap-3 sm:grid-cols-4">
							{#each imagePreviewUrls as url}
								<div class="aspect-square overflow-hidden rounded-lg bg-gray-100">
									<img src={url} alt="Preview" class="h-full w-full object-cover" />
								</div>
							{/each}
							{#if imagePreviewUrls.length === 0}
								<div
									class="col-span-3 rounded-lg bg-gray-50 py-4 text-center text-sm italic text-gray-500"
								>
									No photos uploaded
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/if}

			{#if error}
				<div class="mt-4 rounded-lg bg-red-100 p-3 text-red-700">{error}</div>
			{/if}

			<div class="mt-8 flex justify-between border-t border-gray-100 pt-6">
				<button
					type="button"
					onclick={prevStep}
					disabled={currentStep === 0}
					class="rounded-xl border border-gray-300 px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
				>
					Back
				</button>

				{#if currentStep < steps.length - 1}
					<button
						type="button"
						onclick={nextStep}
						class="rounded-xl bg-[#1f1b17] px-6 py-3 font-medium text-white shadow-lg shadow-gray-200 transition-colors hover:bg-black"
					>
						Next Step
					</button>
				{:else}
					<button
						type="button"
						onclick={handleSubmit}
						disabled={isLoading}
						class="rounded-xl bg-[#ff6d3f] px-8 py-3 font-medium text-white shadow-lg shadow-orange-200 transition-colors hover:bg-[#e65a2f] disabled:opacity-50"
					>
						{isLoading ? 'Posting...' : 'Post Item'}
					</button>
				{/if}
			</div>
		</div>
	</div>
</div>
